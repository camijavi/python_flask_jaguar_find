"""
graph package
Modular graph package for the UAM Campus pedestrian navigation system.
Supports full bilingual internationalization (i18n) via eng.json and spa.json.
"""

from .directedGraph import DirectedEdge, Node, DirectedGraph
from .dijkstraRouter import DijkstraRouter
from .geoUtils import CampusGeoUtils
from .campusGraphBuilder import buildUamCampusGraph
from .navigationService import NavigationService, globalNavigationService
from .campusCategories import CampusCategory, CATEGORY_METADATA
from .placesCatalog import PLACES_CATALOG
from .i18n import I18nManager, t

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
