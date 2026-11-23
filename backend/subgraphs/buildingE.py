"""
buildingE.py
================================================================================
BUILDING E (FACULTAD DE MEDICINA, CLÍNICAS & SIMULADORES) SUBGRAPH / CHILD GRAPH
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


def buildBuildingESubgraph() -> BuildingSubgraph:
    subgraph = BuildingSubgraph(
        buildingId="buildingE",
        name="Edificio E (Facultad de Medicina & Clínicas Médicas)",
        code="E",
        floors=[1, 2],
        macroNodeId="buildingE",
        entranceNodeIds=["e_ramp_f1", "e_mapa_uam_north", "e_faculty_medicine", "e_vida_estudiantil"],
        description="Edificio E: Facultad de Ciencias Médicas, Clínicas Médicas, Cardiología, Vida Estudiantil (DVE), DIE y Centro de Simulación."
    )

    # =========================================================================
    # FLOOR 1 (PRIMER PISO)
    # =========================================================================
    subgraph.addNode(Node(
        nodeId="e_stairs_left_f1",
        name="Escaleras Izquierda Edificio E (Piso 1)",
        category=CampusCategory.STAIRS,
        xPercent=44.5, yPercent=59.5,
        latitude=12.108718, longitude=-86.257299,
        floorLevel=1, isOutdoorAccessPoint=True,
        portalKind="stairs", buildingId="buildingE"
    ))
    subgraph.addNode(Node(
        nodeId="e_consultorio_pediatria",
        name="Consultorio de Pediatría y Laboratorio de Medicina",
        category=CampusCategory.MEDICAL_LAB,
        xPercent=44.0, yPercent=61.0,
        latitude=12.108763, longitude=-86.257082,
        floorLevel=1, isOutdoorAccessPoint=False,
        buildingId="buildingE"
    ))
    subgraph.addNode(Node(
        nodeId="e_mapa_uam_north",
        name="Mapa UAM (Acceso Norte Edificio E / DIE)",
        category=CampusCategory.ADMINISTRATIVE,
        xPercent=44.5, yPercent=61.8,
        latitude=12.108805, longitude=-86.257210,
        floorLevel=1, isOutdoorAccessPoint=True,
        portalKind="door", buildingId="buildingE"
    ))
    subgraph.addNode(Node(
        nodeId="e_clinica_medica",
        name="Clínicas Médicas UAM",
        category=CampusCategory.MEDICAL_LAB,
        xPercent=44.2, yPercent=63.2,
        latitude=12.108882, longitude=-86.257119,
        floorLevel=1, isOutdoorAccessPoint=True,
        portalKind="door", buildingId="buildingE"
    ))
    subgraph.addNode(Node(
        nodeId="e_ramp_f1",
        name="Rampa Accesible hacia Edificio E",
        category=CampusCategory.ACCESSIBLE_RAMP,
        xPercent=45.0, yPercent=66.5,
        latitude=12.109049, longitude=-86.257325,
        floorLevel=1, isOutdoorAccessPoint=True,
        portalKind="ramp", buildingId="buildingE"
    ))
    subgraph.addNode(Node(
        nodeId="e_fountain_f1",
        name="Bebedero de Agua (Edificio E)",
        category=CampusCategory.DRINKING_FOUNTAIN,
        xPercent=45.2, yPercent=67.0,
        latitude=12.109046, longitude=-86.257406,
        floorLevel=1, isOutdoorAccessPoint=False,
        buildingId="buildingE"
    ))
    subgraph.addNode(Node(
        nodeId="e_cardiology",
        name="Centro de Cardiología",
        category=CampusCategory.MEDICAL_LAB,
        xPercent=45.0, yPercent=67.5,
        latitude=12.109062, longitude=-86.257375,
        floorLevel=1, isOutdoorAccessPoint=False,
        buildingId="buildingE"
    ))
    subgraph.addNode(Node(
        nodeId="e_vida_estudiantil",
        name="Dirección de Vida Estudiantil (DVE - Anexo Oeste)",
        category=CampusCategory.ADMINISTRATIVE,
        xPercent=47.5, yPercent=68.5,
        latitude=12.109081, longitude=-86.257416,
        floorLevel=1, isOutdoorAccessPoint=True,
        portalKind="door", buildingId="buildingE"
    ))
    subgraph.addNode(Node(
        nodeId="e_restrooms_f1",
        name="Servicios Sanitarios Edificio E (Hombres, Mujeres e Inclusivos)",
        category=CampusCategory.RESTROOM,
        xPercent=46.5, yPercent=68.2,
        latitude=12.109072, longitude=-86.257603,
        floorLevel=1, isOutdoorAccessPoint=False,
        buildingId="buildingE"
    ))
    subgraph.addNode(Node(
        nodeId="e_mapa_uam_south",
        name="Mapa UAM (Pasillo Facultad de Medicina)",
        category=CampusCategory.ADMINISTRATIVE,
        xPercent=44.5, yPercent=69.5,
        latitude=12.109103, longitude=-86.257189,
        floorLevel=1, isOutdoorAccessPoint=False,
        buildingId="buildingE"
    ))
    subgraph.addNode(Node(
        nodeId="e_psychology",
        name="Oficina de Psicología",
        category=CampusCategory.ADMINISTRATIVE,
        xPercent=44.5, yPercent=71.2,
        latitude=12.109180, longitude=-86.257158,
        floorLevel=1, isOutdoorAccessPoint=False,
        buildingId="buildingE"
    ))
    subgraph.addNode(Node(
        nodeId="e_lab_clinico",
        name="Laboratorio Clínico de Medicina",
        category=CampusCategory.MEDICAL_LAB,
        xPercent=44.5, yPercent=73.5,
        latitude=12.109286, longitude=-86.257194,
        floorLevel=1, isOutdoorAccessPoint=False,
        buildingId="buildingE"
    ))
    subgraph.addNode(Node(
        nodeId="e_faculty_medicine",
        name="Facultad de Ciencias Médicas (Decanatura)",
        category=CampusCategory.FACULTY,
        xPercent=44.5, yPercent=75.8,
        latitude=12.109346, longitude=-86.257217,
        floorLevel=1, isOutdoorAccessPoint=True,
        portalKind="door", buildingId="buildingE"
    ))
    subgraph.addNode(Node(
        nodeId="e_stairs_south_f1",
        name="Escaleras Sur Edificio E (Piso 1)",
        category=CampusCategory.STAIRS,
        xPercent=44.8, yPercent=75.8,
        latitude=12.109346, longitude=-86.257217,
        floorLevel=1, isOutdoorAccessPoint=False,
        portalKind="stairs", buildingId="buildingE"
    ))

    # =========================================================================
    # FLOOR 2 (SEGUNDO PISO)
    # =========================================================================
    subgraph.addNode(Node(
        nodeId="e_stairs_left_f2",
        name="Escaleras Izquierda Edificio E (Piso 2)",
        category=CampusCategory.STAIRS,
        xPercent=44.5, yPercent=59.5,
        latitude=12.108718, longitude=-86.257299,
        floorLevel=2, isOutdoorAccessPoint=False,
        portalKind="stairs", buildingId="buildingE"
    ))
    subgraph.addNode(Node(
        nodeId="e_sim_center_201",
        name="Centro de Simulación Médica (E-201)",
        category=CampusCategory.MEDICAL_LAB,
        xPercent=44.5, yPercent=63.0,
        latitude=12.108874, longitude=-86.257213,
        floorLevel=2, isOutdoorAccessPoint=False,
        buildingId="buildingE"
    ))
    subgraph.addNode(Node(
        nodeId="e_pediatrics_control",
        name="Pediatría, Neonatología, Salas de Control 1-2 y Cuidados Médicos",
        category=CampusCategory.MEDICAL_LAB,
        xPercent=44.5, yPercent=64.0,
        latitude=12.108902, longitude=-86.257221,
        floorLevel=2, isOutdoorAccessPoint=False,
        buildingId="buildingE"
    ))
    subgraph.addNode(Node(
        nodeId="e_stairs_south_f2",
        name="Escaleras Sur Edificio E (Piso 2)",
        category=CampusCategory.STAIRS,
        xPercent=44.8, yPercent=75.8,
        latitude=12.109346, longitude=-86.257217,
        floorLevel=2, isOutdoorAccessPoint=False,
        portalKind="stairs", buildingId="buildingE"
    ))

    # =========================================================================
    # DIRECTED WEIGHTED CORRIDORS (SPARSE, NON-COMPLETE)
    # =========================================================================
    f1Edges = [
        ("e_stairs_left_f1", "e_mapa_uam_north"),
        ("e_mapa_uam_north", "e_consultorio_pediatria"),
        ("e_mapa_uam_north", "e_clinica_medica"),
        ("e_clinica_medica", "e_ramp_f1"),
        ("e_ramp_f1", "e_fountain_f1"),
        ("e_fountain_f1", "e_cardiology"),
        ("e_cardiology", "e_vida_estudiantil"),
        ("e_vida_estudiantil", "e_restrooms_f1"),
        ("e_cardiology", "e_mapa_uam_south"),
        ("e_mapa_uam_south", "e_psychology"),
        ("e_psychology", "e_lab_clinico"),
        ("e_lab_clinico", "e_faculty_medicine"),
        ("e_faculty_medicine", "e_stairs_south_f1"),
    ]
    for u, v in f1Edges:
        nU, nV = subgraph.getNode(u), subgraph.getNode(v)
        subgraph.addBidirectionalCorridor(u, v, _calcDist(nU.latitude, nU.longitude, nV.latitude, nV.longitude), isAccessible=True)

    # Vertical Stairs F1 <-> F2
    subgraph.addVerticalConnection("e_stairs_left_f1", "e_stairs_left_f2", distanceMeters=11.0, isAccessible=False)
    subgraph.addVerticalConnection("e_stairs_south_f1", "e_stairs_south_f2", distanceMeters=11.0, isAccessible=False)

    f2Edges = [
        ("e_stairs_left_f2", "e_sim_center_201"),
        ("e_sim_center_201", "e_pediatrics_control"),
        ("e_pediatrics_control", "e_stairs_south_f2"),
    ]
    for u, v in f2Edges:
        nU, nV = subgraph.getNode(u), subgraph.getNode(v)
        subgraph.addBidirectionalCorridor(u, v, _calcDist(nU.latitude, nU.longitude, nV.latitude, nV.longitude), isAccessible=True)

    aliases = {
        "facultyMedicineE": "e_faculty_medicine", "facultad de medicina": "e_faculty_medicine",
        "decanatura medicina": "e_faculty_medicine", "ciencias medicas": "e_faculty_medicine",
        "medicalClinicsE": "e_clinica_medica", "clinicas medicas": "e_clinica_medica", "clinica medica": "e_clinica_medica",
        "cardiologyCenterE": "e_cardiology", "cardiologia": "e_cardiology",
        "accessibleRestroomE": "e_restrooms_f1", "baños e": "e_restrooms_f1", "bano accesible": "e_restrooms_f1",
        "studentLifeOfficeE": "e_vida_estudiantil", "vida estudiantil": "e_vida_estudiantil", "dve": "e_vida_estudiantil",
        "innovationOfficeE": "e_mapa_uam_north", "die": "e_mapa_uam_north", "innovacion": "e_mapa_uam_north",
        "medicalSimulatorsE2": "e_sim_center_201", "simuladores": "e_sim_center_201", "e201": "e_sim_center_201",
        "centro de simulacion": "e_sim_center_201",
        "pediatria": "e_pediatrics_control", "neonatologia": "e_pediatrics_control", "cuidados medicos": "e_pediatrics_control",
        "psicologia": "e_psychology", "psicologa": "e_psychology",
        "laboratorio clinico": "e_lab_clinico", "lab clinico": "e_lab_clinico",
        "consultorio pediatria": "e_consultorio_pediatria", "rampa e": "e_ramp_f1",
    }
    for alias, nid in aliases.items():
        subgraph.registerRoomAlias(alias, nid)

    return subgraph


buildingESubgraph = buildBuildingESubgraph()
