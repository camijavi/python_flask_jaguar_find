"""
buildingE.py
================================================================================
BUILDING E (FACULTAD DE MEDICINA, CLÍNICAS & SIMULADORES) SUBGRAPH / CHILD GRAPH
================================================================================
Multi-floor indoor child graph (Floors 1 & 2) built strictly from official UAM
room directory (buildings.txt) and field GPS measurements (coordenadas.txt).
Floor 2 includes: Laboratorio Simuladores de Habilidades Medicina (E201),
Laboratorio Simuladores de Medicina, Oficina Psicología, and Laboratorio Clínico
de Medicina.
Weighted, Directed, Non-Complete Graph G = (V, E, W).
================================================================================
"""

from backend.graph.directedGraph import Node
from backend.data.campusCategories import CampusCategory
from .buildingSubgraph import BuildingSubgraph, makeIndoorDistanceCalculator

_calcDist = makeIndoorDistanceCalculator(2.5)


def buildBuildingESubgraph() -> BuildingSubgraph:
    subgraph = BuildingSubgraph(
        buildingId="buildingE",
        name="Edificio E (Facultad de Medicina & Clínicas Médicas)",
        code="E",
        floors=[1, 2],
        macroNodeId="buildingE",
        entranceNodeIds=["e_ramp_f1", "e_mapa_uam_north", "e_faculty_medicine", "e_vida_estudiantil"],
        description="Edificio E: Clínicas Médicas, Sanitarios, Cardiología, Facultad de Ciencias Médicas, Vida Estudiantil (DVE), DIE, Bancas, Simuladores E201, Psicología y Laboratorio Clínico."
    )

    # =========================================================================
    # FLOOR 1 (PRIMER PISO) — Exact order from buildings.txt
    # =========================================================================
    subgraph.addNode(Node(
        nodeId="e_clinica_medica",
        name="Clínicas Médicas",
        category=CampusCategory.MEDICAL_LAB,
        xPercent=44.2, yPercent=63.2,
        latitude=12.108882, longitude=-86.257119,
        floorLevel=1, isOutdoorAccessPoint=True,
        portalKind="door", buildingId="buildingE"
    ))
    subgraph.addNode(Node(
        nodeId="e_restrooms_men_f1",
        name="Servicios Sanitarios Hombres (Edificio E)",
        category=CampusCategory.RESTROOM,
        xPercent=46.3, yPercent=68.2,
        latitude=12.109072, longitude=-86.257603,
        floorLevel=1, isOutdoorAccessPoint=False,
        buildingId="buildingE"
    ))
    subgraph.addNode(Node(
        nodeId="e_restrooms_women_f1",
        name="Servicios Sanitarios Mujeres (Edificio E)",
        category=CampusCategory.RESTROOM,
        xPercent=46.5, yPercent=68.2,
        latitude=12.109072, longitude=-86.257603,
        floorLevel=1, isOutdoorAccessPoint=False,
        buildingId="buildingE"
    ))
    subgraph.addNode(Node(
        nodeId="e_restrooms_f1",
        name="Servicios Sanitarios Personas con Discapacidades Mixtos (Edificio E)",
        category=CampusCategory.RESTROOM,
        xPercent=46.7, yPercent=68.2,
        latitude=12.109072, longitude=-86.257603,
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
        nodeId="e_faculty_medicine",
        name="Facultad de Ciencias Médicas",
        category=CampusCategory.FACULTY,
        xPercent=44.5, yPercent=75.8,
        latitude=12.109346, longitude=-86.257217,
        floorLevel=1, isOutdoorAccessPoint=True,
        portalKind="door", buildingId="buildingE"
    ))
    subgraph.addNode(Node(
        nodeId="e_vida_estudiantil",
        name="Dirección de Vida Estudiantil (Anexo Oeste)",
        category=CampusCategory.ADMINISTRATIVE,
        xPercent=47.5, yPercent=68.5,
        latitude=12.109081, longitude=-86.257416,
        floorLevel=1, isOutdoorAccessPoint=True,
        portalKind="door", buildingId="buildingE"
    ))
    subgraph.addNode(Node(
        nodeId="e_die_innovation",
        name="Dirección de Innovación y Emprendimientos (DIE) (Anexo Norte)",
        category=CampusCategory.ADMINISTRATIVE,
        xPercent=46.8, yPercent=75.0,
        latitude=12.109312, longitude=-86.257369,
        floorLevel=1, isOutdoorAccessPoint=True,
        portalKind="door", buildingId="buildingE"
    ))
    subgraph.addNode(Node(
        nodeId="e_bancas",
        name="Bancas (Edificio E)",
        category=CampusCategory.FOOD_AREA,
        xPercent=45.3, yPercent=67.2,
        latitude=12.109055, longitude=-86.257355,
        floorLevel=1, isOutdoorAccessPoint=False,
        buildingId="buildingE"
    ))
    # Supplementary field-measured Floor 1 nodes from coordenadas.txt
    subgraph.addNode(Node(
        nodeId="e_consultorio_pediatria",
        name="Consultorio de Pediatría / Lab de Medicina",
        category=CampusCategory.MEDICAL_LAB,
        xPercent=44.0, yPercent=61.0,
        latitude=12.108763, longitude=-86.257082,
        floorLevel=1, isOutdoorAccessPoint=False,
        buildingId="buildingE"
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
        nodeId="e_ramp_f1",
        name="Rampa Accesible hacia Edificio E",
        category=CampusCategory.ACCESSIBLE_RAMP,
        xPercent=45.0, yPercent=66.5,
        latitude=12.109049, longitude=-86.257325,
        floorLevel=1, isOutdoorAccessPoint=True,
        portalKind="ramp", buildingId="buildingE"
    ))
    subgraph.addNode(Node(
        nodeId="e_mapa_uam_north",
        name="Mapa UAM (Acceso Norte Edificio E)",
        category=CampusCategory.ADMINISTRATIVE,
        xPercent=44.5, yPercent=61.8,
        latitude=12.108805, longitude=-86.257210,
        floorLevel=1, isOutdoorAccessPoint=True,
        portalKind="door", buildingId="buildingE"
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
        nodeId="e_stairs_left_f1",
        name="Escaleras Izquierda Edificio E (Piso 1)",
        category=CampusCategory.STAIRS,
        xPercent=44.5, yPercent=59.5,
        latitude=12.108718, longitude=-86.257299,
        floorLevel=1, isOutdoorAccessPoint=True,
        portalKind="stairs", buildingId="buildingE"
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
    # FLOOR 2 (SEGUNDO PISO) — Exact order from buildings.txt
    # =========================================================================
    subgraph.addNode(Node(
        nodeId="e_sim_center_201",
        name="Laboratorio Simuladores de Habilidades Medicina (E201)",
        category=CampusCategory.MEDICAL_LAB,
        xPercent=44.5, yPercent=63.0,
        latitude=12.108874, longitude=-86.257213,
        floorLevel=2, isOutdoorAccessPoint=False,
        buildingId="buildingE"
    ))
    subgraph.addNode(Node(
        nodeId="e_pediatrics_control",
        name="Laboratorio Simuladores de Medicina (Pediatría, Neonatología y Salas de Control)",
        category=CampusCategory.MEDICAL_LAB,
        xPercent=44.5, yPercent=64.0,
        latitude=12.108902, longitude=-86.257221,
        floorLevel=2, isOutdoorAccessPoint=False,
        buildingId="buildingE"
    ))
    subgraph.addNode(Node(
        nodeId="e_psychology",
        name="Oficina Psicología",
        category=CampusCategory.ADMINISTRATIVE,
        xPercent=44.5, yPercent=71.2,
        latitude=12.109180, longitude=-86.257158,
        floorLevel=2, isOutdoorAccessPoint=False,
        buildingId="buildingE"
    ))
    subgraph.addNode(Node(
        nodeId="e_lab_clinico",
        name="Laboratorio Clínico de Medicina",
        category=CampusCategory.MEDICAL_LAB,
        xPercent=44.5, yPercent=73.5,
        latitude=12.109286, longitude=-86.257194,
        floorLevel=2, isOutdoorAccessPoint=False,
        buildingId="buildingE"
    ))
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
        ("e_ramp_f1", "e_bancas"),
        ("e_bancas", "e_fountain_f1"),
        ("e_fountain_f1", "e_cardiology"),
        ("e_cardiology", "e_vida_estudiantil"),
        ("e_vida_estudiantil", "e_restrooms_men_f1"),
        ("e_restrooms_men_f1", "e_restrooms_women_f1"),
        ("e_restrooms_women_f1", "e_restrooms_f1"),
        ("e_cardiology", "e_mapa_uam_south"),
        ("e_mapa_uam_south", "e_faculty_medicine"),
        ("e_faculty_medicine", "e_stairs_south_f1"),
        ("e_faculty_medicine", "e_die_innovation"),
        ("e_vida_estudiantil", "e_die_innovation"),
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
        ("e_pediatrics_control", "e_psychology"),
        ("e_psychology", "e_lab_clinico"),
        ("e_lab_clinico", "e_stairs_south_f2"),
    ]
    for u, v in f2Edges:
        nU, nV = subgraph.getNode(u), subgraph.getNode(v)
        subgraph.addBidirectionalCorridor(u, v, _calcDist(nU.latitude, nU.longitude, nV.latitude, nV.longitude), isAccessible=True)

    aliases = {
        "medicalClinicsE": "e_clinica_medica", "clinicas medicas": "e_clinica_medica", "clinica medica": "e_clinica_medica",
        "restroomsMenE": "e_restrooms_men_f1", "baños hombres e": "e_restrooms_men_f1",
        "restroomsWomenE": "e_restrooms_women_f1", "baños mujeres e": "e_restrooms_women_f1",
        "accessibleRestroomE": "e_restrooms_f1", "baños e": "e_restrooms_f1", "bano accesible": "e_restrooms_f1",
        "cardiologyCenterE": "e_cardiology", "cardiologia": "e_cardiology",
        "facultyMedicineE": "e_faculty_medicine", "facultad de medicina": "e_faculty_medicine",
        "decanatura medicina": "e_faculty_medicine", "ciencias medicas": "e_faculty_medicine",
        "studentLifeOfficeE": "e_vida_estudiantil", "vida estudiantil": "e_vida_estudiantil", "dve": "e_vida_estudiantil",
        "innovationOfficeE": "e_die_innovation", "die": "e_die_innovation",
        "innovacion": "e_die_innovation", "emprendimiento": "e_die_innovation",
        "direccion de innovacion": "e_die_innovation",
        "bancas": "e_bancas", "benchesE": "e_bancas",
        "consultorio pediatria": "e_consultorio_pediatria", "rampa e": "e_ramp_f1",
        "medicalSimulatorsE2": "e_sim_center_201", "simuladores": "e_sim_center_201",
        "e201": "e_sim_center_201", "e-201": "e_sim_center_201",
        "centro de simulacion": "e_sim_center_201",
        "medicalSimulatorsWardE2": "e_pediatrics_control", "laboratorio simuladores de medicina": "e_pediatrics_control",
        "pediatria": "e_pediatrics_control", "neonatologia": "e_pediatrics_control", "cuidados medicos": "e_pediatrics_control",
        "psychologyOfficeE": "e_psychology", "oficina psicologia": "e_psychology", "psicologia": "e_psychology", "psicologa": "e_psychology",
        "clinicalMedicineLabE": "e_lab_clinico", "laboratorio clinico de medicina": "e_lab_clinico",
        "laboratorio clinico": "e_lab_clinico", "lab clinico": "e_lab_clinico",
    }
    for alias, nid in aliases.items():
        subgraph.registerRoomAlias(alias, nid)

    return subgraph


buildingESubgraph = buildBuildingESubgraph()
