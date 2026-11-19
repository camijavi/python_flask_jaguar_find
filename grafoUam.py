"""
grafoUam.py
Backward-compatibility facade for the modular 'graph' package.
All graph logic and data structures are maintained in 'graph/'.
"""

from graph import (
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
]
