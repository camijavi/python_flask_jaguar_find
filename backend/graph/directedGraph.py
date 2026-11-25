"""
directedGraph.py
================================================================================
CAMPUS DOMAIN EXTENSION OF THE CENTRAL `graphCombined.py` DATA STRUCTURE
================================================================================
Builds directly on `Vertex` and `Graph` from `graphCombined.py` (the central
weighted, directed, non-complete graph G = (V, E, W) recommended for the project):
  - `Node(Vertex)`: extends `Vertex` with GPS/SVG coordinates, floor level,
    category, access notices, i18n labels, and rich `DirectedEdge` metadata.
  - `DirectedGraph(Graph)`: extends `Graph` while keeping `self.vertices`,
    `self.nodes`, `vertex.neigh`, and `node.outgoingEdges` in strict 1:1 sync.
================================================================================
"""

from __future__ import annotations

from typing import Dict, List, Optional, Union

from .graphCombined import Graph, Vertex

from .i18n import t, I18nManager, normalize_language


class DirectedEdge:
    """
    Represents a directed pedestrian path segment (u -> v) with a positive metric
    weight (meters) and navigation metadata (accessibility, walkway type, i18n key).
    """

    def __init__(
        self,
        targetNodeId: str,
        distanceMeters: float,
        isAccessible: bool = True,
        stepInstruction: str = "",
        edgeKey: Optional[str] = None,
        walkwayType: str = "ground",
        landmarkRef: str = "",
        targetVertex: Optional[Vertex] = None,
    ):
        self.targetNodeId = targetNodeId
        self.targetVertex = targetVertex
        self.distanceMeters = max(0.5, float(distanceMeters))
        self.isAccessible = isAccessible
        self.stepInstruction = stepInstruction
        self.edgeKey = edgeKey
        self.walkwayType = walkwayType      # "ground" | "indoor" | "level2" | "stairs" | "ramp" | "crosswalk"
        self.landmarkRef = landmarkRef

    def getInstruction(self, lang: str = "eng") -> str:
        """Returns localized step instruction, falling back to English/default stepInstruction."""
        if self.edgeKey:
            return t(f"walkways.{self.edgeKey}", lang=lang, default=self.stepInstruction)
        return self.stepInstruction

    def toDict(self) -> dict:
        return {
            "targetNodeId": self.targetNodeId,
            "distanceMeters": self.distanceMeters,
            "isAccessible": self.isAccessible,
            "stepInstruction": self.stepInstruction,
            "edgeKey": self.edgeKey,
            "walkwayType": self.walkwayType,
            "landmarkRef": self.landmarkRef,
        }


class Node(Vertex):
    """
    Domain vertex inheriting from `graphCombined.Vertex`.
    Represents a physical building, entrance portal, pedestrian walkway waypoint,
    classroom, annex, restroom, ramp, stairwell, or campus area.
    """

    def __init__(
        self,
        nodeId: str,
        name: str,
        category: str,
        xPercent: float,
        yPercent: float,
        latitude: float,
        longitude: float,
        floorLevel: int = 1,
        accessLevel: str = "public",        # "public", "restricted", "facultyOnly"
        accessNotice: Optional[str] = None, # Notice displayed upon arrival (e.g. biosecurity)
        isOutdoorAccessPoint: bool = True,
        xSvg: Optional[float] = None,
        ySvg: Optional[float] = None,
        portalKind: Optional[str] = None,   # "door" | "corridor" | "stairs" | "ramp" | "crosswalk" | "skybridge" | "gate" | "plaza"
        buildingId: Optional[str] = None,
        landmarkNameSpa: Optional[str] = None,
        landmarkNameEng: Optional[str] = None,
    ):
        super().__init__(nodeId)
        self.name = name                    # Default internal name in English
        self.category = category
        self.xPercent = xPercent
        self.yPercent = yPercent
        self.latitude = latitude
        self.longitude = longitude
        self.floorLevel = floorLevel
        self.accessLevel = accessLevel
        self.accessNotice = accessNotice
        self.isOutdoorAccessPoint = isOutdoorAccessPoint
        self.xSvg = xSvg if xSvg is not None else round((xPercent / 100.0) * 1200.0, 1)
        self.ySvg = ySvg if ySvg is not None else round((yPercent / 100.0) * 850.0, 1)
        self.portalKind = portalKind
        self.buildingId = buildingId
        self.landmarkNameSpa = landmarkNameSpa
        self.landmarkNameEng = landmarkNameEng
        self.outgoingEdges: List[DirectedEdge] = []

    def getName(self, lang: str = "eng") -> str:
        """Returns localized node name, falling back to default self.name."""
        activeLang = normalize_language(lang)
        if activeLang == "spa" and self.landmarkNameSpa:
            return self.landmarkNameSpa
        if activeLang == "eng" and self.landmarkNameEng:
            return self.landmarkNameEng
        return t(f"nodes.{self.nodeId}", lang=activeLang, default=self.name)

    def getAccessNotice(self, lang: str = "eng") -> Optional[str]:
        """Returns localized access notice, falling back to self.accessNotice."""
        return I18nManager.getInstance().getAccessNotice(self.nodeId, lang=lang, fallback=self.accessNotice)

    def addOutgoingEdge(self, edge: DirectedEdge) -> None:
        self.outgoingEdges.append(edge)
        if edge.targetVertex is not None and not any(
            neighbor is edge.targetVertex for neighbor, _ in self.neigh
        ):
            self.neigh.append((edge.targetVertex, edge.distanceMeters))

    def toDict(self, lang: str = "eng") -> dict:
        return {
            "nodeId": self.nodeId,
            "name": self.getName(lang),
            "category": self.category,
            "xPercent": self.xPercent,
            "yPercent": self.yPercent,
            "xSvg": self.xSvg,
            "ySvg": self.ySvg,
            "latitude": self.latitude,
            "longitude": self.longitude,
            "floorLevel": self.floorLevel,
            "accessLevel": self.accessLevel,
            "accessNotice": self.getAccessNotice(lang),
            "isOutdoorAccessPoint": self.isOutdoorAccessPoint,
            "portalKind": self.portalKind,
            "buildingId": self.buildingId,
        }


