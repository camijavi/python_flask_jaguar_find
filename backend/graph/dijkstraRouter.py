"""
dijkstraRouter.py
Dijkstra shortest path algorithm with min-heap priority queue (heapq),
accessibility filtering, turn-by-turn step generation, and full internationalization (i18n).
Operates seamlessly on any `graphCombined.Graph` or its domain subclass `DirectedGraph`.
All internal code and default strings are in English.
"""

import heapq
import math
from typing import Dict, Iterator, List, Optional, Tuple
from .directedGraph import DirectedEdge, DirectedGraph, Graph, Node, Vertex
from .i18n import t


class DijkstraRouter:
    def __init__(self, graph: Graph, averageWalkingSpeedMpm: float = 72.0):
        self.graph = graph
        self.walkingSpeed = averageWalkingSpeedMpm  # 1.2 m/s = 72 meters per minute

    def _getVertex(self, nodeId: str) -> Optional[Vertex]:
        if isinstance(self.graph, DirectedGraph):
            return self.graph.nodes.get(nodeId)
        return self.graph.search(nodeId)

    def _iterOutgoing(
        self,
        vertex: Vertex,
        accessibleOnly: bool,
    ) -> Iterator[Tuple[str, float, Optional[DirectedEdge]]]:
        """
        Yields (targetId, weight, DirectedEdge | None) for each outgoing edge.
        Uses rich `Node.outgoingEdges` when present, or `Vertex.neigh` directly
        on plain `graphCombined.Graph` instances.
        """
        if isinstance(vertex, Node) and vertex.outgoingEdges:
            for edge in vertex.outgoingEdges:
                if accessibleOnly and (
                    not edge.isAccessible or edge.accessibilityZone == "inaccessible"
                ):
                    continue
                yield edge.targetNodeId, edge.distanceMeters, edge
            return

        for neighbor, weight in vertex.neigh:
            yield neighbor.nodeId, float(weight), None

    def findShortestPathWithEdges(
        self,
        sourceNodeId: str,
        targetNodeId: str,
        accessibleOnly: bool = False,
    ) -> Tuple[List[str], float, int, Dict[Tuple[str, str], DirectedEdge]]:
        """
        Calculates optimal route using Dijkstra's Algorithm with a binary min-heap (heapq).
        Complexity: O((V + E) log V) on a weighted, directed, non-complete graph G = (V, E, W).
        Returns: (pathNodeIds, totalDistanceMeters, estimatedMinutes, edgeTraversedMap)
        """
        sourceVertex = self._getVertex(sourceNodeId)
        targetVertex = self._getVertex(targetNodeId)
        if sourceVertex is None or targetVertex is None:
            return [], float("inf"), 0, {}

        srcId = sourceVertex.nodeId
        dstId = targetVertex.nodeId

        shortestCosts: Dict[str, float] = {v.nodeId: float("inf") for v in self.graph.vertices}
        pathDistances: Dict[str, float] = {v.nodeId: float("inf") for v in self.graph.vertices}
        previousNodes: Dict[str, Optional[str]] = {v.nodeId: None for v in self.graph.vertices}
        edgeTraversed: Dict[Tuple[str, str], DirectedEdge] = {}

        shortestCosts[srcId] = 0.0
        pathDistances[srcId] = 0.0
        priorityQueue: List[Tuple[float, str]] = [(0.0, srcId)]

        while priorityQueue:
            currentDistance, currentNodeId = heapq.heappop(priorityQueue)

            if currentDistance > shortestCosts[currentNodeId]:
                continue

            if currentNodeId == dstId:
                break

            currentVertex = self._getVertex(currentNodeId)
            if currentVertex is None:
                continue

            for targetId, weight, edge in self._iterOutgoing(currentVertex, accessibleOnly):
                costFactor = (
                    edge.routingCostFactor
                    if accessibleOnly and edge and edge.accessibilityZone == "recommended"
                    else 1.0
                )
                newCost = currentDistance + weight * costFactor
                if newCost < shortestCosts[targetId]:
                    shortestCosts[targetId] = newCost
                    pathDistances[targetId] = pathDistances[currentNodeId] + weight
                    previousNodes[targetId] = currentNodeId
                    if edge is not None:
                        edgeTraversed[(currentNodeId, targetId)] = edge
                    heapq.heappush(priorityQueue, (newCost, targetId))

        path: List[str] = []
        currId: Optional[str] = dstId
        while currId is not None:
            path.append(currId)
            currId = previousNodes[currId]
        path.reverse()

        if not path or path[0] != srcId:
            return [], float("inf"), 0, {}

        totalDistance = pathDistances[dstId]
        estimatedMinutes = math.ceil(totalDistance / self.walkingSpeed) if totalDistance > 0 else 0
        return path, round(totalDistance, 1), estimatedMinutes, edgeTraversed

    def findShortestPath(
        self,
        sourceNodeId: str,
        targetNodeId: str,
        accessibleOnly: bool = False,
        lang: str = "eng",
    ) -> Tuple[List[str], float, int, List[str]]:
        """
        Calculates optimal route using Dijkstra's Algorithm with a binary min-heap (heapq).
        Complexity: O((V + E) log V).
        Returns: (pathNodeIds, totalDistanceMeters, estimatedMinutes, stepDirections)
        """
        path, totalDistance, estimatedMinutes, edgeTraversed = self.findShortestPathWithEdges(
            sourceNodeId, targetNodeId, accessibleOnly=accessibleOnly
        )
        if not path:
            return [], float("inf"), 0, []

        stepDirections = self._buildStepDirections(path, edgeTraversed, lang=lang)
        return path, totalDistance, estimatedMinutes, stepDirections

    def _vertexDisplayName(self, vertexId: str, lang: str) -> str:
        vertex = self._getVertex(vertexId)
        if isinstance(vertex, Node):
            return vertex.getName(lang)
        return vertex.nodeId if vertex is not None else vertexId

    def _buildStepDirections(
        self,
        path: List[str],
        edgeTraversed: Dict[Tuple[str, str], DirectedEdge],
        lang: str = "eng",
    ) -> List[str]:
        if len(path) < 2:
            return [t("navigation.already_at_destination", lang=lang)]

        directions: List[str] = []
        startNodeName = self._vertexDisplayName(path[0], lang)
        directions.append(
            t("navigation.start_route", lang=lang, startNode=startNodeName)
        )

        for i in range(len(path) - 1):
            u, v = path[i], path[i + 1]
            edge = edgeTraversed.get((u, v))
            instruction = edge.getInstruction(lang) if edge else ""
            if instruction:
                directions.append(instruction)
            else:
                targetName = self._vertexDisplayName(v, lang)
                directions.append(
                    t("navigation.walk_towards", lang=lang, targetNode=targetName)
                )

        destName = self._vertexDisplayName(path[-1], lang)
        directions.append(
            t("navigation.arrived_at_destination", lang=lang, destNode=destName)
        )
        destVertex = self._getVertex(path[-1])
        accessNotice = destVertex.getAccessNotice(lang) if isinstance(destVertex, Node) else None
        if accessNotice:
            directions.append(
                t("navigation.access_notice", lang=lang, notice=accessNotice)
            )

        return directions
