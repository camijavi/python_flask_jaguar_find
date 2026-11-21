"""
children_graphs package
================================================================================
Alias module for backend.subgraphs (Child graphs per campus building).
================================================================================
"""

from backend.subgraphs import (
    BuildingSubgraph,
    buildingPSubgraph,
    buildBuildingPSubgraph,
    BUILDING_SUBGRAPHS,
    getBuildingSubgraph,
    getAllBuildingSubgraphs,
    registerBuildingSubgraph,
)

__all__ = [
    "BuildingSubgraph",
    "buildingPSubgraph",
    "buildBuildingPSubgraph",
    "BUILDING_SUBGRAPHS",
    "getBuildingSubgraph",
    "getAllBuildingSubgraphs",
    "registerBuildingSubgraph",
]
