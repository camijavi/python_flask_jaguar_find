"""
graph package
Modular graph package for the UAM Campus pedestrian navigation system.
Built directly on top of the central `graph.graphCombined` data structure
(Vertex, Graph) and supports full bilingual internationalization (i18n).
"""

from .directedGraph import Vertex, Graph, DirectedEdge, Node, DirectedGraph
from .dijkstraRouter import DijkstraRouter
from .geoUtils import CampusGeoUtils
from .campusGraphBuilder import buildUamCampusGraph
from .pedestrianWalkwayGraph import buildPedestrianWalkwayGraph, globalPedestrianWalkwayGraph
from .navigationService import NavigationService, globalNavigationService
from .graphRegistry import getAllApplicationGraphs, getGraphsInventory
from .campusCategories import CampusCategory, CATEGORY_METADATA
from .placesCatalog import PLACES_CATALOG
from .i18n import I18nManager, t

_SUBGRAPH_EXPORTS = {
    "BuildingSubgraph",
    "buildingPSubgraph",
    "getBuildingSubgraph",
    "getAllBuildingSubgraphs",
    "BUILDING_SUBGRAPHS",
}


def __getattr__(name: str):
    if name in _SUBGRAPH_EXPORTS:
        import backend.subgraphs as subgraphsPkg
        return getattr(subgraphsPkg, name)
    raise AttributeError(f"module '{__name__}' has no attribute '{name}'")


__all__ = [
    "Vertex",
    "Graph",
    "DirectedEdge",
    "Node",
    "DirectedGraph",
    "DijkstraRouter",
    "CampusGeoUtils",
    "buildUamCampusGraph",
    "buildPedestrianWalkwayGraph",
    "globalPedestrianWalkwayGraph",
    "NavigationService",
    "globalNavigationService",
    "getAllApplicationGraphs",
    "getGraphsInventory",
    "CampusCategory",
    "CATEGORY_METADATA",
    "PLACES_CATALOG",
    "I18nManager",
    "t",
    "BuildingSubgraph",
    "buildingPSubgraph",
    "getBuildingSubgraph",
    "getAllBuildingSubgraphs",
    "BUILDING_SUBGRAPHS",
]
