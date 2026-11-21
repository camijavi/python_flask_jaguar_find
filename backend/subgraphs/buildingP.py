"""
buildingP.py
================================================================================
BUILDING P (EDIFICIO COPÉRNICO) SUBGRAPH / CHILD GRAPH
================================================================================
Full indoor child graph representation for Building P (Edificio Copérnico),
including all 3 floors, classrooms (P101-P108, P201-P208, P301-P306), restrooms,
water fountains, stairwells (East, West, Exterior), ramp access from parking,
and inter-building connection to Building O.
================================================================================
"""

import math
from backend.graph.directedGraph import Node
from backend.data.campusCategories import CampusCategory
from backend.graph.geoUtils import CampusGeoUtils
from .buildingSubgraph import BuildingSubgraph


def _calcDist(lat1: float, lng1: float, lat2: float, lng2: float, minDist: float = 2.0) -> float:
    """Helper to calculate distance in meters, enforcing a sensible minimum for indoor steps."""
    d = CampusGeoUtils.calculateHaversineDistance(lat1, lng1, lat2, lng2)
    return max(minDist, round(d, 1))


def buildBuildingPSubgraph() -> BuildingSubgraph:
    """
    Constructs the official high-resolution child graph for Building P.
    """
    subgraph = BuildingSubgraph(
        buildingId="buildingP",
        name="Edificio P (Copérnico)",
        code="P",
        floors=[1, 2, 3],
        macroNodeId="buildingP",
        entranceNodeIds=[
            "p_stairs_f1_east",
            "p_stairs_f1_west",
            "p_ramp_parking",
            "p_stairs_f1_ext_left"
        ],
        description="Edificio de Aulas Copérnico y Observatorio Astronómico de la UAM."
    )

    # =========================================================================
    # FLOOR 1 (PRIMER PISO)
    # =========================================================================
    # Escaleras exteriores izquierdas
    subgraph.addNode(Node(
        nodeId="p_stairs_f1_ext_left",
        name="Escaleras del P (Izquierda / Exterior)",
        category=CampusCategory.STAIRS,
        xPercent=33.0, yPercent=27.0,
        latitude=12.107584, longitude=-86.256779,
        floorLevel=1, isOutdoorAccessPoint=True
    ))

    # Escalera este para subir al segundo piso
    subgraph.addNode(Node(
        nodeId="p_stairs_f1_east",
        name="Escaleras Este del P (Subir al Piso 2)",
        category=CampusCategory.STAIRS,
        xPercent=33.0, yPercent=27.0,
        latitude=12.107470, longitude=-86.256753,
        floorLevel=1, isOutdoorAccessPoint=True
    ))

    # Bebedero 1er piso
    subgraph.addNode(Node(
        nodeId="p_fountain_f1",
        name="Bebedero 1er Piso del P",
        category=CampusCategory.DRINKING_FOUNTAIN,
        xPercent=33.0, yPercent=27.0,
        latitude=12.107460, longitude=-86.256743,
        floorLevel=1, isOutdoorAccessPoint=False
    ))

    # Salón 101 del P
    subgraph.addNode(Node(
        nodeId="p_room_101",
        name="Salón P-101",
        category=CampusCategory.CLASSROOM,
        xPercent=33.0, yPercent=27.0,
        latitude=12.107460, longitude=-86.256743,
        floorLevel=1, isOutdoorAccessPoint=False
    ))

    # Salón 102 del P
    subgraph.addNode(Node(
        nodeId="p_room_102",
        name="Salón P-102",
        category=CampusCategory.CLASSROOM,
        xPercent=33.0, yPercent=27.0,
        latitude=12.107431, longitude=-86.256783,
        floorLevel=1, isOutdoorAccessPoint=False
    ))

    # Salón 103 del P
    subgraph.addNode(Node(
        nodeId="p_room_103",
        name="Salón P-103",
        category=CampusCategory.CLASSROOM,
        xPercent=33.0, yPercent=27.0,
        latitude=12.107439, longitude=-86.256947,
        floorLevel=1, isOutdoorAccessPoint=False
    ))

    # Salón 104 del P
    subgraph.addNode(Node(
        nodeId="p_room_104",
        name="Salón P-104",
        category=CampusCategory.CLASSROOM,
        xPercent=33.0, yPercent=27.0,
        latitude=12.107455, longitude=-86.256981,
        floorLevel=1, isOutdoorAccessPoint=False
    ))

    # Salón 105 del P
    subgraph.addNode(Node(
        nodeId="p_room_105",
        name="Salón P-105",
        category=CampusCategory.CLASSROOM,
        xPercent=33.0, yPercent=27.0,
        latitude=12.107453, longitude=-86.257149,
        floorLevel=1, isOutdoorAccessPoint=False
    ))

    # Salón 106 del P
    subgraph.addNode(Node(
        nodeId="p_room_106",
        name="Salón P-106",
        category=CampusCategory.CLASSROOM,
        xPercent=33.0, yPercent=27.0,
        latitude=12.107467, longitude=-86.257202,
        floorLevel=1, isOutdoorAccessPoint=False
    ))

    # Salón 107 del P
    subgraph.addNode(Node(
        nodeId="p_room_107",
        name="Salón P-107",
        category=CampusCategory.CLASSROOM,
        xPercent=33.0, yPercent=27.0,
        latitude=12.107450, longitude=-86.257270,
        floorLevel=1, isOutdoorAccessPoint=False
    ))

    # Salón 108 del P
    subgraph.addNode(Node(
        nodeId="p_room_108",
        name="Salón P-108",
        category=CampusCategory.CLASSROOM,
        xPercent=33.0, yPercent=27.0,
        latitude=12.107477, longitude=-86.257206,
        floorLevel=1, isOutdoorAccessPoint=False
    ))

    # Baños del P primer piso
    subgraph.addNode(Node(
        nodeId="p_restrooms_f1",
        name="Baños del P (Primer Piso)",
        category=CampusCategory.RESTROOM,
        xPercent=33.0, yPercent=27.0,
        latitude=12.107441, longitude=-86.257422,
        floorLevel=1, isOutdoorAccessPoint=False
    ))

    # Segundas Escaleras del P para subir al 2do piso (Oeste)
    subgraph.addNode(Node(
        nodeId="p_stairs_f1_west",
        name="Segundas Escaleras Oeste del P (Subir al Piso 2)",
        category=CampusCategory.STAIRS,
        xPercent=33.0, yPercent=27.0,
        latitude=12.107410, longitude=-86.257431,
        floorLevel=1, isOutdoorAccessPoint=True
    ))

    # Escaleras del P hacia el Edificio O
    subgraph.addNode(Node(
        nodeId="p_stairs_to_building_o",
        name="Escaleras del P hacia Edificio O",
        category=CampusCategory.STAIRS,
        xPercent=33.0, yPercent=27.0,
        latitude=12.107453, longitude=-86.257413,
        floorLevel=1, isOutdoorAccessPoint=True
    ))

    # Rampa del estacionamiento hacia el P (enfrente del O)
    subgraph.addNode(Node(
        nodeId="p_ramp_parking",
        name="Rampa del Estacionamiento hacia Edificio P ♿",
        category=CampusCategory.ACCESSIBLE_RAMP,
        xPercent=33.0, yPercent=27.0,
        latitude=12.106991, longitude=-86.258233,
        floorLevel=1, isOutdoorAccessPoint=True
    ))

    # =========================================================================
    # FLOOR 2 (SEGUNDO PISO)
    # =========================================================================
    # Escaleras Este Piso 2
    subgraph.addNode(Node(
        nodeId="p_stairs_f2_east",
        name="Escaleras Este del P (Piso 2)",
        category=CampusCategory.STAIRS,
        xPercent=33.0, yPercent=27.0,
        latitude=12.107470, longitude=-86.256753,
        floorLevel=2, isOutdoorAccessPoint=False
    ))

    # Salón 201
    subgraph.addNode(Node(
        nodeId="p_room_201",
        name="Salón P-201",
        category=CampusCategory.CLASSROOM,
        xPercent=33.0, yPercent=27.0,
        latitude=12.107484, longitude=-86.256721,
        floorLevel=2, isOutdoorAccessPoint=False
    ))

    # 2do bebedero del P en el 2do piso
    subgraph.addNode(Node(
        nodeId="p_fountain_f2_east",
        name="2do Bebedero del P (Piso 2 Este)",
        category=CampusCategory.DRINKING_FOUNTAIN,
        xPercent=33.0, yPercent=27.0,
        latitude=12.107434, longitude=-86.256781,
        floorLevel=2, isOutdoorAccessPoint=False
    ))

    # Salón 202
    subgraph.addNode(Node(
        nodeId="p_room_202",
        name="Salón P-202",
        category=CampusCategory.CLASSROOM,
        xPercent=33.0, yPercent=27.0,
        latitude=12.107428, longitude=-86.256817,
        floorLevel=2, isOutdoorAccessPoint=False
    ))

    # Salón 203
    subgraph.addNode(Node(
        nodeId="p_room_203",
        name="Salón P-203",
        category=CampusCategory.CLASSROOM,
        xPercent=33.0, yPercent=27.0,
        latitude=12.107447, longitude=-86.256957,
        floorLevel=2, isOutdoorAccessPoint=False
    ))

    # Salón 204
    subgraph.addNode(Node(
        nodeId="p_room_204",
        name="Salón P-204",
        category=CampusCategory.CLASSROOM,
        xPercent=33.0, yPercent=27.0,
        latitude=12.107434, longitude=-86.257043,
        floorLevel=2, isOutdoorAccessPoint=False
    ))

    # Salón 205
    subgraph.addNode(Node(
        nodeId="p_room_205",
        name="Salón P-205",
        category=CampusCategory.CLASSROOM,
        xPercent=33.0, yPercent=27.0,
        latitude=12.107492, longitude=-86.257090,
        floorLevel=2, isOutdoorAccessPoint=False
    ))

    # Salón 206
    subgraph.addNode(Node(
        nodeId="p_room_206",
        name="Salón P-206",
        category=CampusCategory.CLASSROOM,
        xPercent=33.0, yPercent=27.0,
        latitude=12.107413, longitude=-86.257153,
        floorLevel=2, isOutdoorAccessPoint=False
    ))

    # Salón 207
    subgraph.addNode(Node(
        nodeId="p_room_207",
        name="Salón P-207",
        category=CampusCategory.CLASSROOM,
        xPercent=33.0, yPercent=27.0,
        latitude=12.107427, longitude=-86.257217,
        floorLevel=2, isOutdoorAccessPoint=False
    ))

    # Salón 208
    subgraph.addNode(Node(
        nodeId="p_room_208",
        name="Salón P-208",
        category=CampusCategory.CLASSROOM,
        xPercent=33.0, yPercent=27.0,
        latitude=12.107402, longitude=-86.257297,
        floorLevel=2, isOutdoorAccessPoint=False
    ))

    # Bebedero del segundo piso del P (Oeste)
    subgraph.addNode(Node(
        nodeId="p_fountain_f2_west",
        name="Bebedero del P (Piso 2 Oeste)",
        category=CampusCategory.DRINKING_FOUNTAIN,
        xPercent=33.0, yPercent=27.0,
        latitude=12.107407, longitude=-86.257298,
        floorLevel=2, isOutdoorAccessPoint=False
    ))

    # Baños del segundo piso del P
    subgraph.addNode(Node(
        nodeId="p_restrooms_f2",
        name="Baños del P (Segundo Piso)",
        category=CampusCategory.RESTROOM,
        xPercent=33.0, yPercent=27.0,
        latitude=12.107480, longitude=-86.257337,
        floorLevel=2, isOutdoorAccessPoint=False
    ))

    # Segundas Escaleras Oeste Piso 2
    subgraph.addNode(Node(
        nodeId="p_stairs_f2_west",
        name="Segundas Escaleras Oeste del P (Piso 2)",
        category=CampusCategory.STAIRS,
        xPercent=33.0, yPercent=27.0,
        latitude=12.107410, longitude=-86.257431,
        floorLevel=2, isOutdoorAccessPoint=False
    ))

    # =========================================================================
    # FLOOR 3 (TERCER PISO)
    # =========================================================================
    # Escaleras Este Piso 3
    subgraph.addNode(Node(
        nodeId="p_stairs_f3_east",
        name="Escaleras Este del P (Piso 3)",
        category=CampusCategory.STAIRS,
        xPercent=33.0, yPercent=27.0,
        latitude=12.107470, longitude=-86.256753,
        floorLevel=3, isOutdoorAccessPoint=False
    ))

    # Salón 301
    subgraph.addNode(Node(
        nodeId="p_room_301",
        name="Salón P-301",
        category=CampusCategory.CLASSROOM,
        xPercent=33.0, yPercent=27.0,
        latitude=12.107461, longitude=-86.256717,
        floorLevel=3, isOutdoorAccessPoint=False
    ))

    # 1er bebedero del P 3er piso
    subgraph.addNode(Node(
        nodeId="p_fountain_f3",
        name="1er Bebedero del P (Piso 3)",
        category=CampusCategory.DRINKING_FOUNTAIN,
        xPercent=33.0, yPercent=27.0,
        latitude=12.107434, longitude=-86.256751,
        floorLevel=3, isOutdoorAccessPoint=False
    ))

    # Salón 301 (2do acceso)
    subgraph.addNode(Node(
        nodeId="p_room_301_b",
        name="Salón P-301 (Acceso 2)",
        category=CampusCategory.CLASSROOM,
        xPercent=33.0, yPercent=27.0,
        latitude=12.107462, longitude=-86.256862,
        floorLevel=3, isOutdoorAccessPoint=False
    ))

    # Salón 302
    subgraph.addNode(Node(
        nodeId="p_room_302",
        name="Salón P-302",
        category=CampusCategory.CLASSROOM,
        xPercent=33.0, yPercent=27.0,
        latitude=12.107443, longitude=-86.256934,
        floorLevel=3, isOutdoorAccessPoint=False
    ))

    # Salón 303
    subgraph.addNode(Node(
        nodeId="p_room_303",
        name="Salón P-303",
        category=CampusCategory.CLASSROOM,
        xPercent=33.0, yPercent=27.0,
        latitude=12.107442, longitude=-86.256936,
        floorLevel=3, isOutdoorAccessPoint=False
    ))

    # Salón 304
    subgraph.addNode(Node(
        nodeId="p_room_304",
        name="Salón P-304",
        category=CampusCategory.CLASSROOM,
        xPercent=33.0, yPercent=27.0,
        latitude=12.107443, longitude=-86.256999,
        floorLevel=3, isOutdoorAccessPoint=False
    ))

    # Salón 305
    subgraph.addNode(Node(
        nodeId="p_room_305",
        name="Salón P-305",
        category=CampusCategory.CLASSROOM,
        xPercent=33.0, yPercent=27.0,
        latitude=12.107454, longitude=-86.257114,
        floorLevel=3, isOutdoorAccessPoint=False
    ))

    # Salón 306
    subgraph.addNode(Node(
        nodeId="p_room_306",
        name="Salón P-306",
        category=CampusCategory.CLASSROOM,
        xPercent=33.0, yPercent=27.0,
        latitude=12.107461, longitude=-86.257145,
        floorLevel=3, isOutdoorAccessPoint=False
    ))

    # Salón 306 (segundo acceso)
    subgraph.addNode(Node(
        nodeId="p_room_306_b",
        name="Salón P-306 (Acceso 2)",
        category=CampusCategory.CLASSROOM,
        xPercent=33.0, yPercent=27.0,
        latitude=12.107435, longitude=-86.257136,
        floorLevel=3, isOutdoorAccessPoint=False
    ))

    # Baño del P 3er piso
    subgraph.addNode(Node(
        nodeId="p_restrooms_f3",
        name="Baños del P (Tercer Piso)",
        category=CampusCategory.RESTROOM,
        xPercent=33.0, yPercent=27.0,
        latitude=12.107468, longitude=-86.257189,
        floorLevel=3, isOutdoorAccessPoint=False
    ))

    # Segundas Escaleras Oeste Piso 3
    subgraph.addNode(Node(
        nodeId="p_stairs_f3_west",
        name="Segundas Escaleras Oeste del P (Piso 3)",
        category=CampusCategory.STAIRS,
        xPercent=33.0, yPercent=27.0,
        latitude=12.107410, longitude=-86.257431,
        floorLevel=3, isOutdoorAccessPoint=False
    ))

    # =========================================================================
    # CORRIDOR WALKWAYS & EDGES: FLOOR 1
    # =========================================================================
    subgraph.addBidirectionalCorridor(
        "p_stairs_f1_ext_left", "p_stairs_f1_east", 13.0, isAccessible=False,
        forwardInstruction="Baja por las escaleras exteriores hacia la entrada este del Edificio P.",
        backwardInstruction="Sube por las escaleras exteriores izquierdas."
    )
    subgraph.addBidirectionalCorridor(
        "p_stairs_f1_east", "p_fountain_f1", 1.6, isAccessible=True,
        forwardInstruction="Avanza 2m hacia el bebedero y entrada a Salón P-101.",
        backwardInstruction="Dirígete hacia las escaleras este del primer piso."
    )
    subgraph.addBidirectionalCorridor(
        "p_fountain_f1", "p_room_101", 1.5, isAccessible=True,
        forwardInstruction="Entra al Salón P-101.",
        backwardInstruction="Sal del Salón P-101 hacia el bebedero del pasillo."
    )
    subgraph.addBidirectionalCorridor(
        "p_room_101", "p_room_102", 5.4, isAccessible=True,
        forwardInstruction="Camina 5m por el pasillo oeste hacia el Salón P-102.",
        backwardInstruction="Camina 5m por el pasillo este hacia el Salón P-101."
    )
    subgraph.addBidirectionalCorridor(
        "p_room_102", "p_room_103", 17.9, isAccessible=True,
        forwardInstruction="Avanza 18m por el pasillo principal hacia el Salón P-103.",
        backwardInstruction="Avanza 18m por el pasillo este hacia el Salón P-102."
    )
    subgraph.addBidirectionalCorridor(
        "p_room_103", "p_room_104", 4.1, isAccessible=True,
        forwardInstruction="Avanza 4m hacia el Salón P-104.",
        backwardInstruction="Avanza 4m hacia el Salón P-103."
    )
    subgraph.addBidirectionalCorridor(
        "p_room_104", "p_room_105", 18.3, isAccessible=True,
        forwardInstruction="Continúa 18m por el pasillo central hacia el Salón P-105.",
        backwardInstruction="Continúa 18m hacia el Salón P-104."
    )
    subgraph.addBidirectionalCorridor(
        "p_room_105", "p_room_106", 6.0, isAccessible=True,
        forwardInstruction="Avanza 6m hacia el Salón P-106.",
        backwardInstruction="Avanza 6m hacia el Salón P-105."
    )
    subgraph.addBidirectionalCorridor(
        "p_room_106", "p_room_107", 7.6, isAccessible=True,
        forwardInstruction="Camina 7m hacia el Salón P-107.",
        backwardInstruction="Camina 7m hacia el Salón P-106."
    )
    subgraph.addBidirectionalCorridor(
        "p_room_107", "p_room_108", 7.6, isAccessible=True,
        forwardInstruction="Avanza hacia el Salón P-108.",
        backwardInstruction="Avanza hacia el Salón P-107."
    )
    subgraph.addBidirectionalCorridor(
        "p_room_108", "p_restrooms_f1", 23.8, isAccessible=True,
        forwardInstruction="Camina 24m hacia los baños del primer piso.",
        backwardInstruction="Camina 24m por el pasillo hacia el Salón P-108."
    )
    subgraph.addBidirectionalCorridor(
        "p_restrooms_f1", "p_stairs_f1_west", 3.6, isAccessible=True,
        forwardInstruction="Gira hacia las segundas escaleras oeste del primer piso.",
        backwardInstruction="Avanza hacia los baños del primer piso."
    )
    subgraph.addBidirectionalCorridor(
        "p_stairs_f1_west", "p_stairs_to_building_o", 5.2, isAccessible=False,
        forwardInstruction="Sal hacia las escaleras de interconexión con el Edificio O.",
        backwardInstruction="Entra hacia las escaleras oeste del Edificio P."
    )
    subgraph.addBidirectionalCorridor(
        "p_stairs_f1_west", "p_ramp_parking", 102.9, isAccessible=True,
        forwardInstruction="Toma la rampa exterior hacia el estacionamiento enfrente del Edificio O.",
        backwardInstruction="Sube por la rampa accesible hacia la entrada oeste del Edificio P."
    )
    subgraph.addBidirectionalCorridor(
        "p_room_108", "p_ramp_parking", 98.0, isAccessible=True,
        forwardInstruction="Sal por el acceso accesible hacia la rampa del estacionamiento.",
        backwardInstruction="Entra por el acceso oeste accesible hacia el Salón P-108."
    )

    # =========================================================================
    # CORRIDOR WALKWAYS & EDGES: FLOOR 2
    # =========================================================================
    subgraph.addBidirectionalCorridor(
        "p_stairs_f2_east", "p_room_201", 8.6, isAccessible=True,
        forwardInstruction="Avanza 8m por el pasillo este hacia el Salón P-201.",
        backwardInstruction="Dirígete hacia el descanso de las escaleras este en el Piso 2."
    )
    subgraph.addBidirectionalCorridor(
        "p_room_201", "p_fountain_f2_east", 8.6, isAccessible=True,
        forwardInstruction="Camina 8m hacia el bebedero este del segundo piso.",
        backwardInstruction="Camina 8m hacia el Salón P-201."
    )
    subgraph.addBidirectionalCorridor(
        "p_fountain_f2_east", "p_room_202", 4.0, isAccessible=True,
        forwardInstruction="Avanza 4m hacia el Salón P-202.",
        backwardInstruction="Avanza hacia el bebedero este."
    )
    subgraph.addBidirectionalCorridor(
        "p_room_202", "p_room_203", 15.4, isAccessible=True,
        forwardInstruction="Camina 15m por el pasillo central hacia el Salón P-203.",
        backwardInstruction="Camina 15m hacia el Salón P-202."
    )
    subgraph.addBidirectionalCorridor(
        "p_room_203", "p_room_204", 9.5, isAccessible=True,
        forwardInstruction="Avanza 9m hacia el Salón P-204.",
        backwardInstruction="Avanza 9m hacia el Salón P-203."
    )
    subgraph.addBidirectionalCorridor(
        "p_room_204", "p_room_205", 8.2, isAccessible=True,
        forwardInstruction="Continúa 8m hacia el Salón P-205.",
        backwardInstruction="Continúa hacia el Salón P-204."
    )
    subgraph.addBidirectionalCorridor(
        "p_room_205", "p_room_206", 11.1, isAccessible=True,
        forwardInstruction="Avanza 11m hacia el Salón P-206.",
        backwardInstruction="Avanza 11m hacia el Salón P-205."
    )
    subgraph.addBidirectionalCorridor(
        "p_room_206", "p_room_207", 7.1, isAccessible=True,
        forwardInstruction="Camina 7m hacia el Salón P-207.",
        backwardInstruction="Camina 7m hacia el Salón P-206."
    )
    subgraph.addBidirectionalCorridor(
        "p_room_207", "p_room_208", 9.1, isAccessible=True,
        forwardInstruction="Avanza 9m hacia el Salón P-208.",
        backwardInstruction="Avanza 9m hacia el Salón P-207."
    )
    subgraph.addBidirectionalCorridor(
        "p_room_208", "p_fountain_f2_west", 1.5, isAccessible=True,
        forwardInstruction="Avanza al bebedero oeste del segundo piso.",
        backwardInstruction="Avanza hacia el Salón P-208."
    )
    subgraph.addBidirectionalCorridor(
        "p_fountain_f2_west", "p_restrooms_f2", 9.2, isAccessible=True,
        forwardInstruction="Avanza 9m hacia los baños del segundo piso.",
        backwardInstruction="Dirígete hacia el bebedero oeste."
    )
    subgraph.addBidirectionalCorridor(
        "p_restrooms_f2", "p_stairs_f2_west", 5.0, isAccessible=True,
        forwardInstruction="Avanza hacia las escaleras oeste del segundo piso.",
        backwardInstruction="Avanza hacia los baños del segundo piso."
    )

    # =========================================================================
    # CORRIDOR WALKWAYS & EDGES: FLOOR 3
    # =========================================================================
    subgraph.addBidirectionalCorridor(
        "p_stairs_f3_east", "p_room_301", 4.8, isAccessible=True,
        forwardInstruction="Avanza 5m hacia el Salón P-301.",
        backwardInstruction="Dirígete hacia las escaleras este del Piso 3."
    )
    subgraph.addBidirectionalCorridor(
        "p_room_301", "p_fountain_f3", 4.8, isAccessible=True,
        forwardInstruction="Avanza hacia el bebedero del tercer piso.",
        backwardInstruction="Avanza hacia el Salón P-301."
    )
    subgraph.addBidirectionalCorridor(
        "p_fountain_f3", "p_room_301_b", 12.5, isAccessible=True,
        forwardInstruction="Camina 12m hacia el acceso 2 del Salón P-301.",
        backwardInstruction="Camina hacia el bebedero del tercer piso."
    )
    subgraph.addBidirectionalCorridor(
        "p_room_301_b", "p_room_302", 8.1, isAccessible=True,
        forwardInstruction="Avanza 8m hacia el Salón P-302.",
        backwardInstruction="Avanza 8m hacia el Salón P-301 (Acceso 2)."
    )
    subgraph.addBidirectionalCorridor(
        "p_room_302", "p_room_303", 2.0, isAccessible=True,
        forwardInstruction="Continúa al Salón P-303 contiguo.",
        backwardInstruction="Regresa al Salón P-302."
    )
    subgraph.addBidirectionalCorridor(
        "p_room_303", "p_room_304", 6.9, isAccessible=True,
        forwardInstruction="Avanza 7m hacia el Salón P-304.",
        backwardInstruction="Avanza 7m hacia el Salón P-303."
    )
    subgraph.addBidirectionalCorridor(
        "p_room_304", "p_room_305", 12.6, isAccessible=True,
        forwardInstruction="Camina 13m por el pasillo central hacia el Salón P-305.",
        backwardInstruction="Camina 13m hacia el Salón P-304."
    )
    subgraph.addBidirectionalCorridor(
        "p_room_305", "p_room_306", 3.5, isAccessible=True,
        forwardInstruction="Avanza 3m hacia el Salón P-306.",
        backwardInstruction="Avanza 3m hacia el Salón P-305."
    )
    subgraph.addBidirectionalCorridor(
        "p_room_306", "p_room_306_b", 3.1, isAccessible=True,
        forwardInstruction="Avanza hacia el segundo acceso del Salón P-306.",
        backwardInstruction="Avanza hacia el primer acceso del Salón P-306."
    )
    subgraph.addBidirectionalCorridor(
        "p_room_306_b", "p_restrooms_f3", 6.8, isAccessible=True,
        forwardInstruction="Camina 7m hacia los baños del tercer piso.",
        backwardInstruction="Camina hacia el Salón P-306."
    )
    subgraph.addBidirectionalCorridor(
        "p_restrooms_f3", "p_stairs_f3_west", 6.0, isAccessible=True,
        forwardInstruction="Avanza hacia las escaleras oeste del tercer piso.",
        backwardInstruction="Avanza hacia los baños del tercer piso."
    )

    # =========================================================================
    # VERTICAL STAIR CONNECTIONS (EAST & WEST STAIRWELLS)
    # =========================================================================
    # East Stairwell: Piso 1 <-> Piso 2
    subgraph.addVerticalConnection(
        lowerNodeId="p_stairs_f1_east",
        upperNodeId="p_stairs_f2_east",
        distanceMeters=12.0,
        isAccessible=False,
        upInstruction="Sube por las escaleras este hacia el Piso 2 del Edificio P.",
        downInstruction="Baja por las escaleras este hacia el Piso 1 del Edificio P."
    )

    # East Stairwell: Piso 2 <-> Piso 3
    subgraph.addVerticalConnection(
        lowerNodeId="p_stairs_f2_east",
        upperNodeId="p_stairs_f3_east",
        distanceMeters=12.0,
        isAccessible=False,
        upInstruction="Sube por las escaleras este hacia el Piso 3 del Edificio P.",
        downInstruction="Baja por las escaleras este hacia el Piso 2 del Edificio P."
    )

    # West Stairwell: Piso 1 <-> Piso 2
    subgraph.addVerticalConnection(
        lowerNodeId="p_stairs_f1_west",
        upperNodeId="p_stairs_f2_west",
        distanceMeters=12.0,
        isAccessible=False,
        upInstruction="Sube por las segundas escaleras oeste hacia el Piso 2 del Edificio P.",
        downInstruction="Baja por las segundas escaleras oeste hacia el Piso 1 del Edificio P."
    )

    # West Stairwell: Piso 2 <-> Piso 3
    subgraph.addVerticalConnection(
        lowerNodeId="p_stairs_f2_west",
        upperNodeId="p_stairs_f3_west",
        distanceMeters=12.0,
        isAccessible=False,
        upInstruction="Sube por las escaleras oeste hacia el Piso 3 del Edificio P.",
        downInstruction="Baja por las escaleras oeste hacia el Piso 2 del Edificio P."
    )

    return subgraph


# Singleton instance of Building P child graph
buildingPSubgraph = buildBuildingPSubgraph()
