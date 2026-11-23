"""
buildingB.py
================================================================================
BUILDING B (AULAS B101-B210, FARMACIA & FOTOCOPIAS) SUBGRAPH / CHILD GRAPH
================================================================================
Multi-floor indoor child graph (Floors 1 & 2) built from official field GPS
measurements (coordenadas.txt) and room directory (buildings.txt).
Weighted, Directed, Non-Complete Graph G = (V, E, W).
================================================================================
"""

from backend.graph.directedGraph import Node
from backend.data.campusCategories import CampusCategory
from backend.graph.geoUtils import CampusGeoUtils
from .buildingSubgraph import BuildingSubgraph


def _calcDist(lat1: float, lng1: float, lat2: float, lng2: float, minDist: float = 2.5) -> float:
    d = CampusGeoUtils.calculateHaversineDistance(lat1, lng1, lat2, lng2)
    return max(minDist, round(d, 1))


def buildBuildingBSubgraph() -> BuildingSubgraph:
    subgraph = BuildingSubgraph(
        buildingId="buildingB",
        name="Edificio B (Aulas B101-B210 & Farmacia)",
        code="B",
        floors=[1, 2],
        macroNodeId="buildingB",
        entranceNodeIds=["b_room_101_pharmacy", "b_fountain_bc", "b_stairs_f1"],
        description="Edificio B: Farmacia del Valle, Aulas B101-B109 (Piso 1), B201-B210 (Piso 2), bebederos, baños y fotocopias."
    )

    # =========================================================================
    # FLOOR 1 (PRIMER PISO)
    # =========================================================================
    subgraph.addNode(Node(
        nodeId="b_room_101_pharmacy",
        name="Aula B-101 y Módulo Comercial 1 (Farmacia del Valle)",
        category=CampusCategory.CLASSROOM,
        xPercent=28.5, yPercent=54.0,
        latitude=12.108563, longitude=-86.256783,
        floorLevel=1, isOutdoorAccessPoint=True,
        portalKind="door", buildingId="buildingB"
    ))
    subgraph.addNode(Node(
        nodeId="b_room_102",
        name="Aula B-102",
        category=CampusCategory.CLASSROOM,
        xPercent=31.0, yPercent=54.0,
        latitude=12.108574, longitude=-86.256820,
        floorLevel=1, isOutdoorAccessPoint=False,
        buildingId="buildingB"
    ))
    subgraph.addNode(Node(
        nodeId="b_room_103_104",
        name="Aulas B-103 y B-104",
        category=CampusCategory.CLASSROOM,
        xPercent=33.5, yPercent=54.0,
        latitude=12.108585, longitude=-86.256858,
        floorLevel=1, isOutdoorAccessPoint=False,
        buildingId="buildingB"
    ))
    subgraph.addNode(Node(
        nodeId="b_room_105_106",
        name="Aulas B-105 y B-106",
        category=CampusCategory.CLASSROOM,
        xPercent=36.5, yPercent=54.0,
        latitude=12.108568, longitude=-86.256991,
        floorLevel=1, isOutdoorAccessPoint=False,
        buildingId="buildingB"
    ))
    subgraph.addNode(Node(
        nodeId="b_fountain_bc",
        name="Bebedero de Agua (Conexión Edificio B y C)",
        category=CampusCategory.DRINKING_FOUNTAIN,
        xPercent=38.0, yPercent=52.5,
        latitude=12.108545, longitude=-86.257057,
        floorLevel=1, isOutdoorAccessPoint=True,
        portalKind="corridor", buildingId="buildingB"
    ))
    subgraph.addNode(Node(
        nodeId="b_room_107",
        name="Aula B-107",
        category=CampusCategory.CLASSROOM,
        xPercent=39.5, yPercent=54.0,
        latitude=12.108610, longitude=-86.257099,
        floorLevel=1, isOutdoorAccessPoint=False,
        buildingId="buildingB"
    ))
    subgraph.addNode(Node(
        nodeId="b_room_108_109",
        name="Aulas B-108 y B-109",
        category=CampusCategory.CLASSROOM,
        xPercent=42.0, yPercent=54.0,
        latitude=12.108575, longitude=-86.257225,
        floorLevel=1, isOutdoorAccessPoint=False,
        buildingId="buildingB"
    ))
    subgraph.addNode(Node(
        nodeId="b_stairs_f1",
        name="Escaleras al Segundo Piso (Edificio B - Piso 1)",
        category=CampusCategory.STAIRS,
        xPercent=43.5, yPercent=54.0,
        latitude=12.108517, longitude=-86.257256,
        floorLevel=1, isOutdoorAccessPoint=True,
        portalKind="stairs", buildingId="buildingB"
    ))
    subgraph.addNode(Node(
        nodeId="b_restrooms_fountain_f1",
        name="Servicios Sanitarios, Bebedero y Fotocopias (Edificio B)",
        category=CampusCategory.RESTROOM,
        xPercent=44.5, yPercent=54.0,
        latitude=12.108590, longitude=-86.257332,
        floorLevel=1, isOutdoorAccessPoint=False,
        buildingId="buildingB"
    ))

    # =========================================================================
    # FLOOR 2 (SEGUNDO PISO)
    # =========================================================================
    subgraph.addNode(Node(
        nodeId="b_room_201",
        name="Aula B-201",
        category=CampusCategory.CLASSROOM,
        xPercent=28.5, yPercent=54.0,
        latitude=12.108556, longitude=-86.256730,
        floorLevel=2, isOutdoorAccessPoint=False,
        buildingId="buildingB"
    ))
    subgraph.addNode(Node(
        nodeId="b_room_202_203",
        name="Aulas B-202 y B-203",
        category=CampusCategory.CLASSROOM,
        xPercent=31.0, yPercent=54.0,
        latitude=12.108527, longitude=-86.256795,
        floorLevel=2, isOutdoorAccessPoint=False,
        buildingId="buildingB"
    ))
    subgraph.addNode(Node(
        nodeId="b_room_204_205",
        name="Aulas B-204 y B-205",
        category=CampusCategory.CLASSROOM,
        xPercent=33.5, yPercent=54.0,
        latitude=12.108552, longitude=-86.256826,
        floorLevel=2, isOutdoorAccessPoint=False,
        buildingId="buildingB"
    ))
    subgraph.addNode(Node(
        nodeId="b_room_206",
        name="Aula B-206",
        category=CampusCategory.CLASSROOM,
        xPercent=36.5, yPercent=54.0,
        latitude=12.108558, longitude=-86.256985,
        floorLevel=2, isOutdoorAccessPoint=False,
        buildingId="buildingB"
    ))
    subgraph.addNode(Node(
        nodeId="b_room_207_208",
        name="Aulas B-207 y B-208",
        category=CampusCategory.CLASSROOM,
        xPercent=40.0, yPercent=54.0,
        latitude=12.108507, longitude=-86.257117,
        floorLevel=2, isOutdoorAccessPoint=False,
        buildingId="buildingB"
    ))
    subgraph.addNode(Node(
        nodeId="b_room_209_210",
        name="Aulas B-209 y B-210",
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
        ("b_room_101_pharmacy", "b_room_102"),
        ("b_room_102", "b_room_103_104"),
        ("b_room_103_104", "b_room_105_106"),
        ("b_room_105_106", "b_fountain_bc"),
        ("b_fountain_bc", "b_room_107"),
        ("b_room_107", "b_room_108_109"),
        ("b_room_108_109", "b_stairs_f1"),
        ("b_stairs_f1", "b_restrooms_fountain_f1"),
    ]
    for u, v in f1Seq:
        nU, nV = subgraph.getNode(u), subgraph.getNode(v)
        subgraph.addBidirectionalCorridor(u, v, _calcDist(nU.latitude, nU.longitude, nV.latitude, nV.longitude), isAccessible=True)

    # Vertical Stairs F1 <-> F2
    subgraph.addVerticalConnection("b_stairs_f1", "b_stairs_f2", distanceMeters=11.0, isAccessible=False)

    f2Seq = [
        ("b_room_201", "b_room_202_203"),
        ("b_room_202_203", "b_room_204_205"),
        ("b_room_204_205", "b_room_206"),
        ("b_room_206", "b_room_207_208"),
        ("b_room_207_208", "b_room_209_210"),
        ("b_room_209_210", "b_stairs_f2"),
    ]
    for u, v in f2Seq:
        nU, nV = subgraph.getNode(u), subgraph.getNode(v)
        subgraph.addBidirectionalCorridor(u, v, _calcDist(nU.latitude, nU.longitude, nV.latitude, nV.longitude), isAccessible=True)

    aliases = {
        "b101": "b_room_101_pharmacy", "classroomB101": "b_room_101_pharmacy",
        "farmacia": "b_room_101_pharmacy", "pharmacyB": "b_room_101_pharmacy", "farmacia del valle": "b_room_101_pharmacy",
        "b102": "b_room_102", "classroomB102": "b_room_102",
        "b103": "b_room_103_104", "classroomB103": "b_room_103_104",
        "b104": "b_room_103_104", "classroomB104": "b_room_103_104",
        "b105": "b_room_105_106", "classroomB105": "b_room_105_106",
        "b106": "b_room_105_106", "classroomB106": "b_room_105_106",
        "bebedero entre b y c": "b_fountain_bc", "drinkingFountainBetweenBC": "b_fountain_bc",
        "b107": "b_room_107", "classroomB107": "b_room_107",
        "b108": "b_room_108_109", "classroomB108": "b_room_108_109",
        "b109": "b_room_108_109", "classroomB109": "b_room_108_109",
        "drinkingFountainB1": "b_restrooms_fountain_f1", "restroomsMenB1": "b_restrooms_fountain_f1",
        "restroomsWomenB1": "b_restrooms_fountain_f1", "photocopyShopB": "b_restrooms_fountain_f1",
        "fotocopias": "b_restrooms_fountain_f1", "baños b": "b_restrooms_fountain_f1",
        "b201": "b_room_201", "classroomB201": "b_room_201",
        "b202": "b_room_202_203", "classroomB202": "b_room_202_203",
        "b203": "b_room_202_203", "classroomB203": "b_room_202_203",
        "b204": "b_room_204_205", "classroomB204": "b_room_204_205",
        "b205": "b_room_204_205", "classroomB205": "b_room_204_205",
        "b206": "b_room_206", "classroomB206": "b_room_206",
        "b207": "b_room_207_208", "b208": "b_room_207_208",
        "b209": "b_room_209_210", "b210": "b_room_209_210",
    }
    for alias, nid in aliases.items():
        subgraph.registerRoomAlias(alias, nid)

    return subgraph


buildingBSubgraph = buildBuildingBSubgraph()
