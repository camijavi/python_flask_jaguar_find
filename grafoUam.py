"""
grafoUam.py
Backward-compatibility facade for the modular 'backend.graph' package.
All graph logic and data structures are maintained in 'backend/graph/'.
"""

from backend.graph import (
    DirectedEdge,
    Node,
    DirectedGraph,
    DijkstraRouter,
    CampusGeoUtils,
    buildUamCampusGraph,
    NavigationService,
    globalNavigationService,
    CampusCategory,
    CATEGORY_METADATA,
    PLACES_CATALOG,
    I18nManager,
    t,
    BuildingSubgraph,
    buildingPSubgraph,
    getBuildingSubgraph,
    getAllBuildingSubgraphs,
    BUILDING_SUBGRAPHS,
)

__all__ = [
    "DirectedEdge",
    "Node",
    "DirectedGraph",
    "DijkstraRouter",
    "CampusGeoUtils",
    "buildUamCampusGraph",
    "NavigationService",
    "globalNavigationService",
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
