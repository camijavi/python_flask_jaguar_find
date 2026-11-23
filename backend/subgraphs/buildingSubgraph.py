"""
buildingSubgraph.py
================================================================================
CHILD GRAPH / SUBGRAPH ARCHITECTURE FOR INDOOR CAMPUS NAVIGATION
================================================================================
Encapsulates an indoor, multi-floor directed graph for an individual building
(e.g. Building P - Copérnico). Provides room-to-room Dijkstra shortest-path
routing, accessibility filtering, floor-specific node queries, and
vertical floor transitions (stairs, elevators, ramps).
================================================================================
"""

import math
from typing import Dict, List, Optional, Tuple, Any

from backend.graph.directedGraph import DirectedGraph, Node, DirectedEdge
from backend.graph.dijkstraRouter import DijkstraRouter
from backend.graph.geoUtils import CampusGeoUtils


class BuildingSubgraph:
    """
    Child graph representing the detailed indoor layout of a single campus building.
    Supports multi-floor nodes, horizontal corridors, and vertical connections (stairs/ramps).
    """

    def __init__(
        self,
        buildingId: str,
        name: str,
        code: str,
        floors: List[int],
        macroNodeId: str,
        entranceNodeIds: Optional[List[str]] = None,
        description: str = ""
    ):
        self.buildingId = buildingId
        self.name = name
        self.code = code
        self.floors = sorted(floors)
        self.macroNodeId = macroNodeId
        self.entranceNodeIds = entranceNodeIds or []
        self.description = description
        self.graph = DirectedGraph()
        self.router = DijkstraRouter(self.graph)
        self.roomAliases: Dict[str, str] = {}

    def registerRoomAlias(self, alias: str, targetNodeId: str) -> None:
        """Maps an alternative room query, code, or alias to a target node ID."""
        self.roomAliases[alias] = targetNodeId

    def addNode(self, node: Node) -> None:
        """Adds an internal room, stairwell, restroom, or POI node."""
        self.graph.addNode(node)

    def addBidirectionalCorridor(
        self,
        nodeAId: str,
        nodeBId: str,
        distanceMeters: float,
        isAccessible: bool = True,
        forwardInstruction: str = "",
        backwardInstruction: str = "",
        forwardEdgeKey: Optional[str] = None,
        backwardEdgeKey: Optional[str] = None
    ) -> None:
        """Adds a bidirectional horizontal walkway along a building hallway/corridor."""
        self.graph.addBidirectionalWalkway(
            nodeAId,
            nodeBId,
            distanceMeters,
            isAccessible=isAccessible,
            forwardInstruction=forwardInstruction,
            backwardInstruction=backwardInstruction,
            forwardEdgeKey=forwardEdgeKey,
            backwardEdgeKey=backwardEdgeKey
        )

    # Alias for compatibility with subgraphs calling addBidirectionalWalkway
    addBidirectionalWalkway = addBidirectionalCorridor

    def addVerticalConnection(
        self,
        lowerNodeId: str,
        upperNodeId: str,
        distanceMeters: float = 12.0,
        isAccessible: bool = False,
        upInstruction: str = "Sube al siguiente piso por las escaleras.",
        downInstruction: str = "Baja al piso inferior por las escaleras."
    ) -> None:
        """
        Adds vertical transition between floors (stairs, ramps, or elevators).
        """
        self.graph.addDirectedEdge(lowerNodeId, upperNodeId, distanceMeters, isAccessible=isAccessible, stepInstruction=upInstruction)
        self.graph.addDirectedEdge(upperNodeId, lowerNodeId, distanceMeters, isAccessible=isAccessible, stepInstruction=downInstruction)

    def getNode(self, nodeId: str) -> Optional[Node]:
        return self.graph.getNode(nodeId)

    def getAllNodes(self) -> List[Node]:
        return self.graph.getAllNodes()

    def getNodesByFloor(self, floorLevel: int) -> List[Node]:
        """Returns all rooms, stairs, and facilities on a given floor level."""
        return [n for n in self.graph.getAllNodes() if getattr(n, "floorLevel", 1) == floorLevel]

    def findNearestIndoorNodeByGps(
        self,
        userLat: float,
        userLng: float,
        floorLevel: Optional[int] = None
    ) -> Tuple[Optional[str], float]:
        """Snaps GPS coordinate to nearest indoor node, optionally constrained to a floor."""
        nearestId = None
        minDistance = float("inf")

        for nodeId, node in self.graph.nodes.items():
            if floorLevel is not None and getattr(node, "floorLevel", 1) != floorLevel:
                continue
            dist = CampusGeoUtils.calculateHaversineDistance(userLat, userLng, node.latitude, node.longitude)
            if dist < minDistance:
                minDistance = dist
                nearestId = nodeId

        return nearestId, round(minDistance, 1)

    def resolveRoomQuery(self, query: str) -> Optional[str]:
        """Resolves room code or keyword to a node ID within this building."""
        import unicodedata

        def _normalize(s: str) -> str:
            s = "".join(c for c in unicodedata.normalize("NFD", s) if unicodedata.category(c) != "Mn")
            return s.lower().replace(" ", "").replace("-", "").replace("_", "")

        clean = _normalize(query or "")
        if not clean:
            return None

        # 0. Check registered room aliases
        for alias, targetNodeId in self.roomAliases.items():
            if _normalize(alias) == clean:
                return targetNodeId

        # 1. Exact node ID match
        for nid in self.graph.nodes:
            if _normalize(nid) == clean:
                return nid

        # 2. Check room number or name match
        for nid, node in self.graph.nodes.items():
            nameNorm = _normalize(node.name)
            if clean in nameNorm or nameNorm in clean:
                return nid

        return None

    def calculateIndoorRoute(
        self,
        originQuery: str,
        destinationQuery: str,
        accessibleOnly: bool = False,
        lang: str = "spa"
    ) -> dict:
        """
        Calculates turn-by-turn indoor route between two locations inside this building.
        """
        originId = self.resolveRoomQuery(originQuery) or originQuery
        destId = self.resolveRoomQuery(destinationQuery) or destinationQuery

        if originId not in self.graph.nodes:
            return {
                "success": False,
                "error": f"Ubicación de origen '{originQuery}' no encontrada en {self.name}." if lang == "spa"
                         else f"Origin location '{originQuery}' not found in {self.name}."
            }

        if destId not in self.graph.nodes:
            return {
                "success": False,
                "error": f"Destino '{destinationQuery}' no encontrado en {self.name}." if lang == "spa"
                         else f"Destination '{destinationQuery}' not found in {self.name}."
            }

        path, dist, mins, _ = self.router.findShortestPathWithEdges(
            originId, destId, accessibleOnly=accessibleOnly
        )

        if not path:
            return {
                "success": False,
                "error": "No se encontró una ruta transitable dentro del edificio con las restricciones dadas." if lang == "spa"
                         else "No walkable indoor route found with requested accessibility restrictions."
            }

        from backend.graph.humanInstructions import buildHumanIndoorSteps, formatHumanWalkingTime
        humanSteps = buildHumanIndoorSteps(self, path, lang=lang, mode="standalone")
        instructions = [s["instruction"] for s in humanSteps]

        originNode = self.graph.nodes[originId]
        destNode = self.graph.nodes[destId]

        pathDetails = [
            {
                "nodeId": nid,
                "name": self.graph.nodes[nid].getName(lang),
                "category": self.graph.nodes[nid].category,
                "floorLevel": self.graph.nodes[nid].floorLevel,
                "lat": self.graph.nodes[nid].latitude,
                "lng": self.graph.nodes[nid].longitude,
            }
            for nid in path
        ]

        floorsCrossed = sorted(list({self.graph.nodes[nid].floorLevel for nid in path}))

        return {
            "success": True,
            "buildingId": self.buildingId,
            "buildingName": self.name,
            "origin": {
                "nodeId": originId,
                "name": originNode.getName(lang),
                "floorLevel": originNode.floorLevel
            },
            "destination": {
                "nodeId": destId,
                "name": destNode.getName(lang),
                "floorLevel": destNode.floorLevel
            },
            "pathNodeIds": path,
            "pathDetails": pathDetails,
            "floorsCrossed": floorsCrossed,
            "totalDistanceMeters": dist,
            "estimatedWalkingMinutes": mins,
            "humanDuration": formatHumanWalkingTime(dist, lang=lang),
            "steps": humanSteps,
            "stepInstructions": instructions,
            "isAccessibleRoute": accessibleOnly
        }

    def toDict(self, lang: str = "spa") -> dict:
        """Serializes the building subgraph metadata, floors, nodes, and connections."""
        nodesList = []
        for nid, node in self.graph.nodes.items():
            edges = [
                {
                    "targetNodeId": edge.targetNodeId,
                    "distanceMeters": edge.distanceMeters,
                    "isAccessible": edge.isAccessible,
                    "stepInstruction": edge.getInstruction(lang),
                }
                for edge in getattr(node, "outgoingEdges", [])
            ]
            nd = node.toDict(lang)
            nd["adjacentEdges"] = edges
            nodesList.append(nd)

        return {
            "buildingId": self.buildingId,
            "name": self.name,
            "code": self.code,
            "floors": self.floors,
            "macroNodeId": self.macroNodeId,
            "entranceNodeIds": self.entranceNodeIds,
            "description": self.description,
            "nodesCount": len(nodesList),
            "nodes": nodesList,
        }