class DirectedGraph(Graph):
    """
    Weighted, Directed, Non-Complete Graph G = (V, E, W) inheriting from
    `graphCombined.Graph`. Used by every macro, walkway, and indoor building
    graph across the entire JaguarFind & JaguarMaps application.
    """

    def __init__(self):
        super().__init__()
        self.nodes: Dict[str, Node] = {}

    def addVertex(self, vertexOrId: Union[str, Vertex]) -> Node:
        """
        Registers a Node (or wraps a string ID into a lightweight Node) using
        the base `Graph.addVertex()` logic and indexes it in `self.nodes`.
        """
        existing = self.search(vertexOrId)
        if existing is not None:
            return existing  # type: ignore[return-value]

        if isinstance(vertexOrId, Node):
            node = vertexOrId
        else:
            rawId = vertexOrId.nodeId if isinstance(vertexOrId, Vertex) else str(vertexOrId)
            node = Node(
                nodeId=rawId,
                name=rawId,
                category="waypoint",
                xPercent=50.0,
                yPercent=50.0,
                latitude=0.0,
                longitude=0.0,
            )

        super().addVertex(node)
        self.nodes[node.nodeId] = node
        return node

    def addNode(self, node: Node) -> Node:
        """Adds a campus Node vertex to the graph (delegates to addVertex)."""
        return self.addVertex(node)

    def addEdge(
        self,
        origin: Union[str, Vertex],
        destination: Union[str, Vertex],
        weight: float,
        isAccessible: bool = True,
        stepInstruction: str = "",
        edgeKey: Optional[str] = None,
        walkwayType: str = "ground",
        landmarkRef: str = "",
    ) -> bool:
        """
        Adds a single directed weighted edge (origin -> destination) enforcing
        `graphCombined.Graph` invariants (positive weight, no self-loops,
        no duplicate edges) while synchronizing `neigh` and `outgoingEdges`.
        """
        v_origin = self.search(origin)
        v_destination = self.search(destination)
        if v_origin is None or v_destination is None:
            return False

        distance = max(0.5, float(weight))
        if not super().addEdge(v_origin, v_destination, distance):
            return False

        key = edgeKey or f"{v_origin.nodeId}_{v_destination.nodeId}"
        edge = DirectedEdge(
            targetNodeId=v_destination.nodeId,
            distanceMeters=distance,
            isAccessible=isAccessible,
            stepInstruction=stepInstruction,
            edgeKey=key,
            walkwayType=walkwayType,
            landmarkRef=landmarkRef,
            targetVertex=v_destination,
        )
        if isinstance(v_origin, Node):
            v_origin.outgoingEdges.append(edge)
        return True

    def addDirectedEdge(
        self,
        sourceNodeId: str,
        targetNodeId: str,
        distanceMeters: float,
        isAccessible: bool = True,
        stepInstruction: str = "",
        edgeKey: Optional[str] = None,
        walkwayType: str = "ground",
        landmarkRef: str = "",
    ) -> bool:
        """Adds a single directed edge from source to target (u -> v)."""
        return self.addEdge(
            origin=sourceNodeId,
            destination=targetNodeId,
            weight=distanceMeters,
            isAccessible=isAccessible,
            stepInstruction=stepInstruction,
            edgeKey=edgeKey,
            walkwayType=walkwayType,
            landmarkRef=landmarkRef,
        )

    def addBidirectionalWalkway(
        self,
        nodeAId: str,
        nodeBId: str,
        distanceMeters: float,
        isAccessible: bool = True,
        forwardInstruction: str = "",
        backwardInstruction: str = "",
        forwardEdgeKey: Optional[str] = None,
        backwardEdgeKey: Optional[str] = None,
        walkwayType: str = "ground",
        landmarkRef: str = "",
    ) -> None:
        """
        Creates two opposite directed edges (u -> v) and (v -> u)
        to model a bidirectional pedestrian sidewalk with equal physical weight.
        """
        fwdKey = forwardEdgeKey or f"{nodeAId}_{nodeBId}"
        bwdKey = backwardEdgeKey or f"{nodeBId}_{nodeAId}"
        self.addDirectedEdge(
            nodeAId, nodeBId, distanceMeters, isAccessible, forwardInstruction,
            edgeKey=fwdKey, walkwayType=walkwayType, landmarkRef=landmarkRef,
        )
        self.addDirectedEdge(
            nodeBId, nodeAId, distanceMeters, isAccessible, backwardInstruction,
            edgeKey=bwdKey, walkwayType=walkwayType, landmarkRef=landmarkRef,
        )

    def deleteEdge(
        self,
        origin: Union[str, Vertex],
        destination: Union[str, Vertex],
    ) -> bool:
        """Removes directed edge (origin -> destination) from both `neigh` and `outgoingEdges`."""
        v_origin = self.search(origin)
        v_destination = self.search(destination)
        if not super().deleteEdge(origin, destination):
            return False

        if isinstance(v_origin, Node) and v_destination is not None:
            v_origin.outgoingEdges = [
                edge for edge in v_origin.outgoingEdges
                if edge.targetNodeId != v_destination.nodeId
            ]
        return True

    def getNode(self, nodeId: str) -> Optional[Node]:
        return self.nodes.get(nodeId)

    def getAllNodes(self) -> List[Node]:
        return list(self.vertices)  # type: ignore[return-value]
