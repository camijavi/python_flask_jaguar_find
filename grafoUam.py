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
)
from backend.subgraphs import (
    BuildingSubgraph,
    buildingPSubgraph,
    buildingDSubgraph,
    buildingJSubgraph,
    buildingOSubgraph,
    buildingCSubgraph,
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
    "buildingDSubgraph",
    "buildingJSubgraph",
    "buildingOSubgraph",
    "buildingCSubgraph",
    "getBuildingSubgraph",
    "getAllBuildingSubgraphs",
    "BUILDING_SUBGRAPHS",
]
