"""
buildingL.py
================================================================================
BUILDING L (CULTURA, MÚSICA, DUCHAS & ACCESO JAGUAR CENTER) SUBGRAPH
================================================================================
Single-floor indoor child graph built strictly from official UAM room directory
(buildings.txt) and field GPS measurements (coordenadas.txt).
Weighted, Directed, Non-Complete Graph G = (V, E, W).
================================================================================
"""

from backend.graph.directedGraph import Node
from backend.data.campusCategories import CampusCategory
from .buildingSubgraph import BuildingSubgraph, calcIndoorDistance as _calcDist


def buildBuildingLSubgraph() -> BuildingSubgraph:
    subgraph = BuildingSubgraph(
        buildingId="buildingL",
        name="Edificio L (Cultura, Música & Vestidores)",
        code="L",
        floors=[1],
        macroNodeId="buildingL",
        entranceNodeIds=["l_cultura_map", "l_jaguar_center_entry"],
        description="Edificio L: Duchas Visitantes, Duchas Home, Salón de Cultura, Aula de Música, Baños Hombres y Baños Mujeres."
    )

    # =========================================================================
    # FLOOR 1 (PLANTA ÚNICA) — Exact order from buildings.txt
    # =========================================================================
    subgraph.addNode(Node(
        nodeId="l_duchas_visitantes",
        name="Duchas Visitantes (Edificio L)",
        category=CampusCategory.SPORTS,
        xPercent=82.1, yPercent=69.1,
        latitude=12.108952, longitude=-86.258551,
        floorLevel=1, isOutdoorAccessPoint=False,
        buildingId="buildingL"
    ))
    subgraph.addNode(Node(
        nodeId="l_duchas_home",
        name="Duchas Home (Edificio L)",
        category=CampusCategory.SPORTS,
        xPercent=81.9, yPercent=68.9,
        latitude=12.108952, longitude=-86.258551,
        floorLevel=1, isOutdoorAccessPoint=False,
        buildingId="buildingL"
    ))
    subgraph.addNode(Node(
        nodeId="l_cultura_map",
        name="Salón de Cultura y Mapa UAM (Edificio L)",
        category=CampusCategory.CLASSROOM,
        xPercent=82.4, yPercent=72.0,
        latitude=12.109123, longitude=-86.258504,
        floorLevel=1, isOutdoorAccessPoint=True,
        portalKind="door", buildingId="buildingL"
    ))
    subgraph.addNode(Node(
        nodeId="l_musica",
        name="Aula de Música (Edificio L)",
        category=CampusCategory.CLASSROOM,
        xPercent=82.4, yPercent=71.2,
        latitude=12.109120, longitude=-86.258513,
        floorLevel=1, isOutdoorAccessPoint=False,
        buildingId="buildingL"
    ))
    subgraph.addNode(Node(
        nodeId="l_restrooms_men",
        name="Baños Hombres (Edificio L)",
        category=CampusCategory.RESTROOM,
        xPercent=81.9, yPercent=66.5,
        latitude=12.108905, longitude=-86.258519,
        floorLevel=1, isOutdoorAccessPoint=False,
        buildingId="buildingL"
    ))
    subgraph.addNode(Node(
        nodeId="l_restrooms_women",
        name="Baños Mujeres (Edificio L)",
        category=CampusCategory.RESTROOM,
        xPercent=82.1, yPercent=66.5,
        latitude=12.108905, longitude=-86.258519,
        floorLevel=1, isOutdoorAccessPoint=False,
        buildingId="buildingL"
    ))
    subgraph.addNode(Node(
        nodeId="l_jaguar_center_entry",
        name="Entrada a Jaguar Center por Edificio L",
        category=CampusCategory.SPORTS,
        xPercent=80.0, yPercent=72.0,
        latitude=12.109111, longitude=-86.258514,
        floorLevel=1, isOutdoorAccessPoint=True,
        portalKind="door", buildingId="buildingL"
    ))

    edges = [
        ("l_jaguar_center_entry", "l_cultura_map"),
        ("l_cultura_map", "l_musica"),
        ("l_musica", "l_duchas_home"),
        ("l_duchas_home", "l_duchas_visitantes"),
        ("l_duchas_visitantes", "l_restrooms_men"),
        ("l_restrooms_men", "l_restrooms_women"),
    ]
    for u, v in edges:
        nU, nV = subgraph.getNode(u), subgraph.getNode(v)
        subgraph.addBidirectionalCorridor(u, v, _calcDist(nU.latitude, nU.longitude, nV.latitude, nV.longitude), isAccessible=True)

    aliases = {
        "duchas visitantes": "l_duchas_visitantes", "showersVisitorsL": "l_duchas_visitantes", "duchas away": "l_duchas_visitantes",
        "duchas home": "l_duchas_home", "showersHomeL": "l_duchas_home", "duchas": "l_duchas_home",
        "l_duchas": "l_duchas_home", "showersTeamsL": "l_duchas_home",
        "salon de cultura": "l_cultura_map", "cultura": "l_cultura_map", "cultureHallL": "l_cultura_map",
        "aula de musica": "l_musica", "musica": "l_musica", "area de musica": "l_musica", "musicClassroomL": "l_musica",
        "baños l": "l_restrooms_men", "banos l": "l_restrooms_men", "l_restrooms": "l_restrooms_men",
        "restroomsMenL": "l_restrooms_men", "restroomsWomenL": "l_restrooms_women",
    }
    for alias, nid in aliases.items():
        subgraph.registerRoomAlias(alias, nid)

    return subgraph


buildingLSubgraph = buildBuildingLSubgraph()
