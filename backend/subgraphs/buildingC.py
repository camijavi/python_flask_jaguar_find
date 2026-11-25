"""
buildingC.py
================================================================================
BUILDING C (AULAS, LABS DE COMPUTACIÓN & TESORERÍA) SUBGRAPH / CHILD GRAPH
================================================================================
Indoor child graph representation for Building C (Edificio C), covering 3 floors
strictly synchronized with buildings.txt and coordenadas.txt.
Enforces left-to-right ordering (C101..C109, C201..C211, C301..C310) and
non-hyphenated room nomenclature (C101, NOT C-101).
Note: DPA / Estudio Audiovisual A301 belongs strictly to Building A (Floor 3).
Weighted, Directed, Non-Complete Graph G = (V, E, W).
================================================================================
"""

from backend.graph.directedGraph import Node
from backend.data.campusCategories import CampusCategory
from .buildingSubgraph import BuildingSubgraph, calcIndoorDistance as _calcDist


def buildBuildingCSubgraph() -> BuildingSubgraph:
    """
    Constructs the official child graph for Building C (3 Floors: Aulas, Labs Computación, Tesorería).
    """
    subgraph = BuildingSubgraph(
        buildingId="buildingC",
        name="Edificio C (Laboratorios de Computación & Tesorería)",
        code="C",
        floors=[1, 2, 3],
        macroNodeId="buildingC",
        entranceNodeIds=["c_mapa_uam_f1", "c_ramp_f1", "c_stairs_left_f1", "c_stairs_right_f1"],
        description="Edificio C: Auditorios C101 y C109, Aulas C102-C106, Caja UAM / Tesorería C105, Lab MAC C107, Lab ACAI-Erasmus+ C108, Labs C201-C205, Bodega C206, Aulas C209-C211 y C301-C310."
    )

    # =========================================================================
    # FLOOR 1 (PLANTA BAJA) — Exact left-to-right order from buildings.txt
    # =========================================================================
    subgraph.addNode(Node(
        nodeId="c_auditorium_101",
        name="Auditorio C101",
        category=CampusCategory.AUDITORIUM,
        xPercent=34.1, yPercent=53.1,
        latitude=12.108528, longitude=-86.256743,
        floorLevel=1, isOutdoorAccessPoint=False
    ))
    subgraph.addNode(Node(
        nodeId="c_room_102",
        name="Aula C102",
        category=CampusCategory.CLASSROOM,
        xPercent=34.3, yPercent=53.2,
        latitude=12.108549, longitude=-86.256848,
        floorLevel=1, isOutdoorAccessPoint=False
    ))
    subgraph.addNode(Node(
        nodeId="c_room_103",
        name="Aula C103",
        category=CampusCategory.CLASSROOM,
        xPercent=34.4, yPercent=53.3,
        latitude=12.108527, longitude=-86.256908,
        floorLevel=1, isOutdoorAccessPoint=False
    ))
    subgraph.addNode(Node(
        nodeId="c_room_104",
        name="Aula C104",
        category=CampusCategory.CLASSROOM,
        xPercent=34.5, yPercent=53.3,
        latitude=12.108583, longitude=-86.256918,
        floorLevel=1, isOutdoorAccessPoint=False
    ))
    subgraph.addNode(Node(
        nodeId="c_treasury_105",
        name="Tesorería UAM (C105)",
        category=CampusCategory.ADMINISTRATIVE,
        xPercent=34.7, yPercent=53.5,
        latitude=12.108557, longitude=-86.257120,
        floorLevel=1, isOutdoorAccessPoint=False
    ))
    subgraph.addNode(Node(
        nodeId="c_fountain_f1",
        name="Bebedero de Agua (Edificio C - Piso 1)",
        category=CampusCategory.DRINKING_FOUNTAIN,
        xPercent=34.4, yPercent=53.3,
        latitude=12.108527, longitude=-86.256908,
        floorLevel=1, isOutdoorAccessPoint=False
    ))
    subgraph.addNode(Node(
        nodeId="c_cashier",
        name="Caja UAM / Tesorería",
        category=CampusCategory.ADMINISTRATIVE,
        xPercent=34.6, yPercent=53.4,
        latitude=12.108446, longitude=-86.257021,
        floorLevel=1, isOutdoorAccessPoint=False
    ))
    subgraph.addNode(Node(
        nodeId="c_room_106",
        name="Aula C106",
        category=CampusCategory.CLASSROOM,
        xPercent=34.8, yPercent=53.6,
        latitude=12.108522, longitude=-86.257194,
        floorLevel=1, isOutdoorAccessPoint=False
    ))
    subgraph.addNode(Node(
        nodeId="c_lab_mac_107",
        name="Laboratorio MAC C107",
        category=CampusCategory.CLASSROOM,
        xPercent=34.9, yPercent=53.6,
        latitude=12.108540, longitude=-86.257206,
        floorLevel=1, isOutdoorAccessPoint=False
    ))
    subgraph.addNode(Node(
        nodeId="c_lab_acai_108",
        name="Laboratorio de Computación ACAI-Erasmus+ (C108)",
        category=CampusCategory.CLASSROOM,
        xPercent=34.9, yPercent=53.7,
        latitude=12.108531, longitude=-86.257233,
        floorLevel=1, isOutdoorAccessPoint=False
    ))
    subgraph.addNode(Node(
        nodeId="c_auditorium_109",
        name="Auditorio C109",
        category=CampusCategory.AUDITORIUM,
        xPercent=35.0, yPercent=53.8,
        latitude=12.108581, longitude=-86.257279,
        floorLevel=1, isOutdoorAccessPoint=False
    ))
    subgraph.addNode(Node(
        nodeId="c_mapa_uam_f1",
        name="Mapa UAM (Entrada Edificio C)",
        category=CampusCategory.ADMINISTRATIVE,
        xPercent=34.6, yPercent=53.4,
        latitude=12.108446, longitude=-86.257021,
        floorLevel=1, isOutdoorAccessPoint=True
    ))
    subgraph.addNode(Node(
        nodeId="c_ramp_f1",
        name="Rampa Accesible Edificio C",
        category=CampusCategory.ACCESSIBLE_RAMP,
        xPercent=34.5, yPercent=53.4,
        latitude=12.108394, longitude=-86.256997,
        floorLevel=1, isOutdoorAccessPoint=True
    ))
    subgraph.addNode(Node(
        nodeId="c_stairs_left_f1",
        name="Escaleras Izquierda Edificio C (Piso 1)",
        category=CampusCategory.STAIRS,
        xPercent=34.0, yPercent=53.0,
        latitude=12.108422, longitude=-86.256732,
        floorLevel=1, isOutdoorAccessPoint=True
    ))
    subgraph.addNode(Node(
        nodeId="c_stairs_right_f1",
        name="Escaleras Derecha Edificio C (Piso 1)",
        category=CampusCategory.STAIRS,
        xPercent=35.1, yPercent=53.9,
        latitude=12.108511, longitude=-86.257316,
        floorLevel=1, isOutdoorAccessPoint=True
    ))

    # =========================================================================
    # FLOOR 2 (SEGUNDO PISO) — Exact left-to-right order (C201..C211)
    # =========================================================================
    subgraph.addNode(Node(
        nodeId="c_lab_201",
        name="Laboratorio de Computación C201",
        category=CampusCategory.CLASSROOM,
        xPercent=34.1, yPercent=53.1,
        latitude=12.108453, longitude=-86.256760,
        floorLevel=2, isOutdoorAccessPoint=False
    ))
    subgraph.addNode(Node(
        nodeId="c_lab_202",
        name="Laboratorio de Computación C202",
        category=CampusCategory.CLASSROOM,
        xPercent=34.1, yPercent=53.0,
        latitude=12.108415, longitude=-86.256742,
        floorLevel=2, isOutdoorAccessPoint=False
    ))
    subgraph.addNode(Node(
        nodeId="c_lab_mac_203",
        name="Laboratorio MAC C203",
        category=CampusCategory.CLASSROOM,
        xPercent=34.2, yPercent=53.1,
        latitude=12.108528, longitude=-86.256800,
        floorLevel=2, isOutdoorAccessPoint=False
    ))
    subgraph.addNode(Node(
        nodeId="c_lab_204",
        name="Laboratorio de Computación C204",
        category=CampusCategory.CLASSROOM,
        xPercent=34.5, yPercent=53.3,
        latitude=12.108510, longitude=-86.256951,
        floorLevel=2, isOutdoorAccessPoint=False
    ))
    subgraph.addNode(Node(
        nodeId="c_fountain_f2",
        name="Bebedero de Agua (Edificio C - Piso 2)",
        category=CampusCategory.DRINKING_FOUNTAIN,
        xPercent=34.5, yPercent=53.3,
        latitude=12.108510, longitude=-86.256951,
        floorLevel=2, isOutdoorAccessPoint=False
    ))
    subgraph.addNode(Node(
        nodeId="c_lab_205",
        name="Laboratorio de Computación C205",
        category=CampusCategory.CLASSROOM,
        xPercent=34.6, yPercent=53.4,
        latitude=12.108433, longitude=-86.257043,
        floorLevel=2, isOutdoorAccessPoint=False
    ))
    subgraph.addNode(Node(
        nodeId="c_warehouse_206",
        name="Bodega de Logística Académica (C206)",
        category=CampusCategory.ADMINISTRATIVE,
        xPercent=34.6, yPercent=53.4,
        latitude=12.108435, longitude=-86.257044,
        floorLevel=2, isOutdoorAccessPoint=False
    ))
    subgraph.addNode(Node(
        nodeId="c_restrooms_men",
        name="Servicios Sanitarios Hombres (Edificio C - Piso 2)",
        category=CampusCategory.RESTROOM,
        xPercent=34.7, yPercent=53.5,
        latitude=12.108423, longitude=-86.257051,
        floorLevel=2, isOutdoorAccessPoint=False
    ))
    subgraph.addNode(Node(
        nodeId="c_restrooms_women",
        name="Servicios Sanitarios Mujeres (Edificio C - Piso 2)",
        category=CampusCategory.RESTROOM,
        xPercent=34.7, yPercent=53.5,
        latitude=12.108423, longitude=-86.257051,
        floorLevel=2, isOutdoorAccessPoint=False
    ))
    subgraph.addNode(Node(
        nodeId="c_room_209",
        name="Aula C209",
        category=CampusCategory.CLASSROOM,
        xPercent=34.9, yPercent=53.6,
        latitude=12.108496, longitude=-86.257203,
        floorLevel=2, isOutdoorAccessPoint=False
    ))
    subgraph.addNode(Node(
        nodeId="c_room_210",
        name="Aula C210",
        category=CampusCategory.CLASSROOM,
        xPercent=34.9, yPercent=53.6,
        latitude=12.108491, longitude=-86.257192,
        floorLevel=2, isOutdoorAccessPoint=False
    ))
    subgraph.addNode(Node(
        nodeId="c_room_211",
        name="Aula C211",
        category=CampusCategory.CLASSROOM,
        xPercent=35.0, yPercent=53.7,
        latitude=12.108500, longitude=-86.257267,
        floorLevel=2, isOutdoorAccessPoint=False
    ))
    subgraph.addNode(Node(
        nodeId="c_mapa_uam_f2",
        name="Mapa UAM (Edificio C - Piso 2)",
        category=CampusCategory.ADMINISTRATIVE,
        xPercent=34.7, yPercent=53.5,
        latitude=12.108423, longitude=-86.257051,
        floorLevel=2, isOutdoorAccessPoint=False
    ))
    subgraph.addNode(Node(
        nodeId="c_stairs_left_f2",
        name="Escaleras Izquierda Edificio C (Piso 2)",
        category=CampusCategory.STAIRS,
        xPercent=34.0, yPercent=53.0,
        latitude=12.108422, longitude=-86.256732,
        floorLevel=2, isOutdoorAccessPoint=False
    ))
    subgraph.addNode(Node(
        nodeId="c_stairs_right_f2",
        name="Escaleras Derecha Edificio C (Piso 2)",
        category=CampusCategory.STAIRS,
        xPercent=35.1, yPercent=53.9,
        latitude=12.108511, longitude=-86.257316,
        floorLevel=2, isOutdoorAccessPoint=False
    ))

    # =========================================================================
    # FLOOR 3 (TERCER PISO) — Exact left-to-right order (C301..C310)
    # =========================================================================
    subgraph.addNode(Node(
        nodeId="c_room_301",
        name="Aula C301",
        category=CampusCategory.CLASSROOM,
        xPercent=34.2, yPercent=53.1,
        latitude=12.108406, longitude=-86.256819,
        floorLevel=3, isOutdoorAccessPoint=False
    ))
    subgraph.addNode(Node(
        nodeId="c_room_302",
        name="Aula C302",
        category=CampusCategory.CLASSROOM,
        xPercent=34.2, yPercent=53.1,
        latitude=12.108418, longitude=-86.256821,
        floorLevel=3, isOutdoorAccessPoint=False
    ))
    subgraph.addNode(Node(
        nodeId="c_room_303",
        name="Aula C303",
        category=CampusCategory.CLASSROOM,
        xPercent=34.3, yPercent=53.2,
        latitude=12.108434, longitude=-86.256861,
        floorLevel=3, isOutdoorAccessPoint=False
    ))
    subgraph.addNode(Node(
        nodeId="c_room_304",
        name="Aula C304",
        category=CampusCategory.CLASSROOM,
        xPercent=34.6, yPercent=53.4,
        latitude=12.108415, longitude=-86.257020,
        floorLevel=3, isOutdoorAccessPoint=False
    ))
    subgraph.addNode(Node(
        nodeId="c_room_305",
        name="Aula C305",
        category=CampusCategory.CLASSROOM,
        xPercent=34.65, yPercent=53.4,
        latitude=12.108408, longitude=-86.257028,
        floorLevel=3, isOutdoorAccessPoint=False
    ))
    subgraph.addNode(Node(
        nodeId="c_compras_306",
        name="Coordinación de Compras (C306)",
        category=CampusCategory.ADMINISTRATIVE,
        xPercent=34.7, yPercent=53.4,
        latitude=12.108402, longitude=-86.257035,
        floorLevel=3, isOutdoorAccessPoint=False
    ))
    subgraph.addNode(Node(
        nodeId="c_room_307",
        name="Aula C307",
        category=CampusCategory.CLASSROOM,
        xPercent=34.7, yPercent=53.5,
        latitude=12.108395, longitude=-86.257064,
        floorLevel=3, isOutdoorAccessPoint=False
    ))
    subgraph.addNode(Node(
        nodeId="c_room_308",
        name="Aula C308",
        category=CampusCategory.CLASSROOM,
        xPercent=34.8, yPercent=53.5,
        latitude=12.108397, longitude=-86.257083,
        floorLevel=3, isOutdoorAccessPoint=False
    ))
    subgraph.addNode(Node(
        nodeId="c_room_309",
        name="Aula C309",
        category=CampusCategory.CLASSROOM,
        xPercent=35.0, yPercent=53.7,
        latitude=12.108420, longitude=-86.257240,
        floorLevel=3, isOutdoorAccessPoint=False
    ))
    subgraph.addNode(Node(
        nodeId="c_room_310",
        name="Aula C310",
        category=CampusCategory.CLASSROOM,
        xPercent=35.1, yPercent=53.8,
        latitude=12.108376, longitude=-86.257292,
        floorLevel=3, isOutdoorAccessPoint=False
    ))
    subgraph.addNode(Node(
        nodeId="c_stairs_ac_f3",
        name="Escaleras de Conexión Edificios A y C (Piso 3)",
        category=CampusCategory.STAIRS,
        xPercent=33.9, yPercent=52.9,
        latitude=12.108424, longitude=-86.256697,
        floorLevel=3, isOutdoorAccessPoint=False
    ))
    subgraph.addNode(Node(
        nodeId="c_stairs_right_f3",
        name="Escaleras Derecha Edificio C (Piso 3)",
        category=CampusCategory.STAIRS,
        xPercent=35.1, yPercent=53.9,
        latitude=12.108511, longitude=-86.257316,
        floorLevel=3, isOutdoorAccessPoint=False
    ))

    # =========================================================================
    # CORRIDORS / WALKWAYS - FLOOR 1 (PLANTA BAJA)
    # =========================================================================
    subgraph.addBidirectionalWalkway(
        "c_stairs_left_f1", "c_auditorium_101",
        _calcDist(12.108422, -86.256732, 12.108528, -86.256743, 11.8),
        isAccessible=True,
        forwardInstruction="Avanza hacia el Auditorio C101.",
        backwardInstruction="Avanza hacia las escaleras izquierda del Edificio C."
    )
    subgraph.addBidirectionalWalkway(
        "c_auditorium_101", "c_room_102",
        _calcDist(12.108528, -86.256743, 12.108549, -86.256848, 11.7),
        isAccessible=True,
        forwardInstruction="Avanza por el pasillo hacia el Aula C102.",
        backwardInstruction="Avanza hacia el Auditorio C101."
    )
    subgraph.addBidirectionalWalkway(
        "c_room_102", "c_room_103",
        _calcDist(12.108549, -86.256848, 12.108527, -86.256908, 7.0),
        isAccessible=True,
        forwardInstruction="Avanza por el pasillo hacia el Aula C103.",
        backwardInstruction="Avanza hacia el Aula C102."
    )
    subgraph.addBidirectionalWalkway(
        "c_room_103", "c_room_104",
        _calcDist(12.108527, -86.256908, 12.108583, -86.256918, 6.3),
        isAccessible=True,
        forwardInstruction="Avanza hacia el Aula C104.",
        backwardInstruction="Avanza hacia el Aula C103."
    )
    subgraph.addBidirectionalWalkway(
        "c_room_103", "c_fountain_f1",
        2.0,
        isAccessible=True,
        forwardInstruction="Avanza al bebedero de agua junto al Aula C103.",
        backwardInstruction="Regresa al Aula C103."
    )
    subgraph.addBidirectionalWalkway(
        "c_room_103", "c_cashier",
        12.0,
        isAccessible=True,
        forwardInstruction="Avanza hacia el área central de Caja UAM y atención financiera.",
        backwardInstruction="Avanza hacia el Aula C103."
    )
    subgraph.addBidirectionalWalkway(
        "c_cashier", "c_mapa_uam_f1",
        2.0,
        isAccessible=True,
        forwardInstruction="Avanza hacia el Mapa UAM y directorio de entrada.",
        backwardInstruction="Avanza hacia las ventanillas de Caja UAM."
    )
    subgraph.addBidirectionalWalkway(
        "c_mapa_uam_f1", "c_ramp_f1",
        _calcDist(12.108446, -86.257021, 12.108394, -86.256997, 6.3),
        isAccessible=True,
        forwardInstruction="Avanza hacia la rampa accesible de acceso exterior.",
        backwardInstruction="Avanza hacia el Mapa UAM y Caja UAM."
    )
    subgraph.addBidirectionalWalkway(
        "c_cashier", "c_treasury_105",
        13.0,
        isAccessible=True,
        forwardInstruction="Avanza por el corredor hacia Tesorería (C105).",
        backwardInstruction="Avanza hacia Caja UAM."
    )
    subgraph.addBidirectionalWalkway(
        "c_room_104", "c_treasury_105",
        _calcDist(12.108583, -86.256918, 12.108557, -86.257120, 15.0),
        isAccessible=True,
        forwardInstruction="Avanza hacia Tesorería (C105).",
        backwardInstruction="Avanza hacia el Aula C104."
    )
    subgraph.addBidirectionalWalkway(
        "c_treasury_105", "c_room_106",
        _calcDist(12.108557, -86.257120, 12.108522, -86.257194, 8.9),
        isAccessible=True,
        forwardInstruction="Avanza por el pasillo hacia el Aula C106.",
        backwardInstruction="Avanza hacia Tesorería (C105)."
    )
    subgraph.addBidirectionalWalkway(
        "c_room_106", "c_lab_mac_107",
        _calcDist(12.108522, -86.257194, 12.108540, -86.257206, 2.4),
        isAccessible=True,
        forwardInstruction="Avanza hacia el Laboratorio MAC C107.",
        backwardInstruction="Avanza hacia el Aula C106."
    )
    subgraph.addBidirectionalWalkway(
        "c_lab_mac_107", "c_lab_acai_108",
        _calcDist(12.108540, -86.257206, 12.108531, -86.257233, 3.1),
        isAccessible=True,
        forwardInstruction="Avanza hacia el Laboratorio ACAI-Erasmus+ (C108).",
        backwardInstruction="Avanza hacia el Laboratorio MAC C107."
    )
    subgraph.addBidirectionalWalkway(
        "c_lab_acai_108", "c_auditorium_109",
        _calcDist(12.108531, -86.257233, 12.108581, -86.257279, 7.5),
        isAccessible=True,
        forwardInstruction="Avanza hacia el Auditorio C109.",
        backwardInstruction="Avanza hacia el Laboratorio ACAI-Erasmus+ (C108)."
    )
    subgraph.addBidirectionalWalkway(
        "c_auditorium_109", "c_stairs_right_f1",
        _calcDist(12.108581, -86.257279, 12.108511, -86.257316, 8.8),
        isAccessible=True,
        forwardInstruction="Avanza hacia las escaleras derecha del Edificio C.",
        backwardInstruction="Avanza hacia el Auditorio C109."
    )

    # =========================================================================
    # VERTICAL CONNECTORS (STAIRS: F1 <-> F2 <-> F3)
    # =========================================================================
    subgraph.addBidirectionalWalkway(
        "c_stairs_left_f1", "c_stairs_left_f2",
        4.0,
        isAccessible=False,
        forwardInstruction="Sube las escaleras izquierda al Segundo Piso (Laboratorios C201 a C205).",
        backwardInstruction="Baja las escaleras izquierda a la Planta Baja."
    )
    subgraph.addBidirectionalWalkway(
        "c_stairs_left_f2", "c_stairs_ac_f3",
        4.0,
        isAccessible=False,
        forwardInstruction="Sube las escaleras hacia el Tercer Piso (Aulas C301 a C310).",
        backwardInstruction="Baja las escaleras hacia el Segundo Piso."
    )
    subgraph.addBidirectionalWalkway(
        "c_stairs_right_f1", "c_stairs_right_f2",
        4.0,
        isAccessible=False,
        forwardInstruction="Sube las escaleras derecha al Segundo Piso (Aulas C209 a C211).",
        backwardInstruction="Baja las escaleras derecha a la Planta Baja."
    )
    subgraph.addBidirectionalWalkway(
        "c_stairs_right_f2", "c_stairs_right_f3",
        4.0,
        isAccessible=False,
        forwardInstruction="Sube las escaleras derecha al Tercer Piso (Aulas C309 y C310).",
        backwardInstruction="Baja las escaleras derecha al Segundo Piso."
    )

    # =========================================================================
    # CORRIDORS / WALKWAYS - FLOOR 2 (SEGUNDO PISO)
    # =========================================================================
    subgraph.addBidirectionalWalkway(
        "c_stairs_left_f2", "c_lab_201",
        3.6,
        isAccessible=True,
        forwardInstruction="Avanza hacia el Laboratorio de Computación C201.",
        backwardInstruction="Avanza hacia las escaleras izquierda."
    )
    subgraph.addBidirectionalWalkway(
        "c_lab_201", "c_lab_202",
        4.6,
        isAccessible=True,
        forwardInstruction="Avanza al Laboratorio de Computación C202.",
        backwardInstruction="Avanza al Laboratorio de Computación C201."
    )
    subgraph.addBidirectionalWalkway(
        "c_lab_202", "c_lab_mac_203",
        9.3,
        isAccessible=True,
        forwardInstruction="Avanza por el corredor hacia el Laboratorio MAC C203.",
        backwardInstruction="Avanza hacia el Laboratorio C202."
    )
    subgraph.addBidirectionalWalkway(
        "c_lab_mac_203", "c_lab_204",
        14.2,
        isAccessible=True,
        forwardInstruction="Avanza por el corredor hacia el Laboratorio de Computación C204.",
        backwardInstruction="Avanza hacia el Laboratorio MAC C203."
    )
    subgraph.addBidirectionalWalkway(
        "c_lab_204", "c_fountain_f2",
        2.0,
        isAccessible=True,
        forwardInstruction="Avanza al bebedero de agua junto al Lab C204.",
        backwardInstruction="Regresa al Laboratorio C204."
    )
    subgraph.addBidirectionalWalkway(
        "c_lab_204", "c_lab_205",
        11.0,
        isAccessible=True,
        forwardInstruction="Avanza por el pasillo hacia el Laboratorio de Computación C205.",
        backwardInstruction="Avanza hacia el Laboratorio C204."
    )
    subgraph.addBidirectionalWalkway(
        "c_lab_205", "c_warehouse_206",
        2.0,
        isAccessible=True,
        forwardInstruction="Avanza a la Bodega de Logística Académica (C206).",
        backwardInstruction="Regresa al Laboratorio C205."
    )
    subgraph.addBidirectionalWalkway(
        "c_warehouse_206", "c_restrooms_men",
        2.5,
        isAccessible=True,
        forwardInstruction="Avanza hacia los servicios sanitarios de hombres.",
        backwardInstruction="Avanza hacia la bodega de logística C206."
    )
    subgraph.addBidirectionalWalkway(
        "c_restrooms_men", "c_restrooms_women",
        2.0,
        isAccessible=True,
        forwardInstruction="Accede a los servicios sanitarios de mujeres.",
        backwardInstruction="Accede a los servicios sanitarios de hombres."
    )
    subgraph.addBidirectionalWalkway(
        "c_restrooms_women", "c_mapa_uam_f2",
        2.0,
        isAccessible=True,
        forwardInstruction="Avanza hacia el Mapa UAM y directorio del segundo piso.",
        backwardInstruction="Avanza hacia los servicios sanitarios."
    )
    # Exact left-to-right corridor order: C209 -> C210 -> C211
    subgraph.addBidirectionalWalkway(
        "c_mapa_uam_f2", "c_room_209",
        14.5,
        isAccessible=True,
        forwardInstruction="Avanza por el corredor hacia el Aula C209.",
        backwardInstruction="Avanza hacia los servicios sanitarios y Mapa UAM."
    )
    subgraph.addBidirectionalWalkway(
        "c_room_209", "c_room_210",
        2.0,
        isAccessible=True,
        forwardInstruction="Avanza al Aula C210.",
        backwardInstruction="Avanza al Aula C209."
    )
    subgraph.addBidirectionalWalkway(
        "c_room_210", "c_room_211",
        6.2,
        isAccessible=True,
        forwardInstruction="Avanza por el corredor hacia el Aula C211.",
        backwardInstruction="Avanza hacia el Aula C210."
    )
    subgraph.addBidirectionalWalkway(
        "c_room_211", "c_stairs_right_f2",
        5.5,
        isAccessible=True,
        forwardInstruction="Avanza hacia las escaleras derecha del segundo piso.",
        backwardInstruction="Avanza hacia el Aula C211."
    )

    # =========================================================================
    # CORRIDORS / WALKWAYS - FLOOR 3 (TERCER PISO) — C301..C310
    # =========================================================================
    subgraph.addBidirectionalWalkway(
        "c_stairs_ac_f3", "c_room_301",
        13.2,
        isAccessible=True,
        forwardInstruction="Avanza por el pasillo hacia el Aula C301.",
        backwardInstruction="Avanza hacia las escaleras de conexión entre Edificios A y C."
    )
    subgraph.addBidirectionalWalkway(
        "c_room_301", "c_room_302",
        2.0,
        isAccessible=True,
        forwardInstruction="Avanza al Aula C302 contigua.",
        backwardInstruction="Regresa al Aula C301."
    )
    subgraph.addBidirectionalWalkway(
        "c_room_302", "c_room_303",
        4.7,
        isAccessible=True,
        forwardInstruction="Avanza por el pasillo hacia el Aula C303.",
        backwardInstruction="Avanza hacia el Aula C302."
    )
    subgraph.addBidirectionalWalkway(
        "c_room_303", "c_room_304",
        14.8,
        isAccessible=True,
        forwardInstruction="Avanza hacia el Aula C304.",
        backwardInstruction="Avanza hacia el Aula C303."
    )
    subgraph.addBidirectionalWalkway(
        "c_room_304", "c_room_305",
        2.0,
        isAccessible=True,
        forwardInstruction="Avanza hacia el Aula C305.",
        backwardInstruction="Avanza hacia el Aula C304."
    )
    subgraph.addBidirectionalWalkway(
        "c_room_305", "c_compras_306",
        2.0,
        isAccessible=True,
        forwardInstruction="Avanza hacia la Coordinación de Compras (C306).",
        backwardInstruction="Avanza hacia el Aula C305."
    )
    subgraph.addBidirectionalWalkway(
        "c_compras_306", "c_room_307",
        3.2,
        isAccessible=True,
        forwardInstruction="Avanza hacia el Aula C307.",
        backwardInstruction="Avanza hacia la Coordinación de Compras (C306)."
    )
    subgraph.addBidirectionalWalkway(
        "c_room_307", "c_room_308",
        2.1,
        isAccessible=True,
        forwardInstruction="Avanza al Aula C308.",
        backwardInstruction="Avanza al Aula C307."
    )
    subgraph.addBidirectionalWalkway(
        "c_room_308", "c_room_309",
        14.6,
        isAccessible=True,
        forwardInstruction="Avanza por el corredor hacia el Aula C309.",
        backwardInstruction="Avanza hacia el Aula C308."
    )
    subgraph.addBidirectionalWalkway(
        "c_room_309", "c_room_310",
        7.5,
        isAccessible=True,
        forwardInstruction="Avanza hacia el Aula C310.",
        backwardInstruction="Avanza hacia el Aula C309."
    )
    subgraph.addBidirectionalWalkway(
        "c_room_310", "c_stairs_right_f3",
        15.2,
        isAccessible=True,
        forwardInstruction="Avanza hacia las escaleras derecha del tercer piso.",
        backwardInstruction="Avanza hacia el Aula C310."
    )
    subgraph.addBidirectionalWalkway(
        "c_room_309", "c_stairs_right_f3",
        13.1,
        isAccessible=True,
        forwardInstruction="Avanza hacia las escaleras derecha del tercer piso.",
        backwardInstruction="Avanza hacia el Aula C309."
    )

    # =========================================================================
    # SEARCH QUERY ALIASES & KEYWORDS (includes hyphenated forms for search)
    # =========================================================================
    aliases = {
        # Floor 1
        "c-101": "c_auditorium_101", "c101": "c_auditorium_101",
        "auditorio c101": "c_auditorium_101", "auditorio 101": "c_auditorium_101", "auditoriumC101": "c_auditorium_101",
        "c-102": "c_room_102", "c102": "c_room_102", "classroomC102": "c_room_102",
        "c-103": "c_room_103", "c103": "c_room_103", "classroomC103": "c_room_103",
        "c-104": "c_room_104", "c104": "c_room_104", "classroomC104": "c_room_104",
        "c-105": "c_treasury_105", "c105": "c_treasury_105", "tesoreria": "c_treasury_105", "treasuryC105": "c_treasury_105",
        "bebedero piso 1": "c_fountain_f1", "bebedero c1": "c_fountain_f1", "drinkingFountainC1": "c_fountain_f1",
        "caja": "c_cashier", "caja uam": "c_cashier", "pagos": "c_cashier", "cashierUamC": "c_cashier",
        "mapa": "c_mapa_uam_f1", "mapa uam": "c_mapa_uam_f1", "directorio": "c_mapa_uam_f1", "mapUamC_F1": "c_mapa_uam_f1",
        "rampa": "c_ramp_f1", "rampla": "c_ramp_f1", "rampa accesible": "c_ramp_f1", "rampC_F1": "c_ramp_f1",
        "c-106": "c_room_106", "c106": "c_room_106", "classroomC106": "c_room_106",
        "mac 107": "c_lab_mac_107", "c-107": "c_lab_mac_107", "c107": "c_lab_mac_107",
        "laboratorio mac 107": "c_lab_mac_107", "macLabC107": "c_lab_mac_107",
        "c-108": "c_lab_acai_108", "c108": "c_lab_acai_108", "acai": "c_lab_acai_108",
        "erasmus": "c_lab_acai_108", "acai erasmus": "c_lab_acai_108", "lab acai": "c_lab_acai_108", "erasmusLabC108": "c_lab_acai_108",
        "auditorio 109": "c_auditorium_109", "c-109": "c_auditorium_109", "c109": "c_auditorium_109", "auditoriumC109": "c_auditorium_109",
        "escaleras izquierda": "c_stairs_left_f1", "escaleras derecha": "c_stairs_right_f1",

        # Floor 2
        "c-201": "c_lab_201", "c201": "c_lab_201", "lab 201": "c_lab_201", "computerLabC201": "c_lab_201",
        "c-202": "c_lab_202", "c202": "c_lab_202", "lab 202": "c_lab_202", "computerLabC202": "c_lab_202",
        "mac c203": "c_lab_mac_203", "c-203": "c_lab_mac_203", "c203": "c_lab_mac_203",
        "laboratorio mac c203": "c_lab_mac_203", "macLabC203": "c_lab_mac_203",
        "c-204": "c_lab_204", "c204": "c_lab_204", "lab 204": "c_lab_204", "computerLabC204": "c_lab_204",
        "c-205": "c_lab_205", "c205": "c_lab_205", "lab 205": "c_lab_205", "computerLabC205": "c_lab_205",
        "c-206": "c_warehouse_206", "c206": "c_warehouse_206", "bodega": "c_warehouse_206",
        "logistica": "c_warehouse_206", "bodega de logistica academica": "c_warehouse_206", "warehouseC206": "c_warehouse_206",
        "baños hombres": "c_restrooms_men", "banos hombres": "c_restrooms_men",
        "sanitarios hombres": "c_restrooms_men", "baños": "c_restrooms_men", "banos": "c_restrooms_men",
        "restroomsMenC2": "c_restrooms_men",
        "baños mujeres": "c_restrooms_women", "banos mujeres": "c_restrooms_women",
        "sanitarios mujeres": "c_restrooms_women", "restroomsWomenC2": "c_restrooms_women",
        "bebedero": "c_fountain_f2", "bebedero piso 2": "c_fountain_f2", "agua": "c_fountain_f2", "drinkingFountainC2": "c_fountain_f2",
        "c-209": "c_room_209", "c209": "c_room_209", "classroomC209": "c_room_209",
        "c-210": "c_room_210", "c210": "c_room_210", "classroomC210": "c_room_210",
        "c-211": "c_room_211", "c211": "c_room_211", "classroomC211": "c_room_211",

        # Floor 3
        "c-301": "c_room_301", "c301": "c_room_301", "classroomC301": "c_room_301",
        "c-302": "c_room_302", "c302": "c_room_302", "classroomC302": "c_room_302",
        "c-303": "c_room_303", "c303": "c_room_303", "classroomC303": "c_room_303",
        "c-304": "c_room_304", "c304": "c_room_304", "classroomC304": "c_room_304",
        "c-305": "c_room_305", "c305": "c_room_305", "classroomC305": "c_room_305",
        "c-306": "c_compras_306", "c306": "c_compras_306", "compras": "c_compras_306",
        "coordinacion de compras": "c_compras_306", "procurementCoordC306": "c_compras_306",
        "c-307": "c_room_307", "c307": "c_room_307", "classroomC307": "c_room_307",
        "c-308": "c_room_308", "c308": "c_room_308", "classroomC308": "c_room_308",
        "c-309": "c_room_309", "c309": "c_room_309", "classroomC309": "c_room_309",
        "c-310": "c_room_310", "c310": "c_room_310", "classroomC310": "c_room_310",
        "escaleras a y c": "c_stairs_ac_f3",
    }

    for alias, targetNodeId in aliases.items():
        subgraph.registerRoomAlias(alias, targetNodeId)

    return subgraph


# Singleton instance of Building C child graph
buildingCSubgraph = buildBuildingCSubgraph()
