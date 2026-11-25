"""
buildingSubgraph.py
================================================================================
CHILD GRAPH / SUBGRAPH ARCHITECTURE FOR INDOOR CAMPUS NAVIGATION
================================================================================
Encapsulates an indoor, multi-floor directed, non-complete, weighted graph for
an individual building (e.g. Building P - Copérnico), powered by `DirectedGraph`
(which inherits directly from `graphCombined.Graph`).

Provides:
  - Room-to-room Dijkstra shortest-path routing and wheelchair accessibility filtering
  - Automatic parent `buildingId` propagation onto every indoor room/annex/area node
  - Shared `calcIndoorDistance()` Haversine helper (eliminating per-file duplication)
  - Direct delegation to the `graphCombined.Graph` interface (`search`, `addVertex`,
    `insertVertex`, `addEdge`, `link`, `deleteEdge`, `display`, `printMatrix`)
================================================================================
"""

from typing import Dict, List, Optional, Tuple, Union

from backend.graph.directedGraph import DirectedEdge, DirectedGraph, Node, Vertex
from backend.graph.dijkstraRouter import DijkstraRouter
from backend.graph.geoUtils import CampusGeoUtils
from backend.i18n import t, normalize_language
from backend.data.campusLocalization import (
    getIndoorNodeNames,
    getLocalizedSubgraphName,
    getLocalizedSubgraphDescription,
)


def calcIndoorDistance(
    lat1: float,
    lng1: float,
    lat2: float,
    lng2: float,
    minDist: float = 2.0,
) -> float:
    """
    Shared Haversine helper for indoor corridor weights (meters), enforcing a
    positive minimum step length to guarantee W(e) > 0 for co-located rooms.
    """
    d = CampusGeoUtils.calculateHaversineDistance(lat1, lng1, lat2, lng2)
    return max(minDist, round(d, 1))


