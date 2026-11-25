"""
buildingG.py
================================================================================
BUILDING G (DERECHO FCJHRI, LANGUAGE CENTER & AUDITORIO CENTRAL) SUBGRAPH
================================================================================
Multi-floor indoor child graph (Floors 1 & 2) built strictly from official UAM
room directory (buildings.txt) and field GPS measurements (coordenadas.txt).
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
        entranceNodeIds=["g_fcjhri", "g_language_center", "g_ramp_gf_auditorium"],
        description="Edificio G: FCJHRI, Auditorio FCJHRI, Centro de Mediación y Arbitraje, Language Center, UAM College, Relaciones Internacionales, Baños Mixtos/Inclusivos y Auditorio Central Rubén Darío."
    )

    # =========================================================================
    # FLOOR 1 (PRIMER PISO) — Exact order from buildings.txt
    # =========================================================================
    subgraph.addNode(Node(
        nodeId="g_fcjhri",
        name="Facultad de Ciencias Jurídicas, Humanidades y Relaciones Internacionales (FCJHRI)",
        category=CampusCategory.FACULTY,
        xPercent=49.5, yPercent=59.0,
        latitude=12.108630, longitude=-86.257479,
        floorLevel=1, isOutdoorAccessPoint=True,
        portalKind="door", buildingId="buildingG"
    ))
    subgraph.addNode(Node(
        nodeId="g_auditorium_fcjhri",
        name="Auditorio FCJHRI",
        category=CampusCategory.AUDITORIUM,
        xPercent=49.7, yPercent=59.2,
        latitude=12.108630, longitude=-86.257479,
        floorLevel=1, isOutdoorAccessPoint=False,
        buildingId="buildingG"
    ))
    subgraph.addNode(Node(
        nodeId="g_mediation_center",
        name="Centro de Mediación y Arbitraje",
        category=CampusCategory.ADMINISTRATIVE,
        xPercent=49.9, yPercent=59.4,
        latitude=12.108630, longitude=-86.257479,
        floorLevel=1, isOutdoorAccessPoint=False,
        buildingId="buildingG"
    ))
    subgraph.addNode(Node(
        nodeId="g_language_center",
        name="Language Center",
        category=CampusCategory.CLASSROOM,
        xPercent=50.5, yPercent=61.3,
        latitude=12.108779, longitude=-86.257498,
        floorLevel=1, isOutdoorAccessPoint=True,
        portalKind="door", buildingId="buildingG"
    ))
    subgraph.addNode(Node(
        nodeId="g_uam_college",
        name="UAM College",
        category=CampusCategory.FACULTY,
        xPercent=50.5, yPercent=61.6,
        latitude=12.108779, longitude=-86.257498,
        floorLevel=1, isOutdoorAccessPoint=False,
        buildingId="buildingG"
    ))
    subgraph.addNode(Node(
        nodeId="g_intl_relations",
        name="Dirección de Relaciones Internacionales e Internacionalización",
        category=CampusCategory.ADMINISTRATIVE,
        xPercent=50.5, yPercent=61.9,
        latitude=12.108779, longitude=-86.257498,
        floorLevel=1, isOutdoorAccessPoint=False,
        buildingId="buildingG"
    ))
    subgraph.addNode(Node(
        nodeId="g_restrooms_mixed",
        name="Baños Mixtos (Edificio G)",
        category=CampusCategory.RESTROOM,
        xPercent=50.2, yPercent=59.7,
        latitude=12.108652, longitude=-86.257520,
        floorLevel=1, isOutdoorAccessPoint=False,
        buildingId="buildingG"
    ))
    subgraph.addNode(Node(
        nodeId="g_restrooms_f1",
        name="Baños para Personas con Discapacidades Mixtos (Edificio G)",
        category=CampusCategory.RESTROOM,
        xPercent=50.3, yPercent=59.9,
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
        nodeId="g_ramp_gf_auditorium",
        name="Escaleras y Rampa entre G y F (Acceso Auditorio Central)",
        category=CampusCategory.ACCESSIBLE_RAMP,
        xPercent=49.0, yPercent=62.5,
        latitude=12.108801, longitude=-86.257410,
        floorLevel=1, isOutdoorAccessPoint=True,
        portalKind="ramp", buildingId="buildingG"
    ))

    # =========================================================================
    # FLOOR 2 (SEGUNDO PISO) — Exact order from buildings.txt
    # =========================================================================
    subgraph.addNode(Node(
        nodeId="g_auditorium_central",
        name="Auditorio Central / Auditorio Rubén Darío",
        category=CampusCategory.AUDITORIUM,
        xPercent=51.0, yPercent=60.2,
        latitude=12.108695, longitude=-86.257600,
        floorLevel=2, isOutdoorAccessPoint=False,
        buildingId="buildingG"
    ))
    subgraph.addNode(Node(
        nodeId="g_stairs_f2",
        name="Escaleras Edificio G (Piso 2)",
        category=CampusCategory.STAIRS,
        xPercent=50.4, yPercent=60.0,
        latitude=12.108652, longitude=-86.257520,
        floorLevel=2, isOutdoorAccessPoint=False,
        portalKind="stairs", buildingId="buildingG"
    ))

    # Corridors F1
    f1Edges = [
        ("g_fcjhri", "g_auditorium_fcjhri"),
        ("g_auditorium_fcjhri", "g_mediation_center"),
        ("g_mediation_center", "g_restrooms_mixed"),
        ("g_restrooms_mixed", "g_restrooms_f1"),
        ("g_restrooms_f1", "g_stairs_f1"),
        ("g_stairs_f1", "g_language_center"),
        ("g_language_center", "g_uam_college"),
        ("g_uam_college", "g_intl_relations"),
        ("g_intl_relations", "g_ramp_gf_auditorium"),
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
        "facultyLawG": "g_fcjhri", "fcjhri": "g_fcjhri", "derecho": "g_fcjhri",
        "auditoriumFcjhriG": "g_auditorium_fcjhri", "auditorio fcjhri": "g_auditorium_fcjhri",
        "mediationCenterG": "g_mediation_center", "centro de mediacion": "g_mediation_center",
        "mediacion y arbitraje": "g_mediation_center", "centro de mediacion y arbitraje": "g_mediation_center",
        "languageCenterG": "g_language_center", "language center": "g_language_center",
        "g_language_uam_college": "g_language_center",
        "uamCollegeG": "g_uam_college", "uam college": "g_uam_college",
        "intlRelationsG": "g_intl_relations", "relaciones internacionales": "g_intl_relations",
        "internacionalizacion": "g_intl_relations",
        "mixedRestroomG": "g_restrooms_mixed", "banos mixtos": "g_restrooms_mixed", "baños g": "g_restrooms_mixed",
        "accessibleRestroomG": "g_restrooms_f1", "banos para personas con discapacidades mixtos": "g_restrooms_f1",
        "auditoriumCentralG": "g_auditorium_central", "auditorio central": "g_auditorium_central",
        "ruben dario": "g_auditorium_central", "auditorio ruben dario": "g_auditorium_central",
    }
    for alias, nid in aliases.items():
        subgraph.registerRoomAlias(alias, nid)

    return subgraph


buildingGSubgraph = buildBuildingGSubgraph()
