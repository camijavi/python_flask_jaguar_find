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

# Registry of active building subgraphs
BUILDING_SUBGRAPHS: Dict[str, BuildingSubgraph] = {
    "buildingP": buildingPSubgraph,
}


def getBuildingSubgraph(buildingId: str) -> Optional[BuildingSubgraph]:
    """Retrieves the indoor child graph for a given building ID (e.g. 'buildingP')."""
    cleanId = (buildingId or "").strip()
    # Normalize if user passes "p", "P", "buildingP", "edificioP"
    if cleanId.lower() in ("p", "buildingp", "edificiop"):
        cleanId = "buildingP"
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
    "BUILDING_SUBGRAPHS",
    "getBuildingSubgraph",
    "getAllBuildingSubgraphs",
    "registerBuildingSubgraph",
]