def makeIndoorDistanceCalculator(defaultMinDist: float = 2.0):
    """Returns a reusable distance helper with a custom default minimum distance."""
    def _calc(
        lat1: float,
        lng1: float,
        lat2: float,
        lng2: float,
        minDist: float = defaultMinDist,
    ) -> float:
        return calcIndoorDistance(lat1, lng1, lat2, lng2, minDist)
    return _calc


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
        description: str = "",
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

    def getName(self, lang: str = "spa") -> str:
        """Returns the localized building subgraph display name."""
        return getLocalizedSubgraphName(self.buildingId, self.name, lang=lang)

    def getDescription(self, lang: str = "spa") -> str:
        """Returns the localized building subgraph description."""
        return getLocalizedSubgraphDescription(self.buildingId, self.description, lang=lang)

    def registerRoomAlias(self, alias: str, targetNodeId: str) -> None:
        """Maps an alternative room query, code, or alias to a target node ID."""
        self.roomAliases[alias] = targetNodeId

    def addNode(self, node: Node) -> Node:
        """
        Adds an internal room, stairwell, restroom, annex, or POI node.
        Automatically links `node.buildingId` to `self.macroNodeId` when omitted
        and attaches bilingual (Spanish/English) localized node names.
        """
        if not node.buildingId:
            node.buildingId = self.macroNodeId
        if not node.landmarkNameSpa or not node.landmarkNameEng:
            spaName, engName = getIndoorNodeNames(node.nodeId, node.name)
            if not node.landmarkNameSpa:
                node.landmarkNameSpa = spaName
            if not node.landmarkNameEng:
                node.landmarkNameEng = engName
        return self.graph.addNode(node)

    # ------------------------------------------------------------------
    # Direct `graphCombined.Graph` guide interface delegation
    # ------------------------------------------------------------------
    def search(self, target: Union[str, Vertex]) -> Optional[Vertex]:
        return self.graph.search(target)

    def addVertex(self, vertexOrId: Union[str, Vertex]) -> Node:
        node = self.graph.addVertex(vertexOrId)
        if not node.buildingId:
            node.buildingId = self.macroNodeId
        return node

    def insertVertex(self, vertexOrId: Union[str, Vertex]) -> bool:
        if self.graph.search(vertexOrId) is not None:
            return False
        self.addVertex(vertexOrId)
        return True

    def addEdge(
        self,
        origin: Union[str, Vertex],
        destination: Union[str, Vertex],
        weight: float,
        isAccessible: bool = True,
        stepInstruction: str = "",
        walkwayType: str = "indoor",
    ) -> bool:
        return self.graph.addEdge(
            origin=origin,
            destination=destination,
            weight=weight,
            isAccessible=isAccessible,
            stepInstruction=stepInstruction,
            walkwayType=walkwayType,
        )

    def link(
        self,
        origin: Union[str, Vertex],
        destination: Union[str, Vertex],
        weight: float,
    ) -> bool:
        return self.addEdge(origin, destination, weight)

    def deleteEdge(
        self,
        origin: Union[str, Vertex],
        destination: Union[str, Vertex],
    ) -> bool:
        return self.graph.deleteEdge(origin, destination)

    def display(self) -> None:
        print(f"=== Subgrafo {self.buildingId}: {self.name} ===")
        self.graph.display()

    def printMatrix(self) -> None:
        print(f"=== Matriz de Adyacencia: {self.buildingId} ===")
        self.graph.printMatrix()

    def getGraphSummary(self) -> dict:
        summary = self.graph.getGraphSummary()
        summary.update({
            "buildingId": self.buildingId,
            "name": self.name,
            "code": self.code,
            "macroNodeId": self.macroNodeId,
            "floors": self.floors,
            "floorCount": len(self.floors),
            "entranceCount": len(self.entranceNodeIds),
        })
        return summary

    def addBidirectionalCorridor(
        self,
        nodeAId: str,
        nodeBId: str,
        distanceMeters: float,
        isAccessible: bool = True,
        forwardInstruction: str = "",
        backwardInstruction: str = "",
        forwardEdgeKey: Optional[str] = None,
        backwardEdgeKey: Optional[str] = None,
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
            backwardEdgeKey=backwardEdgeKey,
            walkwayType="indoor",
        )

    # Alias for compatibility with subgraphs calling addBidirectionalWalkway
    addBidirectionalWalkway = addBidirectionalCorridor

    def addVerticalConnection(
        self,
        lowerNodeId: str,
        upperNodeId: str,
        distanceMeters: float = 12.0,
        isAccessible: bool = False,
        upInstruction: Optional[str] = None,
        downInstruction: Optional[str] = None,
    ) -> None:
        """
        Adds vertical transition between floors (stairs, ramps, or elevators).
        """
        vType = "ramp" if isAccessible else "stairs"
        resolvedUp = upInstruction if upInstruction is not None else t("navigation.indoor_stairs_up_default", lang="eng")
        resolvedDown = downInstruction if downInstruction is not None else t("navigation.indoor_stairs_down_default", lang="eng")
        self.graph.addDirectedEdge(
            lowerNodeId, upperNodeId, distanceMeters,
            isAccessible=isAccessible, stepInstruction=resolvedUp, walkwayType=vType,
        )
        self.graph.addDirectedEdge(
            upperNodeId, lowerNodeId, distanceMeters,
            isAccessible=isAccessible, stepInstruction=resolvedDown, walkwayType=vType,
        )

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
        floorLevel: Optional[int] = None,
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

        # 2. Check room number or bilingual name match
        for nid, node in self.graph.nodes.items():
            for candidateName in (node.name, node.landmarkNameSpa, node.landmarkNameEng):
                if not candidateName:
                    continue
                nameNorm = _normalize(candidateName)
                if clean in nameNorm or nameNorm in clean:
                    return nid

        return None

    def calculateIndoorRoute(
        self,
        originQuery: str,
        destinationQuery: str,
        accessibleOnly: bool = False,
        lang: str = "spa",
    ) -> dict:
        """
        Calculates turn-by-turn indoor route between two locations inside this building.
        """
        activeLang = normalize_language(lang)
        localizedBuilding = t(f"nodes.{self.macroNodeId}", lang=activeLang, default=self.name)
        originId = self.resolveRoomQuery(originQuery) or originQuery
        destId = self.resolveRoomQuery(destinationQuery) or destinationQuery

        if originId not in self.graph.nodes:
            return {
                "success": False,
                "error": t("navigation.indoor_origin_not_found", lang=activeLang, query=originQuery, building=localizedBuilding),
            }

        if destId not in self.graph.nodes:
            return {
                "success": False,
                "error": t("navigation.indoor_dest_not_found", lang=activeLang, query=destinationQuery, building=localizedBuilding),
            }

        path, dist, mins, _ = self.router.findShortestPathWithEdges(
            originId, destId, accessibleOnly=accessibleOnly
        )

        if not path:
            return {
                "success": False,
                "error": t("navigation.indoor_no_route", lang=activeLang),
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
            "buildingName": self.getName(activeLang),
            "origin": {
                "nodeId": originId,
                "name": originNode.getName(lang),
                "floorLevel": originNode.floorLevel,
            },
            "destination": {
                "nodeId": destId,
                "name": destNode.getName(lang),
                "floorLevel": destNode.floorLevel,
            },
            "pathNodeIds": path,
            "pathDetails": pathDetails,
            "floorsCrossed": floorsCrossed,
            "totalDistanceMeters": dist,
            "estimatedWalkingMinutes": mins,
            "humanDuration": formatHumanWalkingTime(dist, lang=lang),
            "steps": humanSteps,
            "stepInstructions": instructions,
            "isAccessibleRoute": accessibleOnly,
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

        metrics = self.graph.getGraphSummary()
        return {
            "buildingId": self.buildingId,
            "name": self.getName(lang),
            "code": self.code,
            "floors": self.floors,
            "macroNodeId": self.macroNodeId,
            "entranceNodeIds": self.entranceNodeIds,
            "description": self.getDescription(lang),
            "nodesCount": len(nodesList),
            "edgesCount": metrics["directedEdgeCount"],
            "density": metrics["density"],
            "isComplete": metrics["isComplete"],
            "nodes": nodesList,
        }
