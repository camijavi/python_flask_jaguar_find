"""
buildingB.py
================================================================================
BUILDING B (AULAS B101-B210, FARMACIA & FOTOCOPIAS) SUBGRAPH / CHILD GRAPH
================================================================================
Multi-floor indoor child graph (Floors 1 & 2) built strictly from official UAM
room directory (buildings.txt) and field GPS measurements (coordenadas.txt).
Enforces exact left-to-right ordering (B101..B109, B201..B210) and non-hyphenated
nomenclature (B101, NOT B-101).
Weighted, Directed, Non-Complete Graph G = (V, E, W).
================================================================================
"""

from backend.graph.directedGraph import Node
from backend.data.campusCategories import CampusCategory
from .buildingSubgraph import BuildingSubgraph, makeIndoorDistanceCalculator

_calcDist = makeIndoorDistanceCalculator(2.5)


def buildBuildingBSubgraph() -> BuildingSubgraph:
    subgraph = BuildingSubgraph(
        buildingId="buildingB",
        name="Edificio B (Aulas B101-B210 & Farmacia)",
        code="B",
        floors=[1, 2],
        macroNodeId="buildingB",
        entranceNodeIds=["b_pharmacy", "b_room_101", "b_fountain_bc", "b_stairs_f1"],
        description="Edificio B: Módulo Comercial 1 (Farmacia), Aulas B101-B109 (Piso 1), B201-B210 (Piso 2), sanitarios, bebederos y fotocopias."
    )

    # =========================================================================
    # FLOOR 1 (PRIMER PISO) — Exact left-to-right order from buildings.txt
    # =========================================================================
    subgraph.addNode(Node(
        nodeId="b_pharmacy",
        name="Módulo Comercial 1 (Farmacia)",
        category=CampusCategory.ADMINISTRATIVE,
        xPercent=28.0, yPercent=54.0,
        latitude=12.108563, longitude=-86.256783,
        floorLevel=1, isOutdoorAccessPoint=True,
        portalKind="door", buildingId="buildingB"
    ))
    subgraph.addNode(Node(
        nodeId="b_room_101",
        name="Aula B101",
        category=CampusCategory.CLASSROOM,
        xPercent=29.0, yPercent=54.0,
        latitude=12.108563, longitude=-86.256783,
        floorLevel=1, isOutdoorAccessPoint=True,
        portalKind="door", buildingId="buildingB"
    ))
    subgraph.addNode(Node(
        nodeId="b_room_102",
        name="Aula B102",
        category=CampusCategory.CLASSROOM,
        xPercent=30.5, yPercent=54.0,
        latitude=12.108574, longitude=-86.256820,
        floorLevel=1, isOutdoorAccessPoint=False,
        buildingId="buildingB"
    ))
    subgraph.addNode(Node(
        nodeId="b_room_103",
        name="Aula B103",
        category=CampusCategory.CLASSROOM,
        xPercent=32.0, yPercent=54.0,
        latitude=12.108585, longitude=-86.256858,
        floorLevel=1, isOutdoorAccessPoint=False,
        buildingId="buildingB"
    ))
    subgraph.addNode(Node(
        nodeId="b_room_104",
        name="Aula B104",
        category=CampusCategory.CLASSROOM,
        xPercent=33.5, yPercent=54.0,
        latitude=12.108585, longitude=-86.256858,
        floorLevel=1, isOutdoorAccessPoint=False,
        buildingId="buildingB"
    ))
    subgraph.addNode(Node(
        nodeId="b_room_105",
        name="Aula B105",
        category=CampusCategory.CLASSROOM,
        xPercent=35.5, yPercent=54.0,
        latitude=12.108568, longitude=-86.256991,
        floorLevel=1, isOutdoorAccessPoint=False,
        buildingId="buildingB"
    ))
    subgraph.addNode(Node(
        nodeId="b_room_106",
        name="Aula B106",
        category=CampusCategory.CLASSROOM,
        xPercent=37.0, yPercent=54.0,
        latitude=12.108568, longitude=-86.256991,
        floorLevel=1, isOutdoorAccessPoint=False,
        buildingId="buildingB"
    ))
    subgraph.addNode(Node(
        nodeId="b_room_107",
        name="Aula B107",
        category=CampusCategory.CLASSROOM,
        xPercent=39.0, yPercent=54.0,
        latitude=12.108610, longitude=-86.257099,
        floorLevel=1, isOutdoorAccessPoint=False,
        buildingId="buildingB"
    ))
    subgraph.addNode(Node(
        nodeId="b_room_108",
        name="Aula B108",
        category=CampusCategory.CLASSROOM,
        xPercent=41.0, yPercent=54.0,
        latitude=12.108575, longitude=-86.257225,
        floorLevel=1, isOutdoorAccessPoint=False,
        buildingId="buildingB"
    ))
    subgraph.addNode(Node(
        nodeId="b_room_109",
        name="Aula B109",
        category=CampusCategory.CLASSROOM,
        xPercent=42.2, yPercent=54.0,
        latitude=12.108575, longitude=-86.257225,
        floorLevel=1, isOutdoorAccessPoint=False,
        buildingId="buildingB"
    ))
    subgraph.addNode(Node(
        nodeId="b_restrooms_men_f1",
        name="Servicios Sanitarios Hombres (Edificio B)",
        category=CampusCategory.RESTROOM,
        xPercent=43.8, yPercent=54.0,
        latitude=12.108590, longitude=-86.257332,
        floorLevel=1, isOutdoorAccessPoint=False,
        buildingId="buildingB"
    ))
    subgraph.addNode(Node(
        nodeId="b_fountain_f1",
        name="Bebedero de Agua (Edificio B)",
        category=CampusCategory.DRINKING_FOUNTAIN,
        xPercent=44.1, yPercent=54.0,
        latitude=12.108590, longitude=-86.257332,
        floorLevel=1, isOutdoorAccessPoint=False,
        buildingId="buildingB"
    ))
    subgraph.addNode(Node(
        nodeId="b_restrooms_women_f1",
        name="Servicios Sanitarios Mujeres (Edificio B)",
        category=CampusCategory.RESTROOM,
        xPercent=44.4, yPercent=54.0,
        latitude=12.108590, longitude=-86.257332,
        floorLevel=1, isOutdoorAccessPoint=False,
        buildingId="buildingB"
    ))
    subgraph.addNode(Node(
        nodeId="b_photocopy",
        name="Fotocopias (Edificio B)",
        category=CampusCategory.ADMINISTRATIVE,
        xPercent=44.8, yPercent=54.0,
        latitude=12.108590, longitude=-86.257332,
        floorLevel=1, isOutdoorAccessPoint=False,
        buildingId="buildingB"
    ))
    subgraph.addNode(Node(
        nodeId="b_fountain_bc",
        name="Bebedero de Agua (Entre Edificio C y B)",
        category=CampusCategory.DRINKING_FOUNTAIN,
        xPercent=38.0, yPercent=52.5,
        latitude=12.108545, longitude=-86.257057,
        floorLevel=1, isOutdoorAccessPoint=True,
        portalKind="corridor", buildingId="buildingB"
    ))
    subgraph.addNode(Node(
        nodeId="b_stairs_f1",
        name="Escaleras al Segundo Piso (Edificio B - Piso 1)",
        category=CampusCategory.STAIRS,
        xPercent=43.2, yPercent=54.0,
        latitude=12.108517, longitude=-86.257256,
        floorLevel=1, isOutdoorAccessPoint=True,
        portalKind="stairs", buildingId="buildingB"
    ))

    # =========================================================================
    # FLOOR 2 (SEGUNDO PISO) — Exact left-to-right order (B201..B210)
    # =========================================================================
    subgraph.addNode(Node(
        nodeId="b_room_201",
        name="Aula B201",
        category=CampusCategory.CLASSROOM,
        xPercent=28.5, yPercent=54.0,
        latitude=12.108556, longitude=-86.256730,
        floorLevel=2, isOutdoorAccessPoint=False,
        buildingId="buildingB"
    ))
    subgraph.addNode(Node(
        nodeId="b_room_202",
        name="Aula B202",
        category=CampusCategory.CLASSROOM,
        xPercent=30.0, yPercent=54.0,
        latitude=12.108527, longitude=-86.256795,
        floorLevel=2, isOutdoorAccessPoint=False,
        buildingId="buildingB"
    ))
    subgraph.addNode(Node(
        nodeId="b_room_203",
        name="Aula B203",
        category=CampusCategory.CLASSROOM,
        xPercent=31.5, yPercent=54.0,
        latitude=12.108527, longitude=-86.256795,
        floorLevel=2, isOutdoorAccessPoint=False,
        buildingId="buildingB"
    ))
    subgraph.addNode(Node(
        nodeId="b_room_204",
        name="Aula B204",
        category=CampusCategory.CLASSROOM,
        xPercent=33.0, yPercent=54.0,
        latitude=12.108552, longitude=-86.256826,
        floorLevel=2, isOutdoorAccessPoint=False,
        buildingId="buildingB"
    ))
    subgraph.addNode(Node(
        nodeId="b_room_205",
        name="Aula B205",
        category=CampusCategory.CLASSROOM,
        xPercent=34.5, yPercent=54.0,
        latitude=12.108552, longitude=-86.256826,
        floorLevel=2, isOutdoorAccessPoint=False,
        buildingId="buildingB"
    ))
    subgraph.addNode(Node(
        nodeId="b_room_206",
        name="Aula B206",
        category=CampusCategory.CLASSROOM,
        xPercent=36.5, yPercent=54.0,
        latitude=12.108558, longitude=-86.256985,
        floorLevel=2, isOutdoorAccessPoint=False,
        buildingId="buildingB"
    ))
    subgraph.addNode(Node(
        nodeId="b_room_207",
        name="Aula B207",
        category=CampusCategory.CLASSROOM,
        xPercent=38.5, yPercent=54.0,
        latitude=12.108507, longitude=-86.257117,
        floorLevel=2, isOutdoorAccessPoint=False,
        buildingId="buildingB"
    ))
    subgraph.addNode(Node(
        nodeId="b_room_208",
        name="Aula B208",
        category=CampusCategory.CLASSROOM,
        xPercent=40.0, yPercent=54.0,
        latitude=12.108507, longitude=-86.257117,
        floorLevel=2, isOutdoorAccessPoint=False,
        buildingId="buildingB"
    ))
    subgraph.addNode(Node(
        nodeId="b_room_209",
        name="Aula B209",
        category=CampusCategory.CLASSROOM,
        xPercent=41.8, yPercent=54.0,
        latitude=12.108525, longitude=-86.257271,
        floorLevel=2, isOutdoorAccessPoint=False,
        buildingId="buildingB"
    ))
    subgraph.addNode(Node(
        nodeId="b_room_210",
        name="Aula B210",
        category=CampusCategory.CLASSROOM,
        xPercent=43.0, yPercent=54.0,
        latitude=12.108525, longitude=-86.257271,
        floorLevel=2, isOutdoorAccessPoint=False,
        buildingId="buildingB"
    ))
    subgraph.addNode(Node(
        nodeId="b_stairs_f2",
        name="Escaleras del Segundo Piso (Edificio B)",
        category=CampusCategory.STAIRS,
        xPercent=43.5, yPercent=54.0,
        latitude=12.108517, longitude=-86.257256,
        floorLevel=2, isOutdoorAccessPoint=False,
        portalKind="stairs", buildingId="buildingB"
    ))

    # =========================================================================
    # DIRECTED WEIGHTED CORRIDORS (SPARSE, NON-COMPLETE)
    # =========================================================================
    f1Seq = [
        ("b_pharmacy", "b_room_101"),
        ("b_room_101", "b_room_102"),
        ("b_room_102", "b_room_103"),
        ("b_room_103", "b_room_104"),
        ("b_room_104", "b_room_105"),
        ("b_room_105", "b_room_106"),
        ("b_room_106", "b_fountain_bc"),
        ("b_fountain_bc", "b_room_107"),
        ("b_room_107", "b_room_108"),
        ("b_room_108", "b_room_109"),
        ("b_room_109", "b_stairs_f1"),
        ("b_stairs_f1", "b_restrooms_men_f1"),
        ("b_restrooms_men_f1", "b_fountain_f1"),
        ("b_fountain_f1", "b_restrooms_women_f1"),
        ("b_restrooms_women_f1", "b_photocopy"),
    ]
    for u, v in f1Seq:
        nU, nV = subgraph.getNode(u), subgraph.getNode(v)
        subgraph.addBidirectionalCorridor(u, v, _calcDist(nU.latitude, nU.longitude, nV.latitude, nV.longitude), isAccessible=True)

    # Vertical Stairs F1 <-> F2
    subgraph.addVerticalConnection("b_stairs_f1", "b_stairs_f2", distanceMeters=11.0, isAccessible=False)

    f2Seq = [
        ("b_room_201", "b_room_202"),
        ("b_room_202", "b_room_203"),
        ("b_room_203", "b_room_204"),
        ("b_room_204", "b_room_205"),
        ("b_room_205", "b_room_206"),
        ("b_room_206", "b_room_207"),
        ("b_room_207", "b_room_208"),
        ("b_room_208", "b_room_209"),
        ("b_room_209", "b_room_210"),
        ("b_room_210", "b_stairs_f2"),
    ]
    for u, v in f2Seq:
        nU, nV = subgraph.getNode(u), subgraph.getNode(v)
        subgraph.addBidirectionalCorridor(u, v, _calcDist(nU.latitude, nU.longitude, nV.latitude, nV.longitude), isAccessible=True)

    aliases = {
        "farmacia": "b_pharmacy", "pharmacyB": "b_pharmacy", "farmacia del valle": "b_pharmacy",
        "modulo comercial 1": "b_pharmacy", "b_room_101_pharmacy": "b_room_101",
        "b101": "b_room_101", "b-101": "b_room_101", "classroomB101": "b_room_101",
        "b102": "b_room_102", "b-102": "b_room_102", "classroomB102": "b_room_102",
        "b103": "b_room_103", "b-103": "b_room_103", "classroomB103": "b_room_103", "b_room_103_104": "b_room_103",
        "b104": "b_room_104", "b-104": "b_room_104", "classroomB104": "b_room_104",
        "b105": "b_room_105", "b-105": "b_room_105", "classroomB105": "b_room_105", "b_room_105_106": "b_room_105",
        "b106": "b_room_106", "b-106": "b_room_106", "classroomB106": "b_room_106",
        "bebedero entre b y c": "b_fountain_bc", "bebedero entre c y b": "b_fountain_bc",
        "drinkingFountainBetweenBC": "b_fountain_bc",
        "b107": "b_room_107", "b-107": "b_room_107", "classroomB107": "b_room_107",
        "b108": "b_room_108", "b-108": "b_room_108", "classroomB108": "b_room_108", "b_room_108_109": "b_room_108",
        "b109": "b_room_109", "b-109": "b_room_109", "classroomB109": "b_room_109",
        "restroomsMenB1": "b_restrooms_men_f1", "baños b": "b_restrooms_men_f1", "banos b": "b_restrooms_men_f1",
        "b_restrooms_fountain_f1": "b_restrooms_men_f1",
        "drinkingFountainB1": "b_fountain_f1", "bebedero b": "b_fountain_f1",
        "restroomsWomenB1": "b_restrooms_women_f1",
        "photocopyShopB": "b_photocopy", "fotocopias": "b_photocopy", "copias": "b_photocopy",
        "b201": "b_room_201", "b-201": "b_room_201", "classroomB201": "b_room_201",
        "b202": "b_room_202", "b-202": "b_room_202", "classroomB202": "b_room_202", "b_room_202_203": "b_room_202",
        "b203": "b_room_203", "b-203": "b_room_203", "classroomB203": "b_room_203",
        "b204": "b_room_204", "b-204": "b_room_204", "classroomB204": "b_room_204", "b_room_204_205": "b_room_204",
        "b205": "b_room_205", "b-205": "b_room_205", "classroomB205": "b_room_205",
        "b206": "b_room_206", "b-206": "b_room_206", "classroomB206": "b_room_206",
        "b207": "b_room_207", "b-207": "b_room_207", "classroomB207": "b_room_207", "b_room_207_208": "b_room_207",
        "b208": "b_room_208", "b-208": "b_room_208", "classroomB208": "b_room_208",
        "b209": "b_room_209", "b-209": "b_room_209", "classroomB209": "b_room_209", "b_room_209_210": "b_room_209",
        "b210": "b_room_210", "b-210": "b_room_210", "classroomB210": "b_room_210",
    }
    for alias, nid in aliases.items():
        subgraph.registerRoomAlias(alias, nid)

    return subgraph


buildingBSubgraph = buildBuildingBSubgraph()
