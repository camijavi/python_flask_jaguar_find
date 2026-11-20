"""
dijkstraRouter.py
Dijkstra shortest path algorithm with min-heap priority queue (heapq),
accessibility filtering, turn-by-turn step generation, and full internationalization (i18n).
All internal code and default strings are in English.
"""

import heapq
import math
from typing import Dict, List, Tuple, Optional
from .directedGraph import DirectedGraph, DirectedEdge
from .i18n import t


class DijkstraRouter:
    def __init__(self, graph: DirectedGraph, averageWalkingSpeedMpm: float = 72.0):
        self.graph = graph
        self.walkingSpeed = averageWalkingSpeedMpm  # 1.2 m/s = 72 meters per minute

    def findShortestPath(
        self,
        sourceNodeId: str,
        targetNodeId: str,
        accessibleOnly: bool = False,
        lang: str = "eng"
    ) -> Tuple[List[str], float, int, List[str]]:
        """
        Calculates optimal route using Dijkstra's Algorithm with a binary min-heap (heapq).
        Complexity: O((V + E) log V).
        Returns: (pathNodeIds, totalDistanceMeters, estimatedMinutes, stepDirections)
        """
        if sourceNodeId not in self.graph.nodes or targetNodeId not in self.graph.nodes:
            return [], float("inf"), 0, []

        shortestDistances: Dict[str, float] = {nodeId: float("inf") for nodeId in self.graph.nodes}
        previousNodes: Dict[str, Optional[str]] = {nodeId: None for nodeId in self.graph.nodes}
        edgeTraversed: Dict[Tuple[str, str], DirectedEdge] = {}

        shortestDistances[sourceNodeId] = 0.0
        priorityQueue = [(0.0, sourceNodeId)]

        while priorityQueue:
            currentDistance, currentNodeId = heapq.heappop(priorityQueue)

            if currentDistance > shortestDistances[currentNodeId]:
                continue

            if currentNodeId == targetNodeId:
                break

            currentNode = self.graph.nodes[currentNodeId]
            for edge in currentNode.outgoingEdges:
                if accessibleOnly and not edge.isAccessible:
                    continue

                newDistance = currentDistance + edge.distanceMeters
                targetId = edge.targetNodeId

                if newDistance < shortestDistances[targetId]:
                    shortestDistances[targetId] = newDistance
                    previousNodes[targetId] = currentNodeId
                    edgeTraversed[(currentNodeId, targetId)] = edge
                    heapq.heappush(priorityQueue, (newDistance, targetId))

        # Reconstruct path from target to source
        path: List[str] = []
        currId = targetNodeId
        while currId is not None:
            path.insert(0, currId)
            currId = previousNodes[currId]

        if not path or path[0] != sourceNodeId:
            return [], float("inf"), 0, []

        totalDistance = shortestDistances[targetNodeId]
        estimatedMinutes = math.ceil(totalDistance / self.walkingSpeed)
        stepDirections = self._buildStepDirections(path, edgeTraversed, lang=lang)

        return path, round(totalDistance, 1), estimatedMinutes, stepDirections

    def _buildStepDirections(
        self,
        path: List[str],
        edgeTraversed: Dict[Tuple[str, str], DirectedEdge],
        lang: str = "eng"
    ) -> List[str]:
        if len(path) < 2:
            return [t("navigation.already_at_destination", lang=lang, default="You are already at your destination.")]

        directions: List[str] = []
        startNode = self.graph.nodes[path[0]]
        startNodeName = startNode.getName(lang)
        directions.append(
            t("navigation.start_route", lang=lang, default=f"Start your route at {startNodeName}.", startNode=startNodeName)
        )

        for i in range(len(path) - 1):
            u, v = path[i], path[i + 1]
            edge = edgeTraversed.get((u, v))
            instruction = edge.getInstruction(lang) if edge else ""
            if instruction:
                directions.append(instruction)
            else:
                targetName = self.graph.nodes[v].getName(lang)
                directions.append(
                    t("navigation.walk_towards", lang=lang, default=f"Walk towards {targetName}.", targetNode=targetName)
                )

        destNode = self.graph.nodes[path[-1]]
        destName = destNode.getName(lang)
        directions.append(
            t("navigation.arrived_at_destination", lang=lang, default=f"You have arrived at your destination: {destName}.", destNode=destName)
        )
        accessNotice = destNode.getAccessNotice(lang)
        if accessNotice:
            directions.append(
                t("navigation.access_notice", lang=lang, default=f"Access notice: {accessNotice}", notice=accessNotice)
            )

        return directions
