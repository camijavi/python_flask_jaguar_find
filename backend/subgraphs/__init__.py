"""
subgraphs package
================================================================================
CHILD GRAPHS / SUBGRAPHS FOR CAMPUS BUILDINGS
================================================================================
Provides indoor navigation graphs per building with high-resolution coordinates,
corridor edges, multi-floor routing, and vertical transitions (stairs/ramps).
================================================================================
"""

from typing import Dict, Optional, List
from .buildingSubgraph import BuildingSubgraph
from .buildingP import buildingPSubgraph, buildBuildingPSubgraph
from .buildingD import buildingDSubgraph, buildBuildingDSubgraph
from .buildingJ import buildingJSubgraph, buildBuildingJSubgraph
from .buildingO import buildingOSubgraph, buildBuildingOSubgraph
from .buildingC import buildingCSubgraph, buildBuildingCSubgraph

# Registry of active building subgraphs
BUILDING_SUBGRAPHS: Dict[str, BuildingSubgraph] = {
    "buildingP": buildingPSubgraph,
    "buildingD": buildingDSubgraph,
    "buildingJ": buildingJSubgraph,
    "buildingO": buildingOSubgraph,
    "buildingC": buildingCSubgraph,
}


def getBuildingSubgraph(buildingId: str) -> Optional[BuildingSubgraph]:
    """Retrieves the indoor child graph for a given building ID (e.g. 'buildingP', 'buildingD', 'buildingJ', 'buildingO', 'buildingC')."""
    cleanId = (buildingId or "").strip()
    # Normalize if user passes "p", "buildingP", "d", "buildingD", "j", "buildingJ", "o", "buildingO", "c", "buildingC"
    if cleanId.lower() in ("p", "buildingp", "edificiop"):
        cleanId = "buildingP"
    elif cleanId.lower() in ("d", "buildingd", "edificiod"):
        cleanId = "buildingD"
    elif cleanId.lower() in ("j", "buildingj", "edificioj"):
        cleanId = "buildingJ"
    elif cleanId.lower() in ("o", "buildingo", "edificioo"):
        cleanId = "buildingO"
    elif cleanId.lower() in ("c", "buildingc", "edificioc"):
        cleanId = "buildingC"
    return BUILDING_SUBGRAPHS.get(cleanId)


def getAllBuildingSubgraphs() -> Dict[str, BuildingSubgraph]:
    """Returns all registered building subgraphs."""
    return dict(BUILDING_SUBGRAPHS)


def registerBuildingSubgraph(buildingId: str, subgraph: BuildingSubgraph) -> None:
    """Registers a new building child graph into the catalog."""
    BUILDING_SUBGRAPHS[buildingId] = subgraph


__all__ = [
    "BuildingSubgraph",
    "buildingPSubgraph",
    "buildBuildingPSubgraph",
    "buildingDSubgraph",
    "buildBuildingDSubgraph",
    "buildingJSubgraph",
    "buildBuildingJSubgraph",
    "buildingOSubgraph",
    "buildBuildingOSubgraph",
    "buildingCSubgraph",
    "buildBuildingCSubgraph",
    "BUILDING_SUBGRAPHS",
    "getBuildingSubgraph",
    "getAllBuildingSubgraphs",
    "registerBuildingSubgraph",
]
