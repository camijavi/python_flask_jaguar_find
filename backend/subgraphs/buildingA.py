"""
buildingA.py
================================================================================
BUILDING A (ATENCIÓN AL ESTUDIANTE, ADMINISTRACIÓN & DPA) SUBGRAPH / CHILD GRAPH
================================================================================
Multi-floor indoor child graph (Floors 1, 2, 3) built from official UAM field
GPS measurements (coordenadas.txt) and room directory (buildings.txt).
Weighted, Directed, Non-Complete Graph G = (V, E, W).
================================================================================
"""

from backend.graph.directedGraph import Node
from backend.data.campusCategories import CampusCategory
from .buildingSubgraph import BuildingSubgraph, calcIndoorDistance as _calcDist


def buildBuildingASubgraph() -> BuildingSubgraph:
    subgraph = BuildingSubgraph(
        buildingId="buildingA",
        name="Edificio A (Atención al Estudiante, Administración & DPA)",
        code="A",
        floors=[1, 2, 3],
        macroNodeId="buildingA",
        entranceNodeIds=["a_atm_map", "a_cae_lobby", "a_reception_lost_found"],
        description="Edificio A: CAE, Registro Académico, Objetos Perdidos (JaguarFind), Contabilidad, TIC, RRHH y DPA."
    )

    # =========================================================================
    # FLOOR 1 (PRIMER PISO)
    # =========================================================================
    subgraph.addNode(Node(
        nodeId="a_atm_map",
        name="Cajeros Automáticos (BAC y LAFISE) y Mapa UAM",
        category=CampusCategory.ADMINISTRATIVE,
        xPercent=26.2, yPercent=51.2,
        latitude=12.108560, longitude=-86.256574,
        floorLevel=1, isOutdoorAccessPoint=True,
        portalKind="door", buildingId="buildingA"
    ))
    subgraph.addNode(Node(
        nodeId="a_cae_lobby",
        name="Centro de Atención al Estudiante (CAE) / Zona Común",
        category=CampusCategory.ADMINISTRATIVE,
        xPercent=26.9, yPercent=51.2,
        latitude=12.108543, longitude=-86.256496,
        floorLevel=1, isOutdoorAccessPoint=True,
        portalKind="door", buildingId="buildingA"
    ))
    subgraph.addNode(Node(
        nodeId="a_contabilidad_101",
        name="Contabilidad (A-101)",
        category=CampusCategory.ADMINISTRATIVE,
        xPercent=26.9, yPercent=52.0,
        latitude=12.108503, longitude=-86.256678,
        floorLevel=1, isOutdoorAccessPoint=False,
        buildingId="buildingA"
    ))
    subgraph.addNode(Node(
        nodeId="a_reception_lost_found",
        name="Recepción, Objetos Perdidos (JaguarFind) y Registro Académico",
        category=CampusCategory.ADMINISTRATIVE,
        xPercent=26.9, yPercent=50.0,
        latitude=12.108417, longitude=-86.256656,
        floorLevel=1, isOutdoorAccessPoint=True,
        portalKind="door", buildingId="buildingA"
    ))
    subgraph.addNode(Node(
        nodeId="a_stairs_f1",
        name="Escaleras Edificio A (conexión con Edificio C - Piso 1)",
        category=CampusCategory.STAIRS,
        xPercent=27.2, yPercent=48.5,
        latitude=12.108424, longitude=-86.256697,
        floorLevel=1, isOutdoorAccessPoint=False,
        portalKind="stairs", buildingId="buildingA"
    ))

    # =========================================================================
    # FLOOR 2 (SEGUNDO PISO)
    # =========================================================================
    subgraph.addNode(Node(
        nodeId="a_stairs_f2",
        name="Escaleras Edificio A (Piso 2)",
        category=CampusCategory.STAIRS,
        xPercent=27.2, yPercent=48.5,
        latitude=12.108424, longitude=-86.256697,
        floorLevel=2, isOutdoorAccessPoint=False,
        portalKind="stairs", buildingId="buildingA"
    ))
    subgraph.addNode(Node(
        nodeId="a_admin_201",
        name="Dirección Administrativa y Logística Académica (A-201)",
        category=CampusCategory.ADMINISTRATIVE,
        xPercent=26.9, yPercent=51.5,
        latitude=12.108543, longitude=-86.256609,
        floorLevel=2, isOutdoorAccessPoint=False,
        buildingId="buildingA"
    ))
    subgraph.addNode(Node(
        nodeId="a_tic_203",
        name="Dirección de Tecnología de la Información y Comunicación - TIC (A-203)",
        category=CampusCategory.ADMINISTRATIVE,
        xPercent=26.9, yPercent=50.2,
        latitude=12.108412, longitude=-86.256682,
        floorLevel=2, isOutdoorAccessPoint=False,
        buildingId="buildingA"
    ))
    subgraph.addNode(Node(
        nodeId="a_marketing_204",
        name="Mercadeo y Publicidad (A-204)",
        category=CampusCategory.ADMINISTRATIVE,
        xPercent=26.9, yPercent=49.8,
        latitude=12.108412, longitude=-86.256682,
        floorLevel=2, isOutdoorAccessPoint=False,
        buildingId="buildingA"
    ))
    subgraph.addNode(Node(
        nodeId="a_hr_205",
        name="Dirección de Gestión del Talento / Recursos Humanos (A-205)",
        category=CampusCategory.ADMINISTRATIVE,
        xPercent=27.0, yPercent=49.4,
        latitude=12.108416, longitude=-86.256709,
        floorLevel=2, isOutdoorAccessPoint=False,
        buildingId="buildingA"
    ))

    # =========================================================================
    # FLOOR 3 (TERCER PISO - PRODUCCIÓN AUDIOVISUAL DPA)
    # =========================================================================
    subgraph.addNode(Node(
        nodeId="a_stairs_f3",
        name="Escaleras Edificio A (Piso 3)",
        category=CampusCategory.STAIRS,
        xPercent=27.2, yPercent=48.5,
        latitude=12.108424, longitude=-86.256697,
        floorLevel=3, isOutdoorAccessPoint=False,
        portalKind="stairs", buildingId="buildingA"
    ))
    subgraph.addNode(Node(
        nodeId="a_dpa_301",
        name="Dirección de Producción Audiovisual - DPA (Estudio A-301, Ciclograma, Sonido y Radio)",
        category=CampusCategory.CLASSROOM,
        xPercent=27.0, yPercent=49.0,
        latitude=12.108418, longitude=-86.256706,
        floorLevel=3, isOutdoorAccessPoint=False,
        buildingId="buildingA"
    ))

    # =========================================================================
    # DIRECTED WEIGHTED CORRIDORS (SPARSE, NON-COMPLETE)
    # =========================================================================
    dAtmCae = _calcDist(12.108560, -86.256574, 12.108543, -86.256496, 6.0)
    subgraph.addBidirectionalCorridor("a_atm_map", "a_cae_lobby", dAtmCae, isAccessible=True)

    dAtmCont = _calcDist(12.108560, -86.256574, 12.108503, -86.256678, 8.0)
    subgraph.addBidirectionalCorridor("a_atm_map", "a_contabilidad_101", dAtmCont, isAccessible=True)

    dCaeCont = _calcDist(12.108543, -86.256496, 12.108503, -86.256678, 12.0)
    subgraph.addBidirectionalCorridor("a_cae_lobby", "a_contabilidad_101", dCaeCont, isAccessible=True)

    dContRec = _calcDist(12.108503, -86.256678, 12.108417, -86.256656, 9.5)
    subgraph.addBidirectionalCorridor("a_contabilidad_101", "a_reception_lost_found", dContRec, isAccessible=True)

    dRecStairs = _calcDist(12.108417, -86.256656, 12.108424, -86.256697, 4.5)
    subgraph.addBidirectionalCorridor("a_reception_lost_found", "a_stairs_f1", dRecStairs, isAccessible=True)

    # Vertical stairs F1 <-> F2 <-> F3
    subgraph.addVerticalConnection("a_stairs_f1", "a_stairs_f2", distanceMeters=11.0, isAccessible=False)
    subgraph.addVerticalConnection("a_stairs_f2", "a_stairs_f3", distanceMeters=11.0, isAccessible=False)

    # Floor 2 corridor
    dStairsHr = _calcDist(12.108424, -86.256697, 12.108416, -86.256709, 3.0)
    subgraph.addBidirectionalCorridor("a_stairs_f2", "a_hr_205", dStairsHr, isAccessible=True)
    subgraph.addBidirectionalCorridor("a_hr_205", "a_marketing_204", 3.5, isAccessible=True)
    subgraph.addBidirectionalCorridor("a_marketing_204", "a_tic_203", 3.0, isAccessible=True)
    dTicAdmin = _calcDist(12.108412, -86.256682, 12.108543, -86.256609, 14.0)
    subgraph.addBidirectionalCorridor("a_tic_203", "a_admin_201", dTicAdmin, isAccessible=True)

    # Floor 3 corridor
    subgraph.addBidirectionalCorridor("a_stairs_f3", "a_dpa_301", 4.0, isAccessible=True)

    # Room & service aliases
    aliases = {
        "cajeros": "a_atm_map", "atm": "a_atm_map", "bac": "a_atm_map", "lafise": "a_atm_map",
        "atmMachinesA": "a_atm_map", "mapa uam a": "a_atm_map",
        "cae": "a_cae_lobby", "studentCareCenterA": "a_cae_lobby", "atencion al estudiante": "a_cae_lobby",
        "zona comun": "a_cae_lobby", "mercadeo y admision": "a_cae_lobby", "admisiones": "a_cae_lobby",
        "cartera y cobro": "a_cae_lobby", "direccion financiera": "a_cae_lobby",
        "contabilidad": "a_contabilidad_101", "a101": "a_contabilidad_101", "a-101": "a_contabilidad_101",
        "accountingOfficeA": "a_contabilidad_101", "finanzas": "a_contabilidad_101",
        "objetos perdidos": "a_reception_lost_found", "lostAndFoundOfficeA": "a_reception_lost_found",
        "jaguarfind": "a_reception_lost_found", "registro academico": "a_reception_lost_found",
        "academicRecordsA": "a_reception_lost_found", "recepcion a": "a_reception_lost_found",
        "a201": "a_admin_201", "a-201": "a_admin_201", "direccion administrativa": "a_admin_201",
        "logistica academica": "a_admin_201",
        "a203": "a_tic_203", "a-203": "a_tic_203", "tic": "a_tic_203", "tecnologia": "a_tic_203",
        "a204": "a_marketing_204", "a-204": "a_marketing_204", "mercadeo y publicidad": "a_marketing_204",
        "a205": "a_hr_205", "a-205": "a_hr_205", "recursos humanos": "a_hr_205", "rrhh": "a_hr_205",
        "gestion del talento": "a_hr_205",
        "dpa": "a_dpa_301", "a301": "a_dpa_301", "a-301": "a_dpa_301", "ciclograma": "a_dpa_301",
        "estudio de sonido": "a_dpa_301", "control master": "a_dpa_301", "set de radio": "a_dpa_301",
        "produccion audiovisual": "a_dpa_301",
    }
    for alias, nid in aliases.items():
        subgraph.registerRoomAlias(alias, nid)

    return subgraph


buildingASubgraph = buildBuildingASubgraph()
