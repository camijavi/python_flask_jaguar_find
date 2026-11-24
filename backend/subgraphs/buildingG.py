"""
buildingG.py
================================================================================
BUILDING G (DERECHO FCJHRI, LANGUAGE CENTER & AUDITORIO CENTRAL) SUBGRAPH
================================================================================
Multi-floor indoor child graph (Floors 1 & 2) built from official field GPS
measurements (coordenadas.txt) and room directory (buildings.txt).
Weighted, Directed, Non-Complete Graph G = (V, E, W).
================================================================================
"""

from backend.graph.directedGraph import Node
from backend.data.campusCategories import CampusCategory
from .buildingSubgraph import BuildingSubgraph, makeIndoorDistanceCalculator

_calcDist = makeIndoorDistanceCalculator(2.5)


def buildBuildingGSubgraph() -> BuildingSubgraph:
    subgraph = BuildingSubgraph(
        buildingId="buildingG",
        name="Edificio G (Derecho FCJHRI, Language Center & Auditorio Central)",
        code="G",
        floors=[1, 2],
        macroNodeId="buildingG",
        entranceNodeIds=["g_fcjhri", "g_language_uam_college", "g_ramp_gf_auditorium"],
        description="Edificio G: Facultad de Derecho (FCJHRI), Centro de Mediación, Language Center, UAM College, Relaciones Internacionales y Auditorio Central Rubén Darío."
    )

    # Floor 1
    subgraph.addNode(Node(
        nodeId="g_fcjhri",
        name="Facultad de Ciencias Jurídicas, Humanidades y Relaciones Internacionales (FCJHRI) y Centro de Mediación",
        category=CampusCategory.FACULTY,
        xPercent=49.5, yPercent=59.0,
        latitude=12.108630, longitude=-86.257479,
        floorLevel=1, isOutdoorAccessPoint=True,
        portalKind="door", buildingId="buildingG"
    ))
    subgraph.addNode(Node(
        nodeId="g_restrooms_f1",
        name="Servicios Sanitarios Edificio G (Mixtos e Inclusivos)",
        category=CampusCategory.RESTROOM,
        xPercent=50.2, yPercent=59.8,
        latitude=12.108652, longitude=-86.257520,
        floorLevel=1, isOutdoorAccessPoint=False,
        buildingId="buildingG"
    ))
    subgraph.addNode(Node(
        nodeId="g_stairs_f1",
        name="Escaleras Edificio G (Piso 1)",
        category=CampusCategory.STAIRS,
        xPercent=50.4, yPercent=60.0,
        latitude=12.108652, longitude=-86.257520,
        floorLevel=1, isOutdoorAccessPoint=False,
        portalKind="stairs", buildingId="buildingG"
    ))
    subgraph.addNode(Node(
        nodeId="g_language_uam_college",
        name="Language Center, UAM College, Relaciones Internacionales y Mapa UAM",
        category=CampusCategory.FACULTY,
        xPercent=50.5, yPercent=61.5,
        latitude=12.108779, longitude=-86.257498,
        floorLevel=1, isOutdoorAccessPoint=True,
        portalKind="door", buildingId="buildingG"
    ))
    subgraph.addNode(Node(
        nodeId="g_ramp_gf_auditorium",
        name="Rampa y Escaleras entre G y F (Acceso Auditorio Central)",
        category=CampusCategory.ACCESSIBLE_RAMP,
        xPercent=49.0, yPercent=62.5,
        latitude=12.108801, longitude=-86.257410,
        floorLevel=1, isOutdoorAccessPoint=True,
        portalKind="ramp", buildingId="buildingG"
    ))

    # Floor 2
    subgraph.addNode(Node(
        nodeId="g_stairs_f2",
        name="Escaleras Edificio G (Piso 2)",
        category=CampusCategory.STAIRS,
        xPercent=50.4, yPercent=60.0,
        latitude=12.108652, longitude=-86.257520,
        floorLevel=2, isOutdoorAccessPoint=False,
        portalKind="stairs", buildingId="buildingG"
    ))
    subgraph.addNode(Node(
        nodeId="g_auditorium_central",
        name="Auditorio Central Rubén Darío (Piso 2)",
        category=CampusCategory.AUDITORIUM,
        xPercent=51.0, yPercent=60.2,
        latitude=12.108695, longitude=-86.257600,
        floorLevel=2, isOutdoorAccessPoint=False,
        buildingId="buildingG"
    ))

    # Corridors F1
    f1Edges = [
        ("g_fcjhri", "g_restrooms_f1"),
        ("g_restrooms_f1", "g_stairs_f1"),
        ("g_stairs_f1", "g_language_uam_college"),
        ("g_language_uam_college", "g_ramp_gf_auditorium"),
    ]
    for u, v in f1Edges:
        nU, nV = subgraph.getNode(u), subgraph.getNode(v)
        subgraph.addBidirectionalCorridor(u, v, _calcDist(nU.latitude, nU.longitude, nV.latitude, nV.longitude), isAccessible=True)

    # Vertical Stairs F1 <-> F2
    subgraph.addVerticalConnection("g_stairs_f1", "g_stairs_f2", distanceMeters=11.0, isAccessible=False)

    # Floor 2
    dAud = _calcDist(12.108652, -86.257520, 12.108695, -86.257600, 6.0)
    subgraph.addBidirectionalCorridor("g_stairs_f2", "g_auditorium_central", dAud, isAccessible=True)

    aliases = {
        "fcjhri": "g_fcjhri", "derecho": "g_fcjhri", "auditorio fcjhri": "g_fcjhri",
        "centro de mediacion": "g_fcjhri", "mediacion y arbitraje": "g_fcjhri",
        "language center": "g_language_uam_college", "uam college": "g_language_uam_college",
        "relaciones internacionales": "g_language_uam_college", "internacionalizacion": "g_language_uam_college",
        "auditorio central": "g_auditorium_central", "ruben dario": "g_auditorium_central",
        "auditorio ruben dario": "g_auditorium_central", "baños g": "g_restrooms_f1",
    }
    for alias, nid in aliases.items():
        subgraph.registerRoomAlias(alias, nid)

    return subgraph


buildingGSubgraph = buildBuildingGSubgraph()
