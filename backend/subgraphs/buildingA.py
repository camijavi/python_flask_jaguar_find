"""
buildingA.py
================================================================================
BUILDING A (ATENCIÓN AL ESTUDIANTE, ADMINISTRACIÓN & DPA) SUBGRAPH / CHILD GRAPH
================================================================================
Multi-floor indoor child graph (Floors 1, 2, 3) built strictly from official UAM
room directory (buildings.txt) and field GPS measurements (coordenadas.txt).
Nomenclature follows non-hyphenated codes (A101, A201, A301).
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
        description="Edificio A: Contabilidad (A101), CAE, Admisión, Registro Académico, Cartera y Cobro, Finanzas, Objetos Perdidos, Cajeros, TIC (A203), RRHH (A205) y DPA (A301)."
    )

    # =========================================================================
    # FLOOR 1 (PRIMER PISO) — Exact order from buildings.txt
    # =========================================================================
    subgraph.addNode(Node(
        nodeId="a_contabilidad_101",
        name="Contabilidad (A101)",
        category=CampusCategory.ADMINISTRATIVE,
        xPercent=26.9, yPercent=52.0,
        latitude=12.108503, longitude=-86.256678,
        floorLevel=1, isOutdoorAccessPoint=False,
        buildingId="buildingA"
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
        nodeId="a_mercadeo_admision",
        name="Dirección de Mercadeo y Admisión",
        category=CampusCategory.ADMINISTRATIVE,
        xPercent=26.9, yPercent=51.0,
        latitude=12.108543, longitude=-86.256496,
        floorLevel=1, isOutdoorAccessPoint=False,
        buildingId="buildingA"
    ))
    subgraph.addNode(Node(
        nodeId="a_registro_academico",
        name="Registro Académico",
        category=CampusCategory.ADMINISTRATIVE,
        xPercent=26.9, yPercent=50.3,
        latitude=12.108417, longitude=-86.256656,
        floorLevel=1, isOutdoorAccessPoint=False,
        buildingId="buildingA"
    ))
    subgraph.addNode(Node(
        nodeId="a_cartera_cobro",
        name="Cartera y Cobro",
        category=CampusCategory.ADMINISTRATIVE,
        xPercent=26.9, yPercent=50.8,
        latitude=12.108543, longitude=-86.256496,
        floorLevel=1, isOutdoorAccessPoint=False,
        buildingId="buildingA"
    ))
    subgraph.addNode(Node(
        nodeId="a_direccion_academica",
        name="Dirección Académica (Edificio A)",
        category=CampusCategory.ADMINISTRATIVE,
        xPercent=26.9, yPercent=50.6,
        latitude=12.108543, longitude=-86.256496,
        floorLevel=1, isOutdoorAccessPoint=False,
        buildingId="buildingA"
    ))
    subgraph.addNode(Node(
        nodeId="a_direccion_financiera",
        name="Dirección Financiera",
        category=CampusCategory.ADMINISTRATIVE,
        xPercent=26.9, yPercent=50.4,
        latitude=12.108543, longitude=-86.256496,
        floorLevel=1, isOutdoorAccessPoint=False,
        buildingId="buildingA"
    ))
    subgraph.addNode(Node(
        nodeId="a_reception_lost_found",
        name="Objetos Perdidos (JaguarFind) y Recepción",
        category=CampusCategory.ADMINISTRATIVE,
        xPercent=26.9, yPercent=50.0,
        latitude=12.108417, longitude=-86.256656,
        floorLevel=1, isOutdoorAccessPoint=True,
        portalKind="door", buildingId="buildingA"
    ))
    # Fuera del edificio
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
        nodeId="a_stairs_f1",
        name="Escaleras Edificio A (conexión con Edificio C - Piso 1)",
        category=CampusCategory.STAIRS,
        xPercent=27.2, yPercent=48.5,
        latitude=12.108424, longitude=-86.256697,
        floorLevel=1, isOutdoorAccessPoint=False,
        portalKind="stairs", buildingId="buildingA"
    ))

    # =========================================================================
    # FLOOR 2 (SEGUNDO PISO) — Exact order from buildings.txt
    # =========================================================================
    subgraph.addNode(Node(
        nodeId="a_admin_201",
        name="Dirección Administrativa (A201)",
        category=CampusCategory.ADMINISTRATIVE,
        xPercent=26.9, yPercent=51.5,
        latitude=12.108543, longitude=-86.256609,
        floorLevel=2, isOutdoorAccessPoint=False,
        buildingId="buildingA"
    ))
    subgraph.addNode(Node(
        nodeId="a_logistica_academica",
        name="Logística Académica",
        category=CampusCategory.ADMINISTRATIVE,
        xPercent=26.9, yPercent=51.1,
        latitude=12.108543, longitude=-86.256609,
        floorLevel=2, isOutdoorAccessPoint=False,
        buildingId="buildingA"
    ))
    subgraph.addNode(Node(
        nodeId="a_tic_203",
        name="Dirección Tecnología de la Información y Comunicación - TIC (A203)",
        category=CampusCategory.ADMINISTRATIVE,
        xPercent=26.9, yPercent=50.2,
        latitude=12.108412, longitude=-86.256682,
        floorLevel=2, isOutdoorAccessPoint=False,
        buildingId="buildingA"
    ))
    subgraph.addNode(Node(
        nodeId="a_marketing_204",
        name="Mercadeo y Publicidad (A204)",
        category=CampusCategory.ADMINISTRATIVE,
        xPercent=26.9, yPercent=49.8,
        latitude=12.108412, longitude=-86.256682,
        floorLevel=2, isOutdoorAccessPoint=False,
        buildingId="buildingA"
    ))
    subgraph.addNode(Node(
        nodeId="a_gestion_talento",
        name="Dirección de Gestión del Talento",
        category=CampusCategory.ADMINISTRATIVE,
        xPercent=27.0, yPercent=49.6,
        latitude=12.108416, longitude=-86.256709,
        floorLevel=2, isOutdoorAccessPoint=False,
        buildingId="buildingA"
    ))
    subgraph.addNode(Node(
        nodeId="a_hr_205",
        name="Recursos Humanos (A205)",
        category=CampusCategory.ADMINISTRATIVE,
        xPercent=27.0, yPercent=49.4,
        latitude=12.108416, longitude=-86.256709,
        floorLevel=2, isOutdoorAccessPoint=False,
        buildingId="buildingA"
    ))
    subgraph.addNode(Node(
        nodeId="a_stairs_f2",
        name="Escaleras Edificio A (Piso 2)",
        category=CampusCategory.STAIRS,
        xPercent=27.2, yPercent=48.5,
        latitude=12.108424, longitude=-86.256697,
        floorLevel=2, isOutdoorAccessPoint=False,
        portalKind="stairs", buildingId="buildingA"
    ))

    # =========================================================================
    # FLOOR 3 (TERCER PISO - PRODUCCIÓN AUDIOVISUAL DPA) — Exact order
    # =========================================================================
    subgraph.addNode(Node(
        nodeId="a_dpa_301",
        name="Dirección de Producción Audiovisual (DPA / A301)",
        category=CampusCategory.CLASSROOM,
        xPercent=27.0, yPercent=49.0,
        latitude=12.108418, longitude=-86.256706,
        floorLevel=3, isOutdoorAccessPoint=False,
        buildingId="buildingA"
    ))
    subgraph.addNode(Node(
        nodeId="a_ciclograma",
        name="Set de Grabación Ciclograma",
        category=CampusCategory.CLASSROOM,
        xPercent=27.0, yPercent=49.1,
        latitude=12.108418, longitude=-86.256706,
        floorLevel=3, isOutdoorAccessPoint=False,
        buildingId="buildingA"
    ))
    subgraph.addNode(Node(
        nodeId="a_estudio_sonido",
        name="Estudio de Sonido",
        category=CampusCategory.CLASSROOM,
        xPercent=27.0, yPercent=49.2,
        latitude=12.108418, longitude=-86.256706,
        floorLevel=3, isOutdoorAccessPoint=False,
        buildingId="buildingA"
    ))
    subgraph.addNode(Node(
        nodeId="a_oficinas_dpa",
        name="Oficinas Auxiliares DPA",
        category=CampusCategory.ADMINISTRATIVE,
        xPercent=27.0, yPercent=49.3,
        latitude=12.108418, longitude=-86.256706,
        floorLevel=3, isOutdoorAccessPoint=False,
        buildingId="buildingA"
    ))
    subgraph.addNode(Node(
        nodeId="a_control_master",
        name="Control Máster",
        category=CampusCategory.CLASSROOM,
        xPercent=27.0, yPercent=49.4,
        latitude=12.108418, longitude=-86.256706,
        floorLevel=3, isOutdoorAccessPoint=False,
        buildingId="buildingA"
    ))
    subgraph.addNode(Node(
        nodeId="a_set_radio",
        name="Set de Radio",
        category=CampusCategory.CLASSROOM,
        xPercent=27.0, yPercent=49.5,
        latitude=12.108418, longitude=-86.256706,
        floorLevel=3, isOutdoorAccessPoint=False,
        buildingId="buildingA"
    ))
    subgraph.addNode(Node(
        nodeId="a_stairs_f3",
        name="Escaleras Edificio A (Piso 3)",
        category=CampusCategory.STAIRS,
        xPercent=27.2, yPercent=48.5,
        latitude=12.108424, longitude=-86.256697,
        floorLevel=3, isOutdoorAccessPoint=False,
        portalKind="stairs", buildingId="buildingA"
    ))

    # =========================================================================
    # DIRECTED WEIGHTED CORRIDORS (SPARSE, NON-COMPLETE)
    # =========================================================================
    f1Edges = [
        ("a_atm_map", "a_cae_lobby", _calcDist(12.108560, -86.256574, 12.108543, -86.256496, 6.0)),
        ("a_atm_map", "a_contabilidad_101", _calcDist(12.108560, -86.256574, 12.108503, -86.256678, 8.0)),
        ("a_contabilidad_101", "a_cae_lobby", _calcDist(12.108503, -86.256678, 12.108543, -86.256496, 12.0)),
        ("a_cae_lobby", "a_mercadeo_admision", 2.5),
        ("a_mercadeo_admision", "a_cartera_cobro", 2.5),
        ("a_cartera_cobro", "a_direccion_academica", 2.5),
        ("a_direccion_academica", "a_direccion_financiera", 2.5),
        ("a_contabilidad_101", "a_registro_academico", _calcDist(12.108503, -86.256678, 12.108417, -86.256656, 9.5)),
        ("a_direccion_financiera", "a_registro_academico", _calcDist(12.108543, -86.256496, 12.108417, -86.256656, 14.0)),
        ("a_registro_academico", "a_reception_lost_found", 2.0),
        ("a_reception_lost_found", "a_stairs_f1", _calcDist(12.108417, -86.256656, 12.108424, -86.256697, 4.5)),
    ]
    for u, v, d in f1Edges:
        subgraph.addBidirectionalCorridor(u, v, d, isAccessible=True)

    # Vertical stairs F1 <-> F2 <-> F3
    subgraph.addVerticalConnection("a_stairs_f1", "a_stairs_f2", distanceMeters=11.0, isAccessible=False)
    subgraph.addVerticalConnection("a_stairs_f2", "a_stairs_f3", distanceMeters=11.0, isAccessible=False)

    # Floor 2 corridor
    f2Edges = [
        ("a_stairs_f2", "a_hr_205", _calcDist(12.108424, -86.256697, 12.108416, -86.256709, 3.0)),
        ("a_hr_205", "a_gestion_talento", 2.0),
        ("a_gestion_talento", "a_marketing_204", 3.0),
        ("a_marketing_204", "a_tic_203", 3.0),
        ("a_tic_203", "a_logistica_academica", _calcDist(12.108412, -86.256682, 12.108543, -86.256609, 14.0)),
        ("a_logistica_academica", "a_admin_201", 2.5),
    ]
    for u, v, d in f2Edges:
        subgraph.addBidirectionalCorridor(u, v, d, isAccessible=True)

    # Floor 3 corridor (DPA)
    f3Edges = [
        ("a_stairs_f3", "a_dpa_301", 4.0),
        ("a_dpa_301", "a_ciclograma", 2.5),
        ("a_ciclograma", "a_estudio_sonido", 2.5),
        ("a_estudio_sonido", "a_oficinas_dpa", 2.5),
        ("a_oficinas_dpa", "a_control_master", 2.5),
        ("a_control_master", "a_set_radio", 2.5),
    ]
    for u, v, d in f3Edges:
        subgraph.addBidirectionalCorridor(u, v, d, isAccessible=True)

    # Room & service aliases (includes hyphenated forms for search tolerance)
    aliases = {
        "contabilidad": "a_contabilidad_101", "a101": "a_contabilidad_101", "a-101": "a_contabilidad_101",
        "accountingOfficeA": "a_contabilidad_101",
        "cae": "a_cae_lobby", "studentCareCenterA": "a_cae_lobby", "atencion al estudiante": "a_cae_lobby",
        "zona comun": "a_cae_lobby",
        "mercadeo y admision": "a_mercadeo_admision",
        "direccion de mercadeo y admision": "a_mercadeo_admision", "admissionsMarketingA": "a_mercadeo_admision",
        "admisiones": "a_mercadeo_admision",
        "registro academico": "a_registro_academico", "academicRecordsA": "a_registro_academico",
        "cartera y cobro": "a_cartera_cobro", "collectionsOfficeA": "a_cartera_cobro",
        "direccion academica a": "a_direccion_academica", "academicDirectorateA": "a_direccion_academica",
        "direccion financiera": "a_direccion_financiera", "financialDirectorateA": "a_direccion_financiera",
        "finanzas": "a_direccion_financiera",
        "objetos perdidos": "a_reception_lost_found", "lostAndFoundOfficeA": "a_reception_lost_found",
        "jaguarfind": "a_reception_lost_found", "recepcion a": "a_reception_lost_found",
        "cajeros": "a_atm_map", "atm": "a_atm_map", "bac": "a_atm_map", "lafise": "a_atm_map",
        "atmMachinesA": "a_atm_map", "mapa uam a": "a_atm_map",
        "a201": "a_admin_201", "a-201": "a_admin_201", "adminDirectorateA": "a_admin_201",
        "direccion administrativa": "a_admin_201",
        "logistica academica": "a_logistica_academica", "academicLogisticsA": "a_logistica_academica",
        "a203": "a_tic_203", "a-203": "a_tic_203", "ticDirectorateA": "a_tic_203",
        "tic": "a_tic_203", "tecnologia": "a_tic_203",
        "direccion tecnologia de la informacion y comunicacion": "a_tic_203",
        "a204": "a_marketing_204", "a-204": "a_marketing_204", "marketingAdvertisingA": "a_marketing_204",
        "mercadeo y publicidad": "a_marketing_204",
        "gestion del talento": "a_gestion_talento", "direccion de gestion del talento": "a_gestion_talento",
        "talentDirectorateA": "a_gestion_talento",
        "a205": "a_hr_205", "a-205": "a_hr_205", "hrTalentA": "a_hr_205",
        "recursos humanos": "a_hr_205", "rrhh": "a_hr_205",
        "dpa": "a_dpa_301", "a301": "a_dpa_301", "a-301": "a_dpa_301", "dpaAudiovisualA": "a_dpa_301",
        "studioA301": "a_dpa_301", "estudio audiovisual": "a_dpa_301", "estudio audio visual": "a_dpa_301",
        "produccion audiovisual": "a_dpa_301",
        "ciclograma": "a_ciclograma", "set de grabacion ciclograma": "a_ciclograma", "cycloramaSetA": "a_ciclograma",
        "estudio de sonido": "a_estudio_sonido", "soundStudioA": "a_estudio_sonido",
        "oficinas auxiliares dpa": "a_oficinas_dpa", "dpaAuxOfficesA": "a_oficinas_dpa",
        "control master": "a_control_master", "masterControlA": "a_control_master",
        "set de radio": "a_set_radio", "radioSetA": "a_set_radio",
    }
    for alias, nid in aliases.items():
        subgraph.registerRoomAlias(alias, nid)

    return subgraph


buildingASubgraph = buildBuildingASubgraph()
