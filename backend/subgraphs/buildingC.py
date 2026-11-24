"""
buildingC.py
================================================================================
BUILDING C (AULAS, LABS DE COMPUTACIÓN & TESORERÍA) SUBGRAPH / CHILD GRAPH
================================================================================
Indoor child graph representation for Building C (Edificio C), covering 3 floors:
Floor 1 (Planta Baja):
- Escaleras izquierda: 12.108422, -86.256732
- Auditorio C101: 12.108528, -86.256743
- Aula C102: 12.108549, -86.256848
- Aula C103: 12.108527, -86.256908
- Aula C104: 12.108583, -86.256918
- Bebedero de agua (Piso 1): 12.108527, -86.256908
- C105, Tesorería: 12.108557, -86.257120
- Caja UAM: 12.108446, -86.257021
- Mapa UAM: 12.108446, -86.257021
- Rampa accesible: 12.108394, -86.256997
- Aula C106: 12.108522, -86.257194
- Laboratorio MAC 107: 12.108540, -86.257206
- Laboratorio de computación Acai-Erasmus + (C-108): 12.108531, -86.257233
- Auditorio 109: 12.108581, -86.257279
- Escaleras derecha: 12.108511, -86.257316

Floor 2 (Segundo Piso):
- Escaleras izquierda (Piso 2): 12.108422, -86.256732
- Lab computación C201: 12.108453, -86.256760
- Lab computación C202: 12.108415, -86.256742
- Lab MAC C203: 12.108528, -86.256800
- Lab computación C204: 12.108510, -86.256951
- Bebedero de agua (Piso 2): 12.108510, -86.256951
- Lab computación C205: 12.108433, -86.257043
- C206, Bodega de logística académica: 12.108435, -86.257044
- Sanitarios hombres: 12.108423, -86.257051
- Sanitarios mujeres: 12.108423, -86.257051
- Mapa UAM: 12.108423, -86.257051
- Aula C209: 12.108496, -86.257203
- Aula C210: 12.108491, -86.257192
- Aula C211: 12.108500, -86.257267
- Escaleras derecha (Piso 2): 12.108511, -86.257316

Floor 3 (Tercer Piso):
- Escaleras del edificio A y C: 12.108424, -86.256697
- A-301 Estudio audiovisual (3er piso): 12.108418, -86.256706
- Aula C-301: 12.108406, -86.256819
- Aula C-302: 12.108418, -86.256821
- Aula C-303: 12.108434, -86.256861
- Aula C-304: 12.108415, -86.257020
- C-306 Coordinación de compras: 12.108402, -86.257035
- Aula C-307: 12.108395, -86.257064
- Aula C-308: 12.108397, -86.257083
- Aula C-309: 12.108420, -86.257240
- Aula C-310: 12.108376, -86.257292
- Escaleras derecha (Piso 3): 12.108511, -86.257316
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
        description="Edificio C de Aulas de Clases, Laboratorios de Computación ACAI-Erasmus y MAC, Caja UAM y Tesorería."
    )

    # =========================================================================
    # FLOOR 1 (PLANTA BAJA)
    # =========================================================================

    # 1. Escaleras Izquierda (P1)
    subgraph.addNode(Node(
        nodeId="c_stairs_left_f1",
        name="Escaleras Izquierda Edificio C (Piso 1)",
        category=CampusCategory.STAIRS,
        xPercent=34.0, yPercent=53.0,
        latitude=12.108422, longitude=-86.256732,
        floorLevel=1, isOutdoorAccessPoint=True
    ))

    # 2. Auditorio C101
    subgraph.addNode(Node(
        nodeId="c_auditorium_101",
        name="Auditorio C-101",
        category=CampusCategory.AUDITORIUM,
        xPercent=34.1, yPercent=53.1,
        latitude=12.108528, longitude=-86.256743,
        floorLevel=1, isOutdoorAccessPoint=False
    ))

    # 3. Aula C102
    subgraph.addNode(Node(
        nodeId="c_room_102",
        name="Aula C-102",
        category=CampusCategory.CLASSROOM,
        xPercent=34.3, yPercent=53.2,
        latitude=12.108549, longitude=-86.256848,
        floorLevel=1, isOutdoorAccessPoint=False
    ))

    # 4. Aula C103
    subgraph.addNode(Node(
        nodeId="c_room_103",
        name="Aula C-103",
        category=CampusCategory.CLASSROOM,
        xPercent=34.4, yPercent=53.3,
        latitude=12.108527, longitude=-86.256908,
        floorLevel=1, isOutdoorAccessPoint=False
    ))

    # 5. Aula C104
    subgraph.addNode(Node(
        nodeId="c_room_104",
        name="Aula C-104",
        category=CampusCategory.CLASSROOM,
        xPercent=34.5, yPercent=53.3,
        latitude=12.108583, longitude=-86.256918,
        floorLevel=1, isOutdoorAccessPoint=False
    ))

    # 6. Bebedero de Agua (Piso 1)
    subgraph.addNode(Node(
        nodeId="c_fountain_f1",
        name="Bebedero de Agua (Edificio C - Piso 1)",
        category=CampusCategory.DRINKING_FOUNTAIN,
        xPercent=34.4, yPercent=53.3,
        latitude=12.108527, longitude=-86.256908,
        floorLevel=1, isOutdoorAccessPoint=False
    ))

    # 7. C105, Tesorería
    subgraph.addNode(Node(
        nodeId="c_treasury_105",
        name="Tesorería UAM (C-105)",
        category=CampusCategory.ADMINISTRATIVE,
        xPercent=34.7, yPercent=53.5,
        latitude=12.108557, longitude=-86.257120,
        floorLevel=1, isOutdoorAccessPoint=False
    ))

    # 8. Caja UAM
    subgraph.addNode(Node(
        nodeId="c_cashier",
        name="Caja UAM (Atención Financiera)",
        category=CampusCategory.ADMINISTRATIVE,
        xPercent=34.6, yPercent=53.4,
        latitude=12.108446, longitude=-86.257021,
        floorLevel=1, isOutdoorAccessPoint=False
    ))

    # 9. Mapa UAM (Directorio Planta Baja)
    subgraph.addNode(Node(
        nodeId="c_mapa_uam_f1",
        name="Mapa UAM (Entrada Edificio C)",
        category=CampusCategory.ADMINISTRATIVE,
        xPercent=34.6, yPercent=53.4,
        latitude=12.108446, longitude=-86.257021,
        floorLevel=1, isOutdoorAccessPoint=True
    ))

    # 10. Rampa Accesible
    subgraph.addNode(Node(
        nodeId="c_ramp_f1",
        name="Rampa Accesible Edificio C",
        category=CampusCategory.ACCESSIBLE_RAMP,
        xPercent=34.5, yPercent=53.4,
        latitude=12.108394, longitude=-86.256997,
        floorLevel=1, isOutdoorAccessPoint=True
    ))

    # 11. Aula C106
    subgraph.addNode(Node(
        nodeId="c_room_106",
        name="Aula C-106",
        category=CampusCategory.CLASSROOM,
        xPercent=34.8, yPercent=53.6,
        latitude=12.108522, longitude=-86.257194,
        floorLevel=1, isOutdoorAccessPoint=False
    ))

    # 12. Laboratorio MAC 107
    subgraph.addNode(Node(
        nodeId="c_lab_mac_107",
        name="Laboratorio MAC C-107",
        category=CampusCategory.CLASSROOM,
        xPercent=34.9, yPercent=53.6,
        latitude=12.108540, longitude=-86.257206,
        floorLevel=1, isOutdoorAccessPoint=False
    ))

    # 13. Laboratorio de Computación ACAI-Erasmus + (C-108)
    subgraph.addNode(Node(
        nodeId="c_lab_acai_108",
        name="Laboratorio de Computación ACAI-Erasmus+ (C-108)",
        category=CampusCategory.CLASSROOM,
        xPercent=34.9, yPercent=53.7,
        latitude=12.108531, longitude=-86.257233,
        floorLevel=1, isOutdoorAccessPoint=False
    ))

    # 14. Auditorio C109
    subgraph.addNode(Node(
        nodeId="c_auditorium_109",
        name="Auditorio C-109",
        category=CampusCategory.AUDITORIUM,
        xPercent=35.0, yPercent=53.8,
        latitude=12.108581, longitude=-86.257279,
        floorLevel=1, isOutdoorAccessPoint=False
    ))

    # 15. Escaleras Derecha (P1)
    subgraph.addNode(Node(
        nodeId="c_stairs_right_f1",
        name="Escaleras Derecha Edificio C (Piso 1)",
        category=CampusCategory.STAIRS,
        xPercent=35.1, yPercent=53.9,
        latitude=12.108511, longitude=-86.257316,
        floorLevel=1, isOutdoorAccessPoint=True
    ))

    # =========================================================================
    # FLOOR 2 (SEGUNDO PISO)
    # =========================================================================

    # 16. Escaleras Izquierda (P2)
    subgraph.addNode(Node(
        nodeId="c_stairs_left_f2",
        name="Escaleras Izquierda Edificio C (Piso 2)",
        category=CampusCategory.STAIRS,
        xPercent=34.0, yPercent=53.0,
        latitude=12.108422, longitude=-86.256732,
        floorLevel=2, isOutdoorAccessPoint=False
    ))

    # 17. Lab Computación C201
    subgraph.addNode(Node(
        nodeId="c_lab_201",
        name="Laboratorio de Computación C-201",
        category=CampusCategory.CLASSROOM,
        xPercent=34.1, yPercent=53.1,
        latitude=12.108453, longitude=-86.256760,
        floorLevel=2, isOutdoorAccessPoint=False
    ))

    # 18. Lab Computación C202
    subgraph.addNode(Node(
        nodeId="c_lab_202",
        name="Laboratorio de Computación C-202",
        category=CampusCategory.CLASSROOM,
        xPercent=34.1, yPercent=53.0,
        latitude=12.108415, longitude=-86.256742,
        floorLevel=2, isOutdoorAccessPoint=False
    ))

    # 19. Lab MAC C203
    subgraph.addNode(Node(
        nodeId="c_lab_mac_203",
        name="Laboratorio MAC C-203",
        category=CampusCategory.CLASSROOM,
        xPercent=34.2, yPercent=53.1,
        latitude=12.108528, longitude=-86.256800,
        floorLevel=2, isOutdoorAccessPoint=False
    ))

    # 20. Lab Computación C204
    subgraph.addNode(Node(
        nodeId="c_lab_204",
        name="Laboratorio de Computación C-204",
        category=CampusCategory.CLASSROOM,
        xPercent=34.5, yPercent=53.3,
        latitude=12.108510, longitude=-86.256951,
        floorLevel=2, isOutdoorAccessPoint=False
    ))

    # 21. Bebedero de Agua (Piso 2)
    subgraph.addNode(Node(
        nodeId="c_fountain_f2",
        name="Bebedero de Agua (Edificio C - Piso 2)",
        category=CampusCategory.DRINKING_FOUNTAIN,
        xPercent=34.5, yPercent=53.3,
        latitude=12.108510, longitude=-86.256951,
        floorLevel=2, isOutdoorAccessPoint=False
    ))

    # 22. Lab Computación C205
    subgraph.addNode(Node(
        nodeId="c_lab_205",
        name="Laboratorio de Computación C-205",
        category=CampusCategory.CLASSROOM,
        xPercent=34.6, yPercent=53.4,
        latitude=12.108433, longitude=-86.257043,
        floorLevel=2, isOutdoorAccessPoint=False
    ))

    # 23. C206, Bodega de Logística Académica
    subgraph.addNode(Node(
        nodeId="c_warehouse_206",
        name="Bodega de Logística Académica (C-206)",
        category=CampusCategory.ADMINISTRATIVE,
        xPercent=34.6, yPercent=53.4,
        latitude=12.108435, longitude=-86.257044,
        floorLevel=2, isOutdoorAccessPoint=False
    ))

    # 24. Sanitarios Hombres (Piso 2)
    subgraph.addNode(Node(
        nodeId="c_restrooms_men",
        name="Servicios Sanitarios Hombres (Edificio C - Piso 2)",
        category=CampusCategory.RESTROOM,
        xPercent=34.7, yPercent=53.5,
        latitude=12.108423, longitude=-86.257051,
        floorLevel=2, isOutdoorAccessPoint=False
    ))

    # 25. Sanitarios Mujeres (Piso 2)
    subgraph.addNode(Node(
        nodeId="c_restrooms_women",
        name="Servicios Sanitarios Mujeres (Edificio C - Piso 2)",
        category=CampusCategory.RESTROOM,
        xPercent=34.7, yPercent=53.5,
        latitude=12.108423, longitude=-86.257051,
        floorLevel=2, isOutdoorAccessPoint=False
    ))

    # 26. Mapa UAM (Piso 2)
    subgraph.addNode(Node(
        nodeId="c_mapa_uam_f2",
        name="Mapa UAM (Edificio C - Piso 2)",
        category=CampusCategory.ADMINISTRATIVE,
        xPercent=34.7, yPercent=53.5,
        latitude=12.108423, longitude=-86.257051,
        floorLevel=2, isOutdoorAccessPoint=False
    ))

    # 27. Aula C209
    subgraph.addNode(Node(
        nodeId="c_room_209",
        name="Aula C-209",
        category=CampusCategory.CLASSROOM,
        xPercent=34.9, yPercent=53.6,
        latitude=12.108496, longitude=-86.257203,
        floorLevel=2, isOutdoorAccessPoint=False
    ))

    # 28. Aula C210
    subgraph.addNode(Node(
        nodeId="c_room_210",
        name="Aula C-210",
        category=CampusCategory.CLASSROOM,
        xPercent=34.9, yPercent=53.6,
        latitude=12.108491, longitude=-86.257192,
        floorLevel=2, isOutdoorAccessPoint=False
    ))

    # 29. Aula C211
    subgraph.addNode(Node(
        nodeId="c_room_211",
        name="Aula C-211",
        category=CampusCategory.CLASSROOM,
        xPercent=35.0, yPercent=53.7,
        latitude=12.108500, longitude=-86.257267,
        floorLevel=2, isOutdoorAccessPoint=False
    ))

    # 30. Escaleras Derecha (Piso 2)
    subgraph.addNode(Node(
        nodeId="c_stairs_right_f2",
        name="Escaleras Derecha Edificio C (Piso 2)",
        category=CampusCategory.STAIRS,
        xPercent=35.1, yPercent=53.9,
        latitude=12.108511, longitude=-86.257316,
        floorLevel=2, isOutdoorAccessPoint=False
    ))

    # =========================================================================
    # FLOOR 3 (TERCER PISO)
    # =========================================================================

    # 31. Escaleras A y C (Piso 3)
    subgraph.addNode(Node(
        nodeId="c_stairs_ac_f3",
        name="Escaleras de Conexión Edificios A y C (Piso 3)",
        category=CampusCategory.STAIRS,
        xPercent=33.9, yPercent=52.9,
        latitude=12.108424, longitude=-86.256697,
        floorLevel=3, isOutdoorAccessPoint=False
    ))

    # 32. Estudio Audiovisual A-301
    subgraph.addNode(Node(
        nodeId="c_studio_a301",
        name="Estudio Audiovisual A-301 (Piso 3)",
        category=CampusCategory.CLASSROOM,
        xPercent=33.9, yPercent=52.9,
        latitude=12.108418, longitude=-86.256706,
        floorLevel=3, isOutdoorAccessPoint=False
    ))

    # 33. Aula C301
    subgraph.addNode(Node(
        nodeId="c_room_301",
        name="Aula C-301",
        category=CampusCategory.CLASSROOM,
        xPercent=34.2, yPercent=53.1,
        latitude=12.108406, longitude=-86.256819,
        floorLevel=3, isOutdoorAccessPoint=False
    ))

    # 34. Aula C302
    subgraph.addNode(Node(
        nodeId="c_room_302",
        name="Aula C-302",
        category=CampusCategory.CLASSROOM,
        xPercent=34.2, yPercent=53.1,
        latitude=12.108418, longitude=-86.256821,
        floorLevel=3, isOutdoorAccessPoint=False
    ))

    # 35. Aula C303
    subgraph.addNode(Node(
        nodeId="c_room_303",
        name="Aula C-303",
        category=CampusCategory.CLASSROOM,
        xPercent=34.3, yPercent=53.2,
        latitude=12.108434, longitude=-86.256861,
        floorLevel=3, isOutdoorAccessPoint=False
    ))

    # 36. Aula C304
    subgraph.addNode(Node(
        nodeId="c_room_304",
        name="Aula C-304",
        category=CampusCategory.CLASSROOM,
        xPercent=34.6, yPercent=53.4,
        latitude=12.108415, longitude=-86.257020,
        floorLevel=3, isOutdoorAccessPoint=False
    ))

    # 37. C306, Coordinación de Compras
    subgraph.addNode(Node(
        nodeId="c_compras_306",
        name="Coordinación de Compras (C-306)",
        category=CampusCategory.ADMINISTRATIVE,
        xPercent=34.7, yPercent=53.4,
        latitude=12.108402, longitude=-86.257035,
        floorLevel=3, isOutdoorAccessPoint=False
    ))

    # 38. Aula C307
    subgraph.addNode(Node(
        nodeId="c_room_307",
        name="Aula C-307",
        category=CampusCategory.CLASSROOM,
        xPercent=34.7, yPercent=53.5,
        latitude=12.108395, longitude=-86.257064,
        floorLevel=3, isOutdoorAccessPoint=False
    ))

    # 39. Aula C308
    subgraph.addNode(Node(
        nodeId="c_room_308",
        name="Aula C-308",
        category=CampusCategory.CLASSROOM,
        xPercent=34.8, yPercent=53.5,
        latitude=12.108397, longitude=-86.257083,
        floorLevel=3, isOutdoorAccessPoint=False
    ))

    # 40. Aula C309
    subgraph.addNode(Node(
        nodeId="c_room_309",
        name="Aula C-309",
        category=CampusCategory.CLASSROOM,
        xPercent=35.0, yPercent=53.7,
        latitude=12.108420, longitude=-86.257240,
        floorLevel=3, isOutdoorAccessPoint=False
    ))

    # 41. Aula C310
    subgraph.addNode(Node(
        nodeId="c_room_310",
        name="Aula C-310",
        category=CampusCategory.CLASSROOM,
        xPercent=35.1, yPercent=53.8,
        latitude=12.108376, longitude=-86.257292,
        floorLevel=3, isOutdoorAccessPoint=False
    ))

    # 42. Escaleras Derecha (Piso 3)
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

    # Escaleras Izquierda <-> Auditorio C101
    subgraph.addBidirectionalWalkway(
        "c_stairs_left_f1", "c_auditorium_101",
        _calcDist(12.108422, -86.256732, 12.108528, -86.256743, 11.8),
        isAccessible=True,
        forwardInstruction="Avanza 12m hacia el Auditorio C-101.",
        backwardInstruction="Avanza 12m hacia las escaleras izquierda del Edificio C."
    )

    # Auditorio C101 <-> Aula C102
    subgraph.addBidirectionalWalkway(
        "c_auditorium_101", "c_room_102",
        _calcDist(12.108528, -86.256743, 12.108549, -86.256848, 11.7),
        isAccessible=True,
        forwardInstruction="Avanza 12m por el pasillo hacia el Aula C-102.",
        backwardInstruction="Avanza 12m hacia el Auditorio C-101."
    )

    # Aula C102 <-> Aula C103
    subgraph.addBidirectionalWalkway(
        "c_room_102", "c_room_103",
        _calcDist(12.108549, -86.256848, 12.108527, -86.256908, 7.0),
        isAccessible=True,
        forwardInstruction="Avanza 7m por el pasillo hacia el Aula C-103.",
        backwardInstruction="Avanza 7m hacia el Aula C-102."
    )

    # Aula C103 <-> Aula C104
    subgraph.addBidirectionalWalkway(
        "c_room_103", "c_room_104",
        _calcDist(12.108527, -86.256908, 12.108583, -86.256918, 6.3),
        isAccessible=True,
        forwardInstruction="Avanza 6m hacia el Aula C-104.",
        backwardInstruction="Avanza 6m hacia el Aula C-103."
    )

    # Aula C103 <-> Bebedero Piso 1
    subgraph.addBidirectionalWalkway(
        "c_room_103", "c_fountain_f1",
        2.0,
        isAccessible=True,
        forwardInstruction="Avanza al bebedero de agua junto al Aula C-103.",
        backwardInstruction="Regresa al Aula C-103."
    )

    # Aula C103 <-> Caja UAM
    subgraph.addBidirectionalWalkway(
        "c_room_103", "c_cashier",
        12.0,
        isAccessible=True,
        forwardInstruction="Avanza 12m hacia el área central de Caja UAM y atención financiera.",
        backwardInstruction="Avanza 12m hacia el Aula C-103."
    )

    # Caja UAM <-> Mapa UAM
    subgraph.addBidirectionalWalkway(
        "c_cashier", "c_mapa_uam_f1",
        2.0,
        isAccessible=True,
        forwardInstruction="Avanza hacia el Mapa UAM y directorio de entrada.",
        backwardInstruction="Avanza hacia las ventanillas de Caja UAM."
    )

    # Mapa UAM <-> Rampa Accesible
    subgraph.addBidirectionalWalkway(
        "c_mapa_uam_f1", "c_ramp_f1",
        _calcDist(12.108446, -86.257021, 12.108394, -86.256997, 6.3),
        isAccessible=True,
        forwardInstruction="Avanza 6m hacia la rampa accesible de acceso exterior.",
        backwardInstruction="Avanza 6m hacia el Mapa UAM y Caja UAM."
    )

    # Caja UAM <-> Tesorería C105
    subgraph.addBidirectionalWalkway(
        "c_cashier", "c_treasury_105",
        13.0,
        isAccessible=True,
        forwardInstruction="Avanza 13m por el corredor hacia Tesorería (C-105).",
        backwardInstruction="Avanza 13m hacia Caja UAM."
    )

    # Aula C104 <-> Tesorería C105
    subgraph.addBidirectionalWalkway(
        "c_room_104", "c_treasury_105",
        _calcDist(12.108583, -86.256918, 12.108557, -86.257120, 15.0),
        isAccessible=True,
        forwardInstruction="Avanza 15m hacia Tesorería (C-105).",
        backwardInstruction="Avanza 15m hacia el Aula C-104."
    )

    # Tesorería C105 <-> Aula C106
    subgraph.addBidirectionalWalkway(
        "c_treasury_105", "c_room_106",
        _calcDist(12.108557, -86.257120, 12.108522, -86.257194, 8.9),
        isAccessible=True,
        forwardInstruction="Avanza 9m por el pasillo hacia el Aula C-106.",
        backwardInstruction="Avanza 9m hacia Tesorería (C-105)."
    )

    # Aula C106 <-> Lab MAC C107
    subgraph.addBidirectionalWalkway(
        "c_room_106", "c_lab_mac_107",
        _calcDist(12.108522, -86.257194, 12.108540, -86.257206, 2.4),
        isAccessible=True,
        forwardInstruction="Avanza hacia el Laboratorio MAC C-107.",
        backwardInstruction="Avanza hacia el Aula C-106."
    )

    # Lab MAC C107 <-> Lab ACAI-Erasmus C108
    subgraph.addBidirectionalWalkway(
        "c_lab_mac_107", "c_lab_acai_108",
        _calcDist(12.108540, -86.257206, 12.108531, -86.257233, 3.1),
        isAccessible=True,
        forwardInstruction="Avanza 3m hacia el Laboratorio ACAI-Erasmus+ (C-108).",
        backwardInstruction="Avanza 3m hacia el Laboratorio MAC C-107."
    )

    # Lab ACAI C108 <-> Auditorio C109
    subgraph.addBidirectionalWalkway(
        "c_lab_acai_108", "c_auditorium_109",
        _calcDist(12.108531, -86.257233, 12.108581, -86.257279, 7.5),
        isAccessible=True,
        forwardInstruction="Avanza 7.5m hacia el Auditorio C-109.",
        backwardInstruction="Avanza 7.5m hacia el Laboratorio ACAI-Erasmus+ (C-108)."
    )

    # Auditorio C109 <-> Escaleras Derecha F1
    subgraph.addBidirectionalWalkway(
        "c_auditorium_109", "c_stairs_right_f1",
        _calcDist(12.108581, -86.257279, 12.108511, -86.257316, 8.8),
        isAccessible=True,
        forwardInstruction="Avanza 9m hacia las escaleras derecha del Edificio C.",
        backwardInstruction="Avanza 9m hacia el Auditorio C-109."
    )

    # =========================================================================
    # VERTICAL CONNECTORS (STAIRS: F1 <-> F2 <-> F3)
    # =========================================================================

    # Escaleras Izquierda: F1 <-> F2
    subgraph.addBidirectionalWalkway(
        "c_stairs_left_f1", "c_stairs_left_f2",
        4.0,
        isAccessible=False,
        forwardInstruction="Sube las escaleras izquierda al Segundo Piso (Laboratorios de Computación C-201 a C-205).",
        backwardInstruction="Baja las escaleras izquierda a la Planta Baja."
    )

    # Escaleras Izquierda F2 <-> Escaleras A-C F3
    subgraph.addBidirectionalWalkway(
        "c_stairs_left_f2", "c_stairs_ac_f3",
        4.0,
        isAccessible=False,
        forwardInstruction="Sube las escaleras hacia el Tercer Piso (Estudio Audiovisual A-301, Aulas C301-C310).",
        backwardInstruction="Baja las escaleras hacia el Segundo Piso."
    )

    # Escaleras Derecha: F1 <-> F2
    subgraph.addBidirectionalWalkway(
        "c_stairs_right_f1", "c_stairs_right_f2",
        4.0,
        isAccessible=False,
        forwardInstruction="Sube las escaleras derecha al Segundo Piso (Aulas C209-C211).",
        backwardInstruction="Baja las escaleras derecha a la Planta Baja."
    )

    # Escaleras Derecha: F2 <-> F3
    subgraph.addBidirectionalWalkway(
        "c_stairs_right_f2", "c_stairs_right_f3",
        4.0,
        isAccessible=False,
        forwardInstruction="Sube las escaleras derecha al Tercer Piso (Aulas C309-C310).",
        backwardInstruction="Baja las escaleras derecha al Segundo Piso."
    )

    # =========================================================================
    # CORRIDORS / WALKWAYS - FLOOR 2 (SEGUNDO PISO)
    # =========================================================================

    # Escaleras Izquierda F2 <-> Lab C202
    subgraph.addBidirectionalWalkway(
        "c_stairs_left_f2", "c_lab_202",
        3.6,
        isAccessible=True,
        forwardInstruction="Avanza hacia el Laboratorio de Computación C-202.",
        backwardInstruction="Avanza hacia las escaleras izquierda."
    )

    # Lab C202 <-> Lab C201
    subgraph.addBidirectionalWalkway(
        "c_lab_202", "c_lab_201",
        4.6,
        isAccessible=True,
        forwardInstruction="Avanza al Laboratorio de Computación C-201.",
        backwardInstruction="Avanza al Laboratorio de Computación C-202."
    )

    # Lab C201 <-> Lab MAC C203
    subgraph.addBidirectionalWalkway(
        "c_lab_201", "c_lab_mac_203",
        9.3,
        isAccessible=True,
        forwardInstruction="Avanza 9m por el corredor hacia el Laboratorio MAC C-203.",
        backwardInstruction="Avanza 9m hacia el Laboratorio C-201."
    )

    # Lab MAC C203 <-> Lab C204
    subgraph.addBidirectionalWalkway(
        "c_lab_mac_203", "c_lab_204",
        14.2,
        isAccessible=True,
        forwardInstruction="Avanza 14m por el corredor hacia el Laboratorio de Computación C-204.",
        backwardInstruction="Avanza 14m hacia el Laboratorio MAC C-203."
    )

    # Lab C204 <-> Bebedero Piso 2
    subgraph.addBidirectionalWalkway(
        "c_lab_204", "c_fountain_f2",
        2.0,
        isAccessible=True,
        forwardInstruction="Avanza al bebedero de agua junto al Lab C-204.",
        backwardInstruction="Regresa al Laboratorio C-204."
    )

    # Lab C204 <-> Lab C205
    subgraph.addBidirectionalWalkway(
        "c_lab_204", "c_lab_205",
        11.0,
        isAccessible=True,
        forwardInstruction="Avanza 11m por el pasillo hacia el Laboratorio de Computación C-205.",
        backwardInstruction="Avanza 11m hacia el Laboratorio C-204."
    )

    # Lab C205 <-> Bodega C206
    subgraph.addBidirectionalWalkway(
        "c_lab_205", "c_warehouse_206",
        2.0,
        isAccessible=True,
        forwardInstruction="Avanza a la Bodega de Logística Académica (C-206).",
        backwardInstruction="Regresa al Laboratorio C-205."
    )

    # Bodega C206 <-> Sanitarios Hombres
    subgraph.addBidirectionalWalkway(
        "c_warehouse_206", "c_restrooms_men",
        2.5,
        isAccessible=True,
        forwardInstruction="Avanza hacia los servicios sanitarios de hombres.",
        backwardInstruction="Avanza hacia la bodega de logística C-206."
    )

    # Sanitarios Hombres <-> Sanitarios Mujeres
    subgraph.addBidirectionalWalkway(
        "c_restrooms_men", "c_restrooms_women",
        2.0,
        isAccessible=True,
        forwardInstruction="Accede a los servicios sanitarios de mujeres.",
        backwardInstruction="Accede a los servicios sanitarios de hombres."
    )

    # Sanitarios <-> Mapa UAM Piso 2
    subgraph.addBidirectionalWalkway(
        "c_restrooms_women", "c_mapa_uam_f2",
        2.0,
        isAccessible=True,
        forwardInstruction="Avanza hacia el Mapa UAM y directorio del segundo piso.",
        backwardInstruction="Avanza hacia los servicios sanitarios."
    )

    # Mapa UAM Piso 2 <-> Aula C210
    subgraph.addBidirectionalWalkway(
        "c_mapa_uam_f2", "c_room_210",
        14.5,
        isAccessible=True,
        forwardInstruction="Avanza 15m por el corredor oeste hacia el Aula C-210.",
        backwardInstruction="Avanza 15m hacia los servicios sanitarios y Mapa UAM."
    )

    # Aula C210 <-> Aula C209
    subgraph.addBidirectionalWalkway(
        "c_room_210", "c_room_209",
        2.0,
        isAccessible=True,
        forwardInstruction="Avanza al Aula C-209.",
        backwardInstruction="Avanza al Aula C-210."
    )

    # Aula C209 <-> Aula C211
    subgraph.addBidirectionalWalkway(
        "c_room_209", "c_room_211",
        6.2,
        isAccessible=True,
        forwardInstruction="Avanza 6m por el corredor hacia el Aula C-211.",
        backwardInstruction="Avanza 6m hacia el Aula C-209."
    )

    # Aula C211 <-> Escaleras Derecha F2
    subgraph.addBidirectionalWalkway(
        "c_room_211", "c_stairs_right_f2",
        5.5,
        isAccessible=True,
        forwardInstruction="Avanza 5.5m hacia las escaleras derecha del segundo piso.",
        backwardInstruction="Avanza 5.5m hacia el Aula C-211."
    )

    # =========================================================================
    # CORRIDORS / WALKWAYS - FLOOR 3 (TERCER PISO)
    # =========================================================================

    # Escaleras A-C <-> Estudio Audiovisual A-301
    subgraph.addBidirectionalWalkway(
        "c_stairs_ac_f3", "c_studio_a301",
        1.2,
        isAccessible=True,
        forwardInstruction="Accede al Estudio Audiovisual A-301.",
        backwardInstruction="Avanza hacia las escaleras de conexión entre Edificios A y C."
    )

    # Estudio A301 <-> Aula C301
    subgraph.addBidirectionalWalkway(
        "c_studio_a301", "c_room_301",
        12.4,
        isAccessible=True,
        forwardInstruction="Avanza 12m por el pasillo hacia el Aula C-301.",
        backwardInstruction="Avanza 12m hacia el Estudio Audiovisual A-301."
    )

    # Aula C301 <-> Aula C302
    subgraph.addBidirectionalWalkway(
        "c_room_301", "c_room_302",
        1.4,
        isAccessible=True,
        forwardInstruction="Avanza al Aula C-302 contigua.",
        backwardInstruction="Regresa al Aula C-301."
    )

    # Aula C302 <-> Aula C303
    subgraph.addBidirectionalWalkway(
        "c_room_302", "c_room_303",
        4.7,
        isAccessible=True,
        forwardInstruction="Avanza 5m por el pasillo hacia el Aula C-303.",
        backwardInstruction="Avanza 5m hacia el Aula C-302."
    )

    # Aula C303 <-> Aula C304
    subgraph.addBidirectionalWalkway(
        "c_room_303", "c_room_304",
        14.8,
        isAccessible=True,
        forwardInstruction="Avanza 15m hacia el Aula C-304.",
        backwardInstruction="Avanza 15m hacia el Aula C-303."
    )

    # Aula C304 <-> C306 Coordinación de Compras
    subgraph.addBidirectionalWalkway(
        "c_room_304", "c_compras_306",
        2.2,
        isAccessible=True,
        forwardInstruction="Avanza hacia la Coordinación de Compras (C-306).",
        backwardInstruction="Avanza hacia el Aula C-304."
    )

    # C306 Compras <-> Aula C307
    subgraph.addBidirectionalWalkway(
        "c_compras_306", "c_room_307",
        3.2,
        isAccessible=True,
        forwardInstruction="Avanza 3m hacia el Aula C-307.",
        backwardInstruction="Avanza 3m hacia la Coordinación de Compras (C-306)."
    )

    # Aula C307 <-> Aula C308
    subgraph.addBidirectionalWalkway(
        "c_room_307", "c_room_308",
        2.1,
        isAccessible=True,
        forwardInstruction="Avanza al Aula C-308.",
        backwardInstruction="Avanza al Aula C-307."
    )

    # Aula C308 <-> Aula C309
    subgraph.addBidirectionalWalkway(
        "c_room_308", "c_room_309",
        14.6,
        isAccessible=True,
        forwardInstruction="Avanza 15m por el corredor hacia el Aula C-309.",
        backwardInstruction="Avanza 15m hacia el Aula C-308."
    )

    # Aula C309 <-> Aula C310
    subgraph.addBidirectionalWalkway(
        "c_room_309", "c_room_310",
        7.5,
        isAccessible=True,
        forwardInstruction="Avanza 7.5m hacia el Aula C-310.",
        backwardInstruction="Avanza 7.5m hacia el Aula C-309."
    )

    # Aula C310 <-> Escaleras Derecha F3
    subgraph.addBidirectionalWalkway(
        "c_room_310", "c_stairs_right_f3",
        15.2,
        isAccessible=True,
        forwardInstruction="Avanza 15m hacia las escaleras derecha del tercer piso.",
        backwardInstruction="Avanza 15m hacia el Aula C-310."
    )

    # Aula C309 <-> Escaleras Derecha F3
    subgraph.addBidirectionalWalkway(
        "c_room_309", "c_stairs_right_f3",
        13.1,
        isAccessible=True,
        forwardInstruction="Avanza 13m hacia las escaleras derecha del tercer piso.",
        backwardInstruction="Avanza 13m hacia el Aula C-309."
    )

    # =========================================================================
    # SEARCH QUERY ALIASES & KEYWORDS
    # =========================================================================
    aliases = {
        # Floor 1
        "c-101": "c_auditorium_101",
        "c101": "c_auditorium_101",
        "auditorio c101": "c_auditorium_101",
        "auditorio 101": "c_auditorium_101",

        "c-102": "c_room_102",
        "c102": "c_room_102",

        "c-103": "c_room_103",
        "c103": "c_room_103",

        "c-104": "c_room_104",
        "c104": "c_room_104",

        "c-105": "c_treasury_105",
        "c105": "c_treasury_105",
        "tesoreria": "c_treasury_105",

        "bebedero piso 1": "c_fountain_f1",
        "bebedero c1": "c_fountain_f1",

        "caja": "c_cashier",
        "caja uam": "c_cashier",
        "pagos": "c_cashier",

        "mapa": "c_mapa_uam_f1",
        "mapa uam": "c_mapa_uam_f1",
        "directorio": "c_mapa_uam_f1",

        "rampa": "c_ramp_f1",
        "rampla": "c_ramp_f1",
        "rampa accesible": "c_ramp_f1",

        "c-106": "c_room_106",
        "c106": "c_room_106",

        "mac 107": "c_lab_mac_107",
        "c-107": "c_lab_mac_107",
        "c107": "c_lab_mac_107",
        "laboratorio mac 107": "c_lab_mac_107",

        "c-108": "c_lab_acai_108",
        "c108": "c_lab_acai_108",
        "acai": "c_lab_acai_108",
        "erasmus": "c_lab_acai_108",
        "acai erasmus": "c_lab_acai_108",
        "lab acai": "c_lab_acai_108",

        "auditorio 109": "c_auditorium_109",
        "c-109": "c_auditorium_109",
        "c109": "c_auditorium_109",

        "escaleras izquierda": "c_stairs_left_f1",
        "escaleras derecha": "c_stairs_right_f1",

        # Floor 2
        "c-201": "c_lab_201",
        "c201": "c_lab_201",
        "lab 201": "c_lab_201",

        "c-202": "c_lab_202",
        "c202": "c_lab_202",
        "lab 202": "c_lab_202",

        "mac c203": "c_lab_mac_203",
        "c-203": "c_lab_mac_203",
        "c203": "c_lab_mac_203",
        "laboratorio mac c203": "c_lab_mac_203",

        "c-204": "c_lab_204",
        "c204": "c_lab_204",
        "lab 204": "c_lab_204",

        "c-205": "c_lab_205",
        "c205": "c_lab_205",
        "lab 205": "c_lab_205",

        "c-206": "c_warehouse_206",
        "c206": "c_warehouse_206",
        "bodega": "c_warehouse_206",
        "logistica": "c_warehouse_206",
        "bodega de logistica academica": "c_warehouse_206",

        "baños hombres": "c_restrooms_men",
        "banos hombres": "c_restrooms_men",
        "sanitarios hombres": "c_restrooms_men",
        "baños": "c_restrooms_men",
        "banos": "c_restrooms_men",

        "baños mujeres": "c_restrooms_women",
        "banos mujeres": "c_restrooms_women",
        "sanitarios mujeres": "c_restrooms_women",

        "bebedero": "c_fountain_f2",
        "bebedero piso 2": "c_fountain_f2",
        "agua": "c_fountain_f2",

        "c-209": "c_room_209",
        "c209": "c_room_209",

        "c-210": "c_room_210",
        "c210": "c_room_210",

        "c-211": "c_room_211",
        "c211": "c_room_211",

        # Floor 3
        "c-301": "c_room_301",
        "c301": "c_room_301",

        "c-302": "c_room_302",
        "c302": "c_room_302",

        "c-303": "c_room_303",
        "c303": "c_room_303",

        "c-304": "c_room_304",
        "c304": "c_room_304",

        "c-306": "c_compras_306",
        "c306": "c_compras_306",
        "compras": "c_compras_306",
        "coordinacion de compras": "c_compras_306",

        "c-307": "c_room_307",
        "c307": "c_room_307",

        "c-308": "c_room_308",
        "c308": "c_room_308",

        "c-309": "c_room_309",
        "c309": "c_room_309",

        "c-310": "c_room_310",
        "c310": "c_room_310",

        "a-301": "c_studio_a301",
        "a301": "c_studio_a301",
        "estudio audio visual": "c_studio_a301",
        "estudio audiovisual": "c_studio_a301",

        "escaleras a y c": "c_stairs_ac_f3",
    }

    for alias, targetNodeId in aliases.items():
        subgraph.registerRoomAlias(alias, targetNodeId)

    return subgraph


# Singleton instance of Building C child graph
buildingCSubgraph = buildBuildingCSubgraph()
