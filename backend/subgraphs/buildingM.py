"""
buildingM.py
================================================================================
BUILDING M (AUDITORIOS M101-M102, AULAS M201-M304 & POSGRADOS) SUBGRAPH
================================================================================
Multi-floor indoor child graph (Floors 1, 2, 3) built from official field GPS
measurements (coordenadas.txt) and room directory (buildings.txt).
Weighted, Directed, Non-Complete Graph G = (V, E, W).
================================================================================
"""

from backend.graph.directedGraph import Node
from backend.data.campusCategories import CampusCategory
from .buildingSubgraph import BuildingSubgraph, makeIndoorDistanceCalculator

_calcDist = makeIndoorDistanceCalculator(2.5)


def buildBuildingMSubgraph() -> BuildingSubgraph:
    subgraph = BuildingSubgraph(
        buildingId="buildingM",
        name="Edificio M (Auditorios M101-M102, Aulas M201-M304 & Posgrados)",
        code="M",
        floors=[1, 2, 3],
        macroNodeId="buildingM",
        entranceNodeIds=["m_stairs_from_b", "m_auditorium_101", "m_stairs_f1"],
        description="Edificio M: Auditorios M-101 y M-102, Dirección de Investigación y Gestión Ambiental, y Aulas M-201 a M-304."
    )

    # Floor 1
    subgraph.addNode(Node(
        nodeId="m_stairs_from_b",
        name="Acceso y Escaleras al Edificio M (desde Edificio B)",
        category=CampusCategory.STAIRS,
        xPercent=50.5, yPercent=48.8,
        latitude=12.108525, longitude=-86.257453,
        floorLevel=1, isOutdoorAccessPoint=True,
        portalKind="door", buildingId="buildingM"
    ))
    subgraph.addNode(Node(
        nodeId="m_auditorium_101",
        name="Auditorio M-101",
        category=CampusCategory.AUDITORIUM,
        xPercent=51.8, yPercent=50.5,
        latitude=12.108452, longitude=-86.257566,
        floorLevel=1, isOutdoorAccessPoint=True,
        portalKind="door", buildingId="buildingM"
    ))
    subgraph.addNode(Node(
        nodeId="m_auditorium_102",
        name="Auditorio M-102",
        category=CampusCategory.AUDITORIUM,
        xPercent=52.5, yPercent=51.2,
        latitude=12.108439, longitude=-86.257594,
        floorLevel=1, isOutdoorAccessPoint=False,
        buildingId="buildingM"
    ))
    subgraph.addNode(Node(
        nodeId="m_fountain_f1",
        name="Bebedero de Agua (Edificio M)",
        category=CampusCategory.DRINKING_FOUNTAIN,
        xPercent=52.0, yPercent=52.0,
        latitude=12.108426, longitude=-86.257560,
        floorLevel=1, isOutdoorAccessPoint=False,
        buildingId="buildingM"
    ))
    subgraph.addNode(Node(
        nodeId="m_restrooms_f1",
        name="Servicios Sanitarios Edificio M (Hombres, Mujeres e Inclusivos)",
        category=CampusCategory.RESTROOM,
        xPercent=51.5, yPercent=52.8,
        latitude=12.108366, longitude=-86.257520,
        floorLevel=1, isOutdoorAccessPoint=False,
        buildingId="buildingM"
    ))
    subgraph.addNode(Node(
        nodeId="m_research_env_office",
        name="Dirección de Investigación, Extensión Universitaria y Gestión Ambiental",
        category=CampusCategory.ADMINISTRATIVE,
        xPercent=52.0, yPercent=53.5,
        latitude=12.108331, longitude=-86.257559,
        floorLevel=1, isOutdoorAccessPoint=False,
        buildingId="buildingM"
    ))
    subgraph.addNode(Node(
        nodeId="m_stairs_f1",
        name="Escaleras Principales Edificio M (Piso 1)",
        category=CampusCategory.STAIRS,
        xPercent=52.8, yPercent=51.5,
        latitude=12.108447, longitude=-86.257612,
        floorLevel=1, isOutdoorAccessPoint=True,
        portalKind="stairs", buildingId="buildingM"
    ))

    # Floor 2
    subgraph.addNode(Node(
        nodeId="m_stairs_f2",
        name="Escaleras Edificio M (Piso 2)",
        category=CampusCategory.STAIRS,
        xPercent=52.8, yPercent=51.5,
        latitude=12.108447, longitude=-86.257612,
        floorLevel=2, isOutdoorAccessPoint=False,
        portalKind="stairs", buildingId="buildingM"
    ))
    subgraph.addNode(Node(
        nodeId="m_room_201_202",
        name="Aulas M-201 y M-202",
        category=CampusCategory.CLASSROOM,
        xPercent=52.2, yPercent=50.5,
        latitude=12.108402, longitude=-86.257582,
        floorLevel=2, isOutdoorAccessPoint=False,
        buildingId="buildingM"
    ))
    subgraph.addNode(Node(
        nodeId="m_room_203_204",
        name="Aulas M-203 y M-204",
        category=CampusCategory.CLASSROOM,
        xPercent=52.0, yPercent=52.0,
        latitude=12.108437, longitude=-86.257556,
        floorLevel=2, isOutdoorAccessPoint=False,
        buildingId="buildingM"
    ))

    # Floor 3
    subgraph.addNode(Node(
        nodeId="m_stairs_f3",
        name="Escaleras Edificio M (Piso 3)",
        category=CampusCategory.STAIRS,
        xPercent=52.8, yPercent=51.5,
        latitude=12.108447, longitude=-86.257612,
        floorLevel=3, isOutdoorAccessPoint=False,
        portalKind="stairs", buildingId="buildingM"
    ))
    subgraph.addNode(Node(
        nodeId="m_room_301_302",
        name="Aulas M-301 y M-302",
        category=CampusCategory.CLASSROOM,
        xPercent=52.5, yPercent=50.5,
        latitude=12.108493, longitude=-86.257603,
        floorLevel=3, isOutdoorAccessPoint=False,
        buildingId="buildingM"
    ))
    subgraph.addNode(Node(
        nodeId="m_room_303_304",
        name="Aulas M-303 y M-304",
        category=CampusCategory.CLASSROOM,
        xPercent=52.0, yPercent=52.0,
        latitude=12.108450, longitude=-86.257575,
        floorLevel=3, isOutdoorAccessPoint=False,
        buildingId="buildingM"
    ))

    f1Edges = [
        ("m_stairs_from_b", "m_auditorium_101"),
        ("m_auditorium_101", "m_auditorium_102"),
        ("m_auditorium_102", "m_stairs_f1"),
        ("m_auditorium_101", "m_fountain_f1"),
        ("m_fountain_f1", "m_restrooms_f1"),
        ("m_restrooms_f1", "m_research_env_office"),
        ("m_fountain_f1", "m_stairs_f1"),
    ]
    for u, v in f1Edges:
        nU, nV = subgraph.getNode(u), subgraph.getNode(v)
        subgraph.addBidirectionalCorridor(u, v, _calcDist(nU.latitude, nU.longitude, nV.latitude, nV.longitude), isAccessible=True)

    subgraph.addVerticalConnection("m_stairs_f1", "m_stairs_f2", distanceMeters=11.0, isAccessible=False)
    subgraph.addVerticalConnection("m_stairs_f2", "m_stairs_f3", distanceMeters=11.0, isAccessible=False)

    f2Edges = [
        ("m_stairs_f2", "m_room_201_202"),
        ("m_stairs_f2", "m_room_203_204"),
        ("m_room_201_202", "m_room_203_204"),
    ]
    for u, v in f2Edges:
        nU, nV = subgraph.getNode(u), subgraph.getNode(v)
        subgraph.addBidirectionalCorridor(u, v, _calcDist(nU.latitude, nU.longitude, nV.latitude, nV.longitude), isAccessible=True)

    f3Edges = [
        ("m_stairs_f3", "m_room_301_302"),
        ("m_stairs_f3", "m_room_303_304"),
        ("m_room_301_302", "m_room_303_304"),
    ]
    for u, v in f3Edges:
        nU, nV = subgraph.getNode(u), subgraph.getNode(v)
        subgraph.addBidirectionalCorridor(u, v, _calcDist(nU.latitude, nU.longitude, nV.latitude, nV.longitude), isAccessible=True)

    aliases = {
        "m101": "m_auditorium_101", "auditorio m101": "m_auditorium_101", "auditoriumM101": "m_auditorium_101",
        "m102": "m_auditorium_102", "auditorio m102": "m_auditorium_102", "auditoriumM102": "m_auditorium_102",
        "gestion ambiental": "m_research_env_office", "environmentalDirectorateM": "m_research_env_office",
        "direccion de gestion ambiental y energetica": "m_research_env_office",
        "investigacion": "m_research_env_office", "researchExtensionM": "m_research_env_office",
        "extension universitaria": "m_research_env_office",
        "direccion investigacion y extension universitaria": "m_research_env_office",
        "baños m": "m_restrooms_f1", "bebedero m": "m_fountain_f1", "drinkingFountainM1": "m_fountain_f1",
        "m201": "m_room_201_202", "classroomM201": "m_room_201_202",
        "m202": "m_room_201_202", "classroomM202": "m_room_201_202",
        "m203": "m_room_203_204", "classroomM203": "m_room_203_204",
        "m204": "m_room_203_204", "classroomM204": "m_room_203_204",
        "m301": "m_room_301_302", "classroomM301": "m_room_301_302",
        "m302": "m_room_301_302", "classroomM302": "m_room_301_302",
        "m303": "m_room_303_304", "classroomM303": "m_room_303_304",
        "m304": "m_room_303_304", "classroomM304": "m_room_303_304",
    }
    for alias, nid in aliases.items():
        subgraph.registerRoomAlias(alias, nid)

    return subgraph


buildingMSubgraph = buildBuildingMSubgraph()
