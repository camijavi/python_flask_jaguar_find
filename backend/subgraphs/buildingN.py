"""
buildingN.py
================================================================================
BUILDING N (CLÍNICAS ODONTOLÓGICAS & FODO) SUBGRAPH — GATEWAY PATTERN
================================================================================
Follows official Rule 1 (GRAPH_MAPPING_RULES.md — Gateway Pattern):
Internal clinical, surgical, sterilization, and radiology suites route strictly
to Public Reception / Control Points with an automatic biosecurity accessNotice,
while modeling public exterior connectors (restrooms by Chilamates, access from
Building D, and stairs/walkways toward Building P).
Weighted, Directed, Non-Complete Graph G = (V, E, W).
================================================================================
"""

from backend.graph.directedGraph import Node
from backend.data.campusCategories import CampusCategory
from backend.graph.geoUtils import CampusGeoUtils
from .buildingSubgraph import BuildingSubgraph


def _calcDist(lat1: float, lng1: float, lat2: float, lng2: float, minDist: float = 3.0) -> float:
    d = CampusGeoUtils.calculateHaversineDistance(lat1, lng1, lat2, lng2)
    return max(minDist, round(d, 1))


def buildBuildingNSubgraph() -> BuildingSubgraph:
    bioNotice = (
        "Recepción de Clínicas Odontológicas (Edificio N). El ingreso a cubículos clínicos, "
        "quirófanos, esterilización y radiología requiere uniforme estéril y autorización docente."
    )
    subgraph = BuildingSubgraph(
        buildingId="buildingN",
        name="Edificio N (Clínicas Odontológicas & FODO)",
        code="N",
        floors=[1, 2],
        macroNodeId="buildingN",
        entranceNodeIds=["n_reception", "n_restrooms_chilamate", "n_access_from_d"],
        description="Edificio N: Recepción de Clínicas Odontológicas, Archivo/Caja, Sanitarios junto a Plaza Chilamates y Facultad de Odontología (FODO)."
    )

    # Floor 1 (Public Gateway Points)
    subgraph.addNode(Node(
        nodeId="n_access_from_d",
        name="Acceso hacia Clínicas Odontológicas (desde Lab Odontología Digital D)",
        category=CampusCategory.DENTAL_LAB,
        xPercent=35.0, yPercent=34.0,
        latitude=12.108000, longitude=-86.256842,
        floorLevel=1, isOutdoorAccessPoint=True,
        portalKind="door", buildingId="buildingN"
    ))
    subgraph.addNode(Node(
        nodeId="n_reception",
        name="Recepción de Clínicas Odontológicas y Archivo/Caja (Edificio N)",
        category=CampusCategory.DENTAL_LAB,
        xPercent=36.0, yPercent=33.5,
        latitude=12.107871, longitude=-86.256967,
        floorLevel=1, isOutdoorAccessPoint=True,
        accessLevel="restricted",
        accessNotice=bioNotice,
        portalKind="door", buildingId="buildingN"
    ))
    subgraph.addNode(Node(
        nodeId="n_restrooms_chilamate",
        name="Servicios Sanitarios Edificio N (junto a Plaza Chilamates)",
        category=CampusCategory.RESTROOM,
        xPercent=30.5, yPercent=30.5,
        latitude=12.107741, longitude=-86.256842,
        floorLevel=1, isOutdoorAccessPoint=True,
        portalKind="door", buildingId="buildingN"
    ))
    subgraph.addNode(Node(
        nodeId="n_stairs_to_p",
        name="Acceso Norte Edificio N hacia Parqueo y Edificio P",
        category=CampusCategory.STAIRS,
        xPercent=35.0, yPercent=26.2,
        latitude=12.107742, longitude=-86.257105,
        floorLevel=1, isOutdoorAccessPoint=True,
        portalKind="stairs", buildingId="buildingN"
    ))
    subgraph.addNode(Node(
        nodeId="n_stairs_f1",
        name="Escaleras hacia Facultad de Odontología (FODO - Piso 1)",
        category=CampusCategory.STAIRS,
        xPercent=36.2, yPercent=32.0,
        latitude=12.107871, longitude=-86.256967,
        floorLevel=1, isOutdoorAccessPoint=False,
        portalKind="stairs", buildingId="buildingN"
    ))

    # Floor 2 (FODO Gateway)
    subgraph.addNode(Node(
        nodeId="n_stairs_f2",
        name="Escaleras Edificio N (Piso 2)",
        category=CampusCategory.STAIRS,
        xPercent=36.2, yPercent=32.0,
        latitude=12.107871, longitude=-86.256967,
        floorLevel=2, isOutdoorAccessPoint=False,
        portalKind="stairs", buildingId="buildingN"
    ))
    subgraph.addNode(Node(
        nodeId="n_fodo_f2_reception",
        name="Facultad de Odontología (FODO) — Recepción Piso 2",
        category=CampusCategory.FACULTY,
        xPercent=36.5, yPercent=31.0,
        latitude=12.107871, longitude=-86.256967,
        floorLevel=2, isOutdoorAccessPoint=False,
        accessLevel="restricted",
        accessNotice=bioNotice,
        buildingId="buildingN"
    ))

    edges = [
        ("n_access_from_d", "n_reception"),
        ("n_reception", "n_restrooms_chilamate"),
        ("n_restrooms_chilamate", "n_stairs_to_p"),
        ("n_reception", "n_stairs_f1"),
    ]
    for u, v in edges:
        nU, nV = subgraph.getNode(u), subgraph.getNode(v)
        subgraph.addBidirectionalCorridor(u, v, _calcDist(nU.latitude, nU.longitude, nV.latitude, nV.longitude), isAccessible=True)

    subgraph.addVerticalConnection("n_stairs_f1", "n_stairs_f2", distanceMeters=11.0, isAccessible=False)
    subgraph.addBidirectionalCorridor("n_stairs_f2", "n_fodo_f2_reception", 5.0, isAccessible=True)

    # Gateway Pattern Aliases: all clinical / restricted terms route cleanly to Reception
    aliases = {
        "recepcion n": "n_reception", "clinicas odontologicas": "n_reception", "clinica odontologica": "n_reception",
        "quirofano": "n_reception", "quirofano 1": "n_reception", "quirofano 2": "n_reception",
        "esterilizacion": "n_reception", "radiologia": "n_reception", "tomografia": "n_reception",
        "clinica medica a": "n_reception", "clinica medica b": "n_reception", "clinica medica e": "n_reception",
        "proveeduria": "n_reception", "archivo caja": "n_reception", "oficina idea": "n_reception",
        "fabricacion digital": "n_reception", "baños n": "n_restrooms_chilamate",
        "banos chilamate": "n_restrooms_chilamate", "fodo": "n_fodo_f2_reception",
        "facultad de odontologia": "n_fodo_f2_reception", "revelado digital": "n_fodo_f2_reception",
    }
    for alias, nid in aliases.items():
        subgraph.registerRoomAlias(alias, nid)

    return subgraph


buildingNSubgraph = buildBuildingNSubgraph()
