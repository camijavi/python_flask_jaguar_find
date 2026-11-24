"""
buildingL.py
================================================================================
BUILDING L (CULTURA, MÚSICA, DUCHAS & ACCESO JAGUAR CENTER) SUBGRAPH
================================================================================
Single-floor indoor child graph built from official UAM field GPS measurements
(coordenadas.txt) and room directory (buildings.txt).
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
        description="Edificio L: Salón de Cultura, Aula de Música, Entrada a Jaguar Center, Duchas de Equipos (Home/Visitantes) y Servicios Sanitarios."
    )

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
        nodeId="l_jaguar_center_entry",
        name="Entrada a Jaguar Center por Edificio L",
        category=CampusCategory.SPORTS,
        xPercent=80.0, yPercent=72.0,
        latitude=12.109111, longitude=-86.258514,
        floorLevel=1, isOutdoorAccessPoint=True,
        portalKind="door", buildingId="buildingL"
    ))
    subgraph.addNode(Node(
        nodeId="l_duchas",
        name="Duchas de Equipos (Home izquierda, Visitantes derecha)",
        category=CampusCategory.SPORTS,
        xPercent=82.0, yPercent=69.0,
        latitude=12.108952, longitude=-86.258551,
        floorLevel=1, isOutdoorAccessPoint=False,
        buildingId="buildingL"
    ))
    subgraph.addNode(Node(
        nodeId="l_restrooms",
        name="Servicios Sanitarios Edificio L (Hombres y Mujeres)",
        category=CampusCategory.RESTROOM,
        xPercent=82.0, yPercent=66.5,
        latitude=12.108905, longitude=-86.258519,
        floorLevel=1, isOutdoorAccessPoint=False,
        buildingId="buildingL"
    ))

    edges = [
        ("l_jaguar_center_entry", "l_cultura_map"),
        ("l_cultura_map", "l_musica"),
        ("l_musica", "l_duchas"),
        ("l_duchas", "l_restrooms"),
    ]
    for u, v in edges:
        nU, nV = subgraph.getNode(u), subgraph.getNode(v)
        subgraph.addBidirectionalCorridor(u, v, _calcDist(nU.latitude, nU.longitude, nV.latitude, nV.longitude), isAccessible=True)

    aliases = {
        "salon de cultura": "l_cultura_map", "cultura": "l_cultura_map",
        "aula de musica": "l_musica", "musica": "l_musica",
        "duchas": "l_duchas", "duchas home": "l_duchas", "duchas visitantes": "l_duchas",
        "baños l": "l_restrooms", "banos l": "l_restrooms",
    }
    for alias, nid in aliases.items():
        subgraph.registerRoomAlias(alias, nid)

    return subgraph


buildingLSubgraph = buildBuildingLSubgraph()
