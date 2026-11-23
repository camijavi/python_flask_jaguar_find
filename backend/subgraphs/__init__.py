"""
subgraphs package
================================================================================
CHILD GRAPHS / SUBGRAPHS FOR ALL UAM CAMPUS BUILDINGS & COMPLEXES
================================================================================
Provides indoor navigation graphs per building (A through P + Jaguar Center &
Sports Fields) with real field GPS coordinates (coordenadas.txt), corridor
edges, multi-floor routing, accessibility filtering, and Gateway Pattern rules.
================================================================================
"""

from typing import Dict, Optional
from .buildingSubgraph import BuildingSubgraph
from .buildingA import buildingASubgraph, buildBuildingASubgraph
from .buildingB import buildingBSubgraph, buildBuildingBSubgraph
from .buildingC import buildingCSubgraph, buildBuildingCSubgraph
from .buildingD import buildingDSubgraph, buildBuildingDSubgraph
from .buildingE import buildingESubgraph, buildBuildingESubgraph
from .buildingF import buildingFSubgraph, buildBuildingFSubgraph
from .buildingG import buildingGSubgraph, buildBuildingGSubgraph
from .buildingH import buildingHSubgraph, buildBuildingHSubgraph
from .buildingI import buildingISubgraph, buildBuildingISubgraph
from .buildingJ import buildingJSubgraph, buildBuildingJSubgraph
from .buildingK import buildingKSubgraph, buildBuildingKSubgraph
from .buildingL import buildingLSubgraph, buildBuildingLSubgraph
from .buildingM import buildingMSubgraph, buildBuildingMSubgraph
from .buildingN import buildingNSubgraph, buildBuildingNSubgraph
from .buildingO import buildingOSubgraph, buildBuildingOSubgraph
from .buildingP import buildingPSubgraph, buildBuildingPSubgraph
from .sportsComplex import (
    jaguarCenterSubgraph,
    buildJaguarCenterSubgraph,
    sportsZoneSubgraph,
    buildSportsZoneSubgraph,
)

# Registry of all active building & complex child graphs
BUILDING_SUBGRAPHS: Dict[str, BuildingSubgraph] = {
    "buildingA": buildingASubgraph,
    "buildingB": buildingBSubgraph,
    "buildingC": buildingCSubgraph,
    "buildingD": buildingDSubgraph,
    "buildingE": buildingESubgraph,
    "buildingF": buildingFSubgraph,
    "buildingG": buildingGSubgraph,
    "buildingH": buildingHSubgraph,
    "buildingI": buildingISubgraph,
    "buildingJ": buildingJSubgraph,
    "buildingK": buildingKSubgraph,
    "buildingL": buildingLSubgraph,
    "buildingM": buildingMSubgraph,
    "buildingN": buildingNSubgraph,
    "buildingO": buildingOSubgraph,
    "buildingP": buildingPSubgraph,
    "jaguarCenter": jaguarCenterSubgraph,
    "sportsZone": sportsZoneSubgraph,
}

_BUILDING_ALIASES: Dict[str, str] = {}
for _letter in "abcdefghijklmnop":
    _bid = f"building{_letter.upper()}"
    _BUILDING_ALIASES[_letter] = _bid
    _BUILDING_ALIASES[f"building{_letter}"] = _bid
    _BUILDING_ALIASES[f"edificio{_letter}"] = _bid

_BUILDING_ALIASES.update({
    "jc": "jaguarCenter",
    "jaguarcenter": "jaguarCenter",
    "jaguargym": "jaguarCenter",
    "physiotherapy": "jaguarCenter",
    "fisioterapia": "jaguarCenter",
    "sp": "sportsZone",
    "sportszone": "sportsZone",
    "camposdeportivos": "sportsZone",
})


def getBuildingSubgraph(buildingId: str) -> Optional[BuildingSubgraph]:
    """Retrieves the indoor child graph for a given building ID or letter alias."""
    cleanId = (buildingId or "").strip()
    if cleanId in BUILDING_SUBGRAPHS:
        return BUILDING_SUBGRAPHS[cleanId]
    norm = cleanId.lower().replace(" ", "").replace("-", "").replace("_", "")
    canonical = _BUILDING_ALIASES.get(norm)
    if canonical:
        return BUILDING_SUBGRAPHS.get(canonical)
    return None


def getAllBuildingSubgraphs() -> Dict[str, BuildingSubgraph]:
    """Returns all registered building subgraphs."""
    return dict(BUILDING_SUBGRAPHS)


def registerBuildingSubgraph(buildingId: str, subgraph: BuildingSubgraph) -> None:
    """Registers a new building child graph into the catalog."""
    BUILDING_SUBGRAPHS[buildingId] = subgraph


__all__ = [
    "BuildingSubgraph",
    "buildingASubgraph", "buildBuildingASubgraph",
    "buildingBSubgraph", "buildBuildingBSubgraph",
    "buildingCSubgraph", "buildBuildingCSubgraph",
    "buildingDSubgraph", "buildBuildingDSubgraph",
    "buildingESubgraph", "buildBuildingESubgraph",
    "buildingFSubgraph", "buildBuildingFSubgraph",
    "buildingGSubgraph", "buildBuildingGSubgraph",
    "buildingHSubgraph", "buildBuildingHSubgraph",
    "buildingISubgraph", "buildBuildingISubgraph",
    "buildingJSubgraph", "buildBuildingJSubgraph",
    "buildingKSubgraph", "buildBuildingKSubgraph",
    "buildingLSubgraph", "buildBuildingLSubgraph",
    "buildingMSubgraph", "buildBuildingMSubgraph",
    "buildingNSubgraph", "buildBuildingNSubgraph",
    "buildingOSubgraph", "buildBuildingOSubgraph",
    "buildingPSubgraph", "buildBuildingPSubgraph",
    "jaguarCenterSubgraph", "buildJaguarCenterSubgraph",
    "sportsZoneSubgraph", "buildSportsZoneSubgraph",
    "BUILDING_SUBGRAPHS",
    "getBuildingSubgraph",
    "getAllBuildingSubgraphs",
    "registerBuildingSubgraph",
]
