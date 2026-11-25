"""
buildingM.py
================================================================================
BUILDING M (AUDITORIOS M101-M102, AULAS M201-M304 & POSGRADOS) SUBGRAPH
================================================================================
Multi-floor indoor child graph (Floors 1, 2, 3) built strictly from official UAM
room directory (buildings.txt) and field GPS measurements (coordenadas.txt).
Enforces exact ordering and non-hyphenated room codes (M101, M201, M301).
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
        description="Edificio M: Auditorios M101 y M102, Dirección de Gestión Ambiental y Energética, Dirección de Investigación y Extensión Universitaria, Aula, Sanitarios, Bebedero, Aulas M201-M204 y M301-M304."
    )

    # =========================================================================
    # FLOOR 1 (PRIMER PISO) — Exact order from buildings.txt
    # =========================================================================
    subgraph.addNode(Node(
        nodeId="m_auditorium_101",
        name="Auditorio M101",
        category=CampusCategory.AUDITORIUM,
        xPercent=51.8, yPercent=50.5,
        latitude=12.108452, longitude=-86.257566,
        floorLevel=1, isOutdoorAccessPoint=True,
        portalKind="door", buildingId="buildingM"
    ))
    subgraph.addNode(Node(
        nodeId="m_auditorium_102",
        name="Auditorio M102",
        category=CampusCategory.AUDITORIUM,
        xPercent=52.5, yPercent=51.2,
        latitude=12.108439, longitude=-86.257594,
        floorLevel=1, isOutdoorAccessPoint=False,
        buildingId="buildingM"
    ))
    subgraph.addNode(Node(
        nodeId="m_env_directorate",
        name="Dirección de Gestión Ambiental y Energética",
        category=CampusCategory.ADMINISTRATIVE,
        xPercent=51.9, yPercent=53.5,
        latitude=12.108331, longitude=-86.257559,
        floorLevel=1, isOutdoorAccessPoint=False,
        buildingId="buildingM"
    ))
    subgraph.addNode(Node(
        nodeId="m_research_extension",
        name="Dirección Investigación y Extensión Universitaria",
        category=CampusCategory.ADMINISTRATIVE,
        xPercent=52.1, yPercent=53.5,
        latitude=12.108331, longitude=-86.257559,
        floorLevel=1, isOutdoorAccessPoint=False,
        buildingId="buildingM"
    ))
    subgraph.addNode(Node(
        nodeId="m_classroom_f1",
        name="Aula (Edificio M - Piso 1)",
        category=CampusCategory.CLASSROOM,
        xPercent=51.8, yPercent=52.4,
        latitude=12.108385, longitude=-86.257550,
        floorLevel=1, isOutdoorAccessPoint=False,
        buildingId="buildingM"
    ))
    subgraph.addNode(Node(
        nodeId="m_restrooms_men",
        name="Baños Hombres (Edificio M)",
        category=CampusCategory.RESTROOM,
        xPercent=51.4, yPercent=52.8,
        latitude=12.108366, longitude=-86.257520,
        floorLevel=1, isOutdoorAccessPoint=False,
        buildingId="buildingM"
    ))
    subgraph.addNode(Node(
        nodeId="m_restrooms_women",
        name="Baños Mujeres (Edificio M)",
        category=CampusCategory.RESTROOM,
        xPercent=51.6, yPercent=52.8,
        latitude=12.108366, longitude=-86.257520,
        floorLevel=1, isOutdoorAccessPoint=False,
        buildingId="buildingM"
    ))
    subgraph.addNode(Node(
        nodeId="m_restrooms_accessible",
        name="Servicios Mixtos Discapacitados (Edificio M)",
        category=CampusCategory.RESTROOM,
        xPercent=51.8, yPercent=52.8,
        latitude=12.108366, longitude=-86.257520,
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
        nodeId="m_stairs_from_b",
        name="Acceso y Escaleras al Edificio M (desde Edificio B)",
        category=CampusCategory.STAIRS,
        xPercent=50.5, yPercent=48.8,
        latitude=12.108525, longitude=-86.257453,
        floorLevel=1, isOutdoorAccessPoint=True,
        portalKind="door", buildingId="buildingM"
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

    # =========================================================================
    # FLOOR 2 (SEGUNDO PISO) — Exact left-to-right order (M201..M204)
    # =========================================================================
    subgraph.addNode(Node(
        nodeId="m_room_201",
        name="Aula M201",
        category=CampusCategory.CLASSROOM,
        xPercent=52.0, yPercent=50.5,
        latitude=12.108402, longitude=-86.257582,
        floorLevel=2, isOutdoorAccessPoint=False,
        buildingId="buildingM"
    ))
    subgraph.addNode(Node(
        nodeId="m_room_202",
        name="Aula M202",
        category=CampusCategory.CLASSROOM,
        xPercent=52.4, yPercent=50.5,
        latitude=12.108402, longitude=-86.257582,
        floorLevel=2, isOutdoorAccessPoint=False,
        buildingId="buildingM"
    ))
    subgraph.addNode(Node(
        nodeId="m_room_203",
        name="Aula M203",
        category=CampusCategory.CLASSROOM,
        xPercent=51.9, yPercent=52.0,
        latitude=12.108437, longitude=-86.257556,
        floorLevel=2, isOutdoorAccessPoint=False,
        buildingId="buildingM"
    ))
    subgraph.addNode(Node(
        nodeId="m_room_204",
        name="Aula M204",
        category=CampusCategory.CLASSROOM,
        xPercent=52.2, yPercent=52.0,
        latitude=12.108437, longitude=-86.257556,
        floorLevel=2, isOutdoorAccessPoint=False,
        buildingId="buildingM"
    ))
    subgraph.addNode(Node(
        nodeId="m_stairs_f2",
        name="Escaleras Edificio M (Piso 2)",
        category=CampusCategory.STAIRS,
        xPercent=52.8, yPercent=51.5,
        latitude=12.108447, longitude=-86.257612,
        floorLevel=2, isOutdoorAccessPoint=False,
        portalKind="stairs", buildingId="buildingM"
    ))

    # =========================================================================
    # FLOOR 3 (TERCER PISO) — Exact left-to-right order (M301..M304)
    # =========================================================================
    subgraph.addNode(Node(
        nodeId="m_room_301",
        name="Aula M301",
        category=CampusCategory.CLASSROOM,
        xPercent=52.3, yPercent=50.5,
        latitude=12.108493, longitude=-86.257603,
        floorLevel=3, isOutdoorAccessPoint=False,
        buildingId="buildingM"
    ))
    subgraph.addNode(Node(
        nodeId="m_room_302",
        name="Aula M302",
        category=CampusCategory.CLASSROOM,
        xPercent=52.7, yPercent=50.5,
        latitude=12.108493, longitude=-86.257603,
        floorLevel=3, isOutdoorAccessPoint=False,
        buildingId="buildingM"
    ))
    subgraph.addNode(Node(
        nodeId="m_room_303",
        name="Aula M303",
        category=CampusCategory.CLASSROOM,
        xPercent=51.9, yPercent=52.0,
        latitude=12.108450, longitude=-86.257575,
        floorLevel=3, isOutdoorAccessPoint=False,
        buildingId="buildingM"
    ))
    subgraph.addNode(Node(
        nodeId="m_room_304",
        name="Aula M304",
        category=CampusCategory.CLASSROOM,
        xPercent=52.2, yPercent=52.0,
        latitude=12.108450, longitude=-86.257575,
        floorLevel=3, isOutdoorAccessPoint=False,
        buildingId="buildingM"
    ))
    subgraph.addNode(Node(
        nodeId="m_stairs_f3",
        name="Escaleras Edificio M (Piso 3)",
        category=CampusCategory.STAIRS,
        xPercent=52.8, yPercent=51.5,
        latitude=12.108447, longitude=-86.257612,
        floorLevel=3, isOutdoorAccessPoint=False,
        portalKind="stairs", buildingId="buildingM"
    ))

    f1Edges = [
        ("m_stairs_from_b", "m_auditorium_101"),
        ("m_auditorium_101", "m_auditorium_102"),
        ("m_auditorium_102", "m_stairs_f1"),
        ("m_auditorium_101", "m_fountain_f1"),
        ("m_fountain_f1", "m_stairs_f1"),
        ("m_fountain_f1", "m_classroom_f1"),
        ("m_classroom_f1", "m_restrooms_men"),
        ("m_restrooms_men", "m_restrooms_women"),
        ("m_restrooms_women", "m_restrooms_accessible"),
        ("m_restrooms_men", "m_env_directorate"),
        ("m_env_directorate", "m_research_extension"),
    ]
    for u, v in f1Edges:
        nU, nV = subgraph.getNode(u), subgraph.getNode(v)
        subgraph.addBidirectionalCorridor(u, v, _calcDist(nU.latitude, nU.longitude, nV.latitude, nV.longitude), isAccessible=True)

    subgraph.addVerticalConnection("m_stairs_f1", "m_stairs_f2", distanceMeters=11.0, isAccessible=False)
    subgraph.addVerticalConnection("m_stairs_f2", "m_stairs_f3", distanceMeters=11.0, isAccessible=False)

    f2Edges = [
        ("m_stairs_f2", "m_room_201"),
        ("m_room_201", "m_room_202"),
        ("m_room_202", "m_room_203"),
        ("m_room_203", "m_room_204"),
        ("m_stairs_f2", "m_room_203"),
    ]
    for u, v in f2Edges:
        nU, nV = subgraph.getNode(u), subgraph.getNode(v)
        subgraph.addBidirectionalCorridor(u, v, _calcDist(nU.latitude, nU.longitude, nV.latitude, nV.longitude), isAccessible=True)

    f3Edges = [
        ("m_stairs_f3", "m_room_301"),
        ("m_room_301", "m_room_302"),
        ("m_room_302", "m_room_303"),
        ("m_room_303", "m_room_304"),
        ("m_stairs_f3", "m_room_303"),
    ]
    for u, v in f3Edges:
        nU, nV = subgraph.getNode(u), subgraph.getNode(v)
        subgraph.addBidirectionalCorridor(u, v, _calcDist(nU.latitude, nU.longitude, nV.latitude, nV.longitude), isAccessible=True)

    aliases = {
        "m101": "m_auditorium_101", "m-101": "m_auditorium_101", "auditorio m101": "m_auditorium_101", "auditoriumM101": "m_auditorium_101",
        "m102": "m_auditorium_102", "m-102": "m_auditorium_102", "auditorio m102": "m_auditorium_102", "auditoriumM102": "m_auditorium_102",
        "gestion ambiental": "m_env_directorate", "environmentalDirectorateM": "m_env_directorate",
        "direccion de gestion ambiental y energetica": "m_env_directorate", "m_research_env_office": "m_env_directorate",
        "investigacion": "m_research_extension", "researchExtensionM": "m_research_extension",
        "extension universitaria": "m_research_extension",
        "direccion investigacion y extension universitaria": "m_research_extension",
        "aula m": "m_classroom_f1", "classroomM1": "m_classroom_f1",
        "baños m": "m_restrooms_men", "banos m": "m_restrooms_men", "m_restrooms_f1": "m_restrooms_men",
        "restroomsMenM1": "m_restrooms_men", "restroomsWomenM1": "m_restrooms_women",
        "accessibleRestroomM1": "m_restrooms_accessible", "servicios mixtos discapacitados m": "m_restrooms_accessible",
        "bebedero m": "m_fountain_f1", "drinkingFountainM1": "m_fountain_f1",
        "m201": "m_room_201", "m-201": "m_room_201", "classroomM201": "m_room_201", "m_room_201_202": "m_room_201",
        "m202": "m_room_202", "m-202": "m_room_202", "classroomM202": "m_room_202",
        "m203": "m_room_203", "m-203": "m_room_203", "classroomM203": "m_room_203", "m_room_203_204": "m_room_203",
        "m204": "m_room_204", "m-204": "m_room_204", "classroomM204": "m_room_204",
        "m301": "m_room_301", "m-301": "m_room_301", "classroomM301": "m_room_301", "m_room_301_302": "m_room_301",
        "m302": "m_room_302", "m-302": "m_room_302", "classroomM302": "m_room_302",
        "m303": "m_room_303", "m-303": "m_room_303", "classroomM303": "m_room_303", "m_room_303_304": "m_room_303",
        "m304": "m_room_304", "m-304": "m_room_304", "classroomM304": "m_room_304",
    }
    for alias, nid in aliases.items():
        subgraph.registerRoomAlias(alias, nid)

    return subgraph


buildingMSubgraph = buildBuildingMSubgraph()
