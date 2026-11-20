"""
directedGraph.py
Core data structures for directed graph representation:
DirectedEdge, Node, and DirectedGraph (Adjacency List).
Supports internationalization (i18n) for entity labels and directions.
"""

from typing import Dict, List, Optional
from .i18n import t, I18nManager


class DirectedEdge:
    """
    Represents a directed pedestrian path segment (u -> v) with a positive metric weight (meters).
    """
    def __init__(
        self,
        targetNodeId: str,
        distanceMeters: float,
        isAccessible: bool = True,
        stepInstruction: str = "",
        edgeKey: Optional[str] = None
    ):
        self.targetNodeId = targetNodeId
        self.distanceMeters = distanceMeters
        self.isAccessible = isAccessible
        self.stepInstruction = stepInstruction
        self.edgeKey = edgeKey

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
            "edgeKey": self.edgeKey
        }


class Node:
    """
    Represents a physical building entrance, pedestrian gate, or junction on the UAM campus.
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
        isOutdoorAccessPoint: bool = True
    ):
        self.nodeId = nodeId
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
        self.outgoingEdges: List[DirectedEdge] = []

    def getName(self, lang: str = "eng") -> str:
        """Returns localized node name, falling back to default self.name."""
        return t(f"nodes.{self.nodeId}", lang=lang, default=self.name)

    def getAccessNotice(self, lang: str = "eng") -> Optional[str]:
        """Returns localized access notice, falling back to self.accessNotice."""
        return I18nManager.getInstance().getAccessNotice(self.nodeId, lang=lang, fallback=self.accessNotice)

    def addOutgoingEdge(self, edge: DirectedEdge) -> None:
        self.outgoingEdges.append(edge)

    def toDict(self, lang: str = "eng") -> dict:
        return {
            "nodeId": self.nodeId,
            "name": self.getName(lang),
            "category": self.category,
            "xPercent": self.xPercent,
            "yPercent": self.yPercent,
            "latitude": self.latitude,
            "longitude": self.longitude,
            "floorLevel": self.floorLevel,
            "accessLevel": self.accessLevel,
            "accessNotice": self.getAccessNotice(lang),
            "isOutdoorAccessPoint": self.isOutdoorAccessPoint
        }


class DirectedGraph:
    """
    Weighted, Directed, Non-Complete Graph G = (V, E, W) representing the UAM Campus.
    """
    def __init__(self):
        self.nodes: Dict[str, Node] = {}

    def addNode(self, node: Node) -> None:
        if node.nodeId not in self.nodes:
            self.nodes[node.nodeId] = node

    def addDirectedEdge(
        self,
        sourceNodeId: str,
        targetNodeId: str,
        distanceMeters: float,
        isAccessible: bool = True,
        stepInstruction: str = "",
        edgeKey: Optional[str] = None
    ) -> None:
        """Adds a single directed edge from source to target (u -> v)."""
        if sourceNodeId in self.nodes and targetNodeId in self.nodes:
            key = edgeKey or f"{sourceNodeId}_{targetNodeId}"
            edge = DirectedEdge(targetNodeId, distanceMeters, isAccessible, stepInstruction, edgeKey=key)
            self.nodes[sourceNodeId].addOutgoingEdge(edge)

    def addBidirectionalWalkway(
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
        """
        Creates two opposite directed edges (u -> v) and (v -> u)
        to model a bidirectional pedestrian sidewalk with equal physical weight.
        """
        fwdKey = forwardEdgeKey or f"{nodeAId}_{nodeBId}"
        bwdKey = backwardEdgeKey or f"{nodeBId}_{nodeAId}"
        self.addDirectedEdge(nodeAId, nodeBId, distanceMeters, isAccessible, forwardInstruction, edgeKey=fwdKey)
        self.addDirectedEdge(nodeBId, nodeAId, distanceMeters, isAccessible, backwardInstruction, edgeKey=bwdKey)

    def getNode(self, nodeId: str) -> Optional[Node]:
        return self.nodes.get(nodeId)

    def getAllNodes(self) -> List[Node]:
        return list(self.nodes.values())
