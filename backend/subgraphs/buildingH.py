"""
buildingH.py
================================================================================
BUILDING H (LABORATORIOS DE MEDICINA H101-H207) SUBGRAPH / CHILD GRAPH
================================================================================
Multi-floor indoor child graph (Floors 1 & 2) built strictly from official UAM
room directory (buildings.txt) and field GPS measurements (coordenadas.txt).
Enforces exact left-to-right ordering (H101..H107 on Floor 1 with Oficina de
Supervisión de Laboratorios de Medicina; H201..H207 on Floor 2) and non-hyphenated
nomenclature (H101, NOT H-101).
Weighted, Directed, Non-Complete Graph G = (V, E, W).
================================================================================
"""

from backend.graph.directedGraph import Node
from backend.data.campusCategories import CampusCategory
from .buildingSubgraph import BuildingSubgraph, makeIndoorDistanceCalculator

_calcDist = makeIndoorDistanceCalculator(2.5)


def buildBuildingHSubgraph() -> BuildingSubgraph:
    subgraph = BuildingSubgraph(
        buildingId="buildingH",
        name="Edificio H (Laboratorios de Medicina)",
        code="H",
        floors=[1, 2],
        macroNodeId="buildingH",
        entranceNodeIds=["h_stairs_from_c", "h_restrooms_men_f1", "h_stairs_main_f1"],
        description="Edificio H: Baños, Laboratorios de Medicina H101-H107, Coordinación de Gestión de Calidad, Supervisión de Laboratorios (Piso 1) y Laboratorios H201-H207 (Piso 2)."
    )

    # =========================================================================
    # FLOOR 1 (PRIMER PISO) — Exact left-to-right order from buildings.txt
    # =========================================================================
    subgraph.addNode(Node(
        nodeId="h_restrooms_men_f1",
        name="Baños Hombres (Edificio H)",
        category=CampusCategory.RESTROOM,
        xPercent=51.9, yPercent=44.5,
        latitude=12.108255, longitude=-86.257537,
        floorLevel=1, isOutdoorAccessPoint=True,
        buildingId="buildingH"
    ))
    subgraph.addNode(Node(
        nodeId="h_restrooms_women_f1",
        name="Baños Mujeres (Edificio H)",
        category=CampusCategory.RESTROOM,
        xPercent=52.1, yPercent=44.5,
        latitude=12.108255, longitude=-86.257537,
        floorLevel=1, isOutdoorAccessPoint=False,
        buildingId="buildingH"
    ))
    subgraph.addNode(Node(
        nodeId="h_lab_101",
        name="Laboratorio de Medicina H101",
        category=CampusCategory.MEDICAL_LAB,
        xPercent=52.5, yPercent=44.5,
        latitude=12.108272, longitude=-86.257569,
        floorLevel=1, isOutdoorAccessPoint=False,
        buildingId="buildingH"
    ))
    subgraph.addNode(Node(
        nodeId="h_lab_102",
        name="Laboratorio de Medicina H102",
        category=CampusCategory.MEDICAL_LAB,
        xPercent=52.9, yPercent=44.2,
        latitude=12.108265, longitude=-86.257549,
        floorLevel=1, isOutdoorAccessPoint=False,
        buildingId="buildingH"
    ))
    subgraph.addNode(Node(
        nodeId="h_lab_103",
        name="Laboratorio de Medicina H103",
        category=CampusCategory.MEDICAL_LAB,
        xPercent=53.3, yPercent=44.2,
        latitude=12.108265, longitude=-86.257549,
        floorLevel=1, isOutdoorAccessPoint=False,
        buildingId="buildingH"
    ))
    subgraph.addNode(Node(
        nodeId="h_lab_104",
        name="Coordinación de Gestión de Calidad (Laboratorio H104)",
        category=CampusCategory.MEDICAL_LAB,
        xPercent=54.0, yPercent=43.8,
        latitude=12.108263, longitude=-86.257695,
        floorLevel=1, isOutdoorAccessPoint=False,
        buildingId="buildingH"
    ))
    subgraph.addNode(Node(
        nodeId="h_lab_coord_necroteca",
        name="Oficina de Supervisión de Laboratorios de Medicina (Necroteca)",
        category=CampusCategory.MEDICAL_LAB,
        xPercent=53.8, yPercent=45.0,
        latitude=12.108304, longitude=-86.257660,
        floorLevel=1, isOutdoorAccessPoint=False,
        accessLevel="restricted",
        accessNotice="Área de laboratorios médicos y necroteca. Requiere gabacha y autorización docente.",
        buildingId="buildingH"
    ))
    subgraph.addNode(Node(
        nodeId="h_lab_105",
        name="Laboratorio de Medicina H105",
        category=CampusCategory.MEDICAL_LAB,
        xPercent=55.5, yPercent=42.8,
        latitude=12.108200, longitude=-86.257812,
        floorLevel=1, isOutdoorAccessPoint=False,
        buildingId="buildingH"
    ))
    subgraph.addNode(Node(
        nodeId="h_lab_106",
        name="Laboratorio de Medicina H106",
        category=CampusCategory.MEDICAL_LAB,
        xPercent=54.7, yPercent=41.8,
        latitude=12.108156, longitude=-86.257708,
        floorLevel=1, isOutdoorAccessPoint=False,
        buildingId="buildingH"
    ))
    subgraph.addNode(Node(
        nodeId="h_lab_107",
        name="Laboratorio de Medicina H107",
        category=CampusCategory.MEDICAL_LAB,
        xPercent=54.3, yPercent=41.8,
        latitude=12.108156, longitude=-86.257708,
        floorLevel=1, isOutdoorAccessPoint=False,
        buildingId="buildingH"
    ))
    # Supplementary Floor 1 nodes from coordenadas.txt
    subgraph.addNode(Node(
        nodeId="h_food_science_lab",
        name="Laboratorio de Ciencias de los Alimentos",
        category=CampusCategory.MEDICAL_LAB,
        xPercent=53.8, yPercent=41.8,
        latitude=12.108156, longitude=-86.257647,
        floorLevel=1, isOutdoorAccessPoint=False,
        buildingId="buildingH"
    ))
    subgraph.addNode(Node(
        nodeId="h_stairs_from_c",
        name="Acceso y Escaleras al Edificio H (lado C)",
        category=CampusCategory.STAIRS,
        xPercent=51.5, yPercent=45.0,
        latitude=12.108253, longitude=-86.257529,
        floorLevel=1, isOutdoorAccessPoint=True,
        portalKind="door", buildingId="buildingH"
    ))
    subgraph.addNode(Node(
        nodeId="h_stairs_main_f1",
        name="Escaleras Principales Edificio H (Piso 1)",
        category=CampusCategory.STAIRS,
        xPercent=55.2, yPercent=41.8,
        latitude=12.108156, longitude=-86.257782,
        floorLevel=1, isOutdoorAccessPoint=True,
        portalKind="stairs", buildingId="buildingH"
    ))

    # =========================================================================
    # FLOOR 2 (SEGUNDO PISO) — Exact left-to-right order (H201..H207)
    # =========================================================================
    subgraph.addNode(Node(
        nodeId="h_lab_201",
        name="Laboratorio de Medicina H201",
        category=CampusCategory.MEDICAL_LAB,
        xPercent=52.5, yPercent=43.5,
        latitude=12.108236, longitude=-86.257552,
        floorLevel=2, isOutdoorAccessPoint=False,
        buildingId="buildingH"
    ))
    subgraph.addNode(Node(
        nodeId="h_lab_202",
        name="Laboratorio de Medicina H202",
        category=CampusCategory.MEDICAL_LAB,
        xPercent=53.1, yPercent=43.2,
        latitude=12.108231, longitude=-86.257608,
        floorLevel=2, isOutdoorAccessPoint=False,
        buildingId="buildingH"
    ))
    subgraph.addNode(Node(
        nodeId="h_lab_203",
        name="Laboratorio de Medicina H203",
        category=CampusCategory.MEDICAL_LAB,
        xPercent=52.8, yPercent=44.2,
        latitude=12.108270, longitude=-86.257560,
        floorLevel=2, isOutdoorAccessPoint=False,
        buildingId="buildingH"
    ))
    subgraph.addNode(Node(
        nodeId="h_lab_204",
        name="Laboratorio de Medicina H204",
        category=CampusCategory.MEDICAL_LAB,
        xPercent=53.2, yPercent=44.2,
        latitude=12.108270, longitude=-86.257560,
        floorLevel=2, isOutdoorAccessPoint=False,
        buildingId="buildingH"
    ))
    subgraph.addNode(Node(
        nodeId="h_lab_205",
        name="Laboratorio de Medicina H205",
        category=CampusCategory.MEDICAL_LAB,
        xPercent=54.2, yPercent=42.8,
        latitude=12.108211, longitude=-86.257727,
        floorLevel=2, isOutdoorAccessPoint=False,
        buildingId="buildingH"
    ))
    subgraph.addNode(Node(
        nodeId="h_lab_206",
        name="Laboratorio de Medicina H206",
        category=CampusCategory.MEDICAL_LAB,
        xPercent=54.5, yPercent=42.8,
        latitude=12.108211, longitude=-86.257727,
        floorLevel=2, isOutdoorAccessPoint=False,
        buildingId="buildingH"
    ))
    subgraph.addNode(Node(
        nodeId="h_lab_207",
        name="Laboratorio de Medicina H207",
        category=CampusCategory.MEDICAL_LAB,
        xPercent=54.8, yPercent=42.8,
        latitude=12.108211, longitude=-86.257727,
        floorLevel=2, isOutdoorAccessPoint=False,
        buildingId="buildingH"
    ))
    subgraph.addNode(Node(
        nodeId="h_stairs_main_f2",
        name="Escaleras Principales Edificio H (Piso 2)",
        category=CampusCategory.STAIRS,
        xPercent=55.2, yPercent=41.8,
        latitude=12.108156, longitude=-86.257782,
        floorLevel=2, isOutdoorAccessPoint=False,
        portalKind="stairs", buildingId="buildingH"
    ))

    f1Edges = [
        ("h_stairs_from_c", "h_restrooms_men_f1"),
        ("h_restrooms_men_f1", "h_restrooms_women_f1"),
        ("h_restrooms_women_f1", "h_lab_101"),
        ("h_lab_101", "h_lab_102"),
        ("h_lab_102", "h_lab_103"),
        ("h_lab_103", "h_lab_104"),
        ("h_lab_104", "h_lab_coord_necroteca"),
        ("h_lab_coord_necroteca", "h_lab_105"),
        ("h_lab_105", "h_stairs_main_f1"),
        ("h_stairs_main_f1", "h_lab_106"),
        ("h_lab_106", "h_lab_107"),
        ("h_lab_107", "h_food_science_lab"),
    ]
    for u, v in f1Edges:
        nU, nV = subgraph.getNode(u), subgraph.getNode(v)
        subgraph.addBidirectionalCorridor(u, v, _calcDist(nU.latitude, nU.longitude, nV.latitude, nV.longitude), isAccessible=True)

    subgraph.addVerticalConnection("h_stairs_main_f1", "h_stairs_main_f2", distanceMeters=11.0, isAccessible=False)

    f2Edges = [
        ("h_stairs_main_f2", "h_lab_207"),
        ("h_lab_207", "h_lab_206"),
        ("h_lab_206", "h_lab_205"),
        ("h_lab_205", "h_lab_204"),
        ("h_lab_204", "h_lab_203"),
        ("h_lab_203", "h_lab_202"),
        ("h_lab_202", "h_lab_201"),
    ]
    for u, v in f2Edges:
        nU, nV = subgraph.getNode(u), subgraph.getNode(v)
        subgraph.addBidirectionalCorridor(u, v, _calcDist(nU.latitude, nU.longitude, nV.latitude, nV.longitude), isAccessible=True)

    aliases = {
        "restroomsMenH1": "h_restrooms_men_f1", "baños h": "h_restrooms_men_f1", "banos h": "h_restrooms_men_f1",
        "h_restrooms_f1": "h_restrooms_men_f1",
        "restroomsWomenH1": "h_restrooms_women_f1",
        "h101": "h_lab_101", "h-101": "h_lab_101", "medicalLabH101": "h_lab_101",
        "h102": "h_lab_102", "h-102": "h_lab_102", "medicalLabH102": "h_lab_102", "h_lab_102_103": "h_lab_102",
        "h103": "h_lab_103", "h-103": "h_lab_103", "medicalLabH103": "h_lab_103", "i108": "h_lab_103",
        "h104": "h_lab_104", "h-104": "h_lab_104", "medicalLabH104": "h_lab_104",
        "gestion de calidad": "h_lab_104", "coordinacion de gestion de calidad": "h_lab_104",
        "necroteca": "h_lab_coord_necroteca", "supervision laboratorios": "h_lab_coord_necroteca",
        "labSupervisionOfficeH": "h_lab_coord_necroteca",
        "oficina de supervision de laboratorios de medicina": "h_lab_coord_necroteca",
        "h105": "h_lab_105", "h-105": "h_lab_105", "medicalLabH105": "h_lab_105",
        "h106": "h_lab_106", "h-106": "h_lab_106", "medicalLabH106": "h_lab_106", "h_lab_106_107": "h_lab_106",
        "h107": "h_lab_107", "h-107": "h_lab_107", "medicalLabH107": "h_lab_107",
        "ciencias de los alimentos": "h_food_science_lab", "foodScienceLabH": "h_food_science_lab",
        "h201": "h_lab_201", "h-201": "h_lab_201", "medicalLabH201": "h_lab_201",
        "h202": "h_lab_202", "h-202": "h_lab_202", "medicalLabH202": "h_lab_202",
        "h203": "h_lab_203", "h-203": "h_lab_203", "medicalLabH203": "h_lab_203", "h_lab_203_204": "h_lab_203",
        "h204": "h_lab_204", "h-204": "h_lab_204", "medicalLabH204": "h_lab_204",
        "h205": "h_lab_205", "h-205": "h_lab_205", "medicalLabH205": "h_lab_205", "h_lab_205_206": "h_lab_205",
        "h206": "h_lab_206", "h-206": "h_lab_206", "medicalLabH206": "h_lab_206",
        "h207": "h_lab_207", "h-207": "h_lab_207", "medicalLabH207": "h_lab_207",
    }
    for alias, nid in aliases.items():
        subgraph.registerRoomAlias(alias, nid)

    return subgraph


buildingHSubgraph = buildBuildingHSubgraph()
