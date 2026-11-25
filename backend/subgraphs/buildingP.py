"""
buildingP.py
================================================================================
BUILDING P (EDIFICIO COPÉRNICO) SUBGRAPH / CHILD GRAPH
================================================================================
Full indoor child graph representation for Building P (Edificio Copérnico),
strictly synchronized with buildings.txt and coordenadas.txt across all 5 floors:
  - Floor 1: Estación de Meteorología, Aulas P101-P108, Bebederos Este/Oeste,
    Baños Hombres/Mujeres, Escaleras y Rampa
  - Floor 2: Aulas P201-P208, Bebederos Este/Oeste, Baños Hombres/Mujeres, Escaleras
  - Floor 3: Aulas P301-P308 (all 8 classrooms aligned to coordenadas.txt),
    Bebederos Este/Oeste, Baños Hombres/Mujeres, Escaleras
  - Floor 4: Aula P401
  - Floor 5: Observatorio Copérnico (P501)
Nomenclature strictly follows P101 (no hyphen).
Weighted, Directed, Non-Complete Graph G = (V, E, W).
================================================================================
"""

from backend.graph.directedGraph import Node
from backend.data.campusCategories import CampusCategory
from .buildingSubgraph import BuildingSubgraph, calcIndoorDistance as _calcDist


def buildBuildingPSubgraph() -> BuildingSubgraph:
    """
    Constructs the official high-resolution child graph for Building P.
    """
    subgraph = BuildingSubgraph(
        buildingId="buildingP",
        name="Edificio P (Copérnico)",
        code="P",
        floors=[1, 2, 3, 4, 5],
        macroNodeId="buildingP",
        entranceNodeIds=[
            "p_stairs_f1_east",
            "p_stairs_f1_west",
            "p_ramp_parking",
            "p_stairs_f1_ext_left"
        ],
        description="Edificio Copérnico (P): Estación de Meteorología, Aulas P101-P108, P201-P208, P301-P308, Aula P401 y Observatorio Copérnico (P501)."
    )

    # =========================================================================
    # FLOOR 1 (PRIMER PISO) — Exact left-to-right order from buildings.txt
    # =========================================================================
    subgraph.addNode(Node(
        nodeId="p_weather_station",
        name="Estación de Meteorología (Edificio P)",
        category=CampusCategory.CLASSROOM,
        xPercent=32.5, yPercent=27.0,
        latitude=12.107470, longitude=-86.256753,
        floorLevel=1, isOutdoorAccessPoint=True
    ))
    subgraph.addNode(Node(
        nodeId="p_room_101",
        name="Aula P101",
        category=CampusCategory.CLASSROOM,
        xPercent=33.0, yPercent=27.0,
        latitude=12.107460, longitude=-86.256743,
        floorLevel=1, isOutdoorAccessPoint=False
    ))
    subgraph.addNode(Node(
        nodeId="p_fountain_f1",
        name="Bebedero de Agua (Edificio P - Piso 1 Este)",
        category=CampusCategory.DRINKING_FOUNTAIN,
        xPercent=33.1, yPercent=27.0,
        latitude=12.107460, longitude=-86.256743,
        floorLevel=1, isOutdoorAccessPoint=False
    ))
    subgraph.addNode(Node(
        nodeId="p_room_102",
        name="Aula P102",
        category=CampusCategory.CLASSROOM,
        xPercent=33.5, yPercent=27.0,
        latitude=12.107431, longitude=-86.256783,
        floorLevel=1, isOutdoorAccessPoint=False
    ))
    subgraph.addNode(Node(
        nodeId="p_room_103",
        name="Aula P103",
        category=CampusCategory.CLASSROOM,
        xPercent=34.5, yPercent=27.0,
        latitude=12.107439, longitude=-86.256947,
        floorLevel=1, isOutdoorAccessPoint=False
    ))
    subgraph.addNode(Node(
        nodeId="p_room_104",
        name="Aula P104",
        category=CampusCategory.CLASSROOM,
        xPercent=35.5, yPercent=27.0,
        latitude=12.107455, longitude=-86.256981,
        floorLevel=1, isOutdoorAccessPoint=False
    ))
    subgraph.addNode(Node(
        nodeId="p_room_105",
        name="Aula P105",
        category=CampusCategory.CLASSROOM,
        xPercent=36.5, yPercent=27.0,
        latitude=12.107453, longitude=-86.257149,
        floorLevel=1, isOutdoorAccessPoint=False
    ))
    subgraph.addNode(Node(
        nodeId="p_room_106",
        name="Aula P106",
        category=CampusCategory.CLASSROOM,
        xPercent=37.5, yPercent=27.0,
        latitude=12.107467, longitude=-86.257202,
        floorLevel=1, isOutdoorAccessPoint=False
    ))
    subgraph.addNode(Node(
        nodeId="p_room_107",
        name="Aula P107",
        category=CampusCategory.CLASSROOM,
        xPercent=38.5, yPercent=27.0,
        latitude=12.107450, longitude=-86.257270,
        floorLevel=1, isOutdoorAccessPoint=False
    ))
    subgraph.addNode(Node(
        nodeId="p_room_108",
        name="Aula P108",
        category=CampusCategory.CLASSROOM,
        xPercent=39.5, yPercent=27.0,
        latitude=12.107477, longitude=-86.257206,
        floorLevel=1, isOutdoorAccessPoint=False
    ))
    subgraph.addNode(Node(
        nodeId="p_fountain_f1_west",
        name="Bebedero de Agua (Edificio P - Piso 1 Oeste)",
        category=CampusCategory.DRINKING_FOUNTAIN,
        xPercent=40.0, yPercent=27.0,
        latitude=12.107459, longitude=-86.257314,
        floorLevel=1, isOutdoorAccessPoint=False
    ))
    subgraph.addNode(Node(
        nodeId="p_restrooms_men_f1",
        name="Baños Hombres (Edificio P - Piso 1)",
        category=CampusCategory.RESTROOM,
        xPercent=40.5, yPercent=27.0,
        latitude=12.107441, longitude=-86.257422,
        floorLevel=1, isOutdoorAccessPoint=False
    ))
    subgraph.addNode(Node(
        nodeId="p_restrooms_women_f1",
        name="Baños Mujeres (Edificio P - Piso 1)",
        category=CampusCategory.RESTROOM,
        xPercent=40.7, yPercent=27.0,
        latitude=12.107441, longitude=-86.257422,
        floorLevel=1, isOutdoorAccessPoint=False
    ))
    # Stairs & ramps (Floor 1)
    subgraph.addNode(Node(
        nodeId="p_stairs_f1_ext_left",
        name="Escaleras del P (Izquierda / Exterior)",
        category=CampusCategory.STAIRS,
        xPercent=32.0, yPercent=27.0,
        latitude=12.107584, longitude=-86.256779,
        floorLevel=1, isOutdoorAccessPoint=True
    ))
    subgraph.addNode(Node(
        nodeId="p_stairs_f1_east",
        name="Escaleras Este del P (Piso 1)",
        category=CampusCategory.STAIRS,
        xPercent=32.7, yPercent=27.0,
        latitude=12.107470, longitude=-86.256753,
        floorLevel=1, isOutdoorAccessPoint=True
    ))
    subgraph.addNode(Node(
        nodeId="p_stairs_f1_west",
        name="Escaleras Oeste del P (Piso 1)",
        category=CampusCategory.STAIRS,
        xPercent=41.0, yPercent=27.0,
        latitude=12.107410, longitude=-86.257431,
        floorLevel=1, isOutdoorAccessPoint=True
    ))
    subgraph.addNode(Node(
        nodeId="p_stairs_to_building_o",
        name="Escaleras del P hacia Edificio O",
        category=CampusCategory.STAIRS,
        xPercent=41.5, yPercent=27.0,
        latitude=12.107453, longitude=-86.257413,
        floorLevel=1, isOutdoorAccessPoint=True
    ))
    subgraph.addNode(Node(
        nodeId="p_ramp_parking",
        name="Rampa del Estacionamiento hacia Edificio P",
        category=CampusCategory.ACCESSIBLE_RAMP,
        xPercent=42.0, yPercent=27.0,
        latitude=12.106991, longitude=-86.258233,
        floorLevel=1, isOutdoorAccessPoint=True
    ))

    # =========================================================================
    # FLOOR 2 (SEGUNDO PISO) — Exact left-to-right order from buildings.txt
    # =========================================================================
    subgraph.addNode(Node(
        nodeId="p_room_201",
        name="Aula P201",
        category=CampusCategory.CLASSROOM,
        xPercent=33.0, yPercent=27.0,
        latitude=12.107484, longitude=-86.256721,
        floorLevel=2, isOutdoorAccessPoint=False
    ))
    subgraph.addNode(Node(
        nodeId="p_fountain_f2_east",
        name="Bebedero de Agua (Edificio P - Piso 2 Este)",
        category=CampusCategory.DRINKING_FOUNTAIN,
        xPercent=33.2, yPercent=27.0,
        latitude=12.107434, longitude=-86.256781,
        floorLevel=2, isOutdoorAccessPoint=False
    ))
    subgraph.addNode(Node(
        nodeId="p_room_202",
        name="Aula P202",
        category=CampusCategory.CLASSROOM,
        xPercent=33.5, yPercent=27.0,
        latitude=12.107428, longitude=-86.256817,
        floorLevel=2, isOutdoorAccessPoint=False
    ))
    subgraph.addNode(Node(
        nodeId="p_room_203",
        name="Aula P203",
        category=CampusCategory.CLASSROOM,
        xPercent=34.5, yPercent=27.0,
        latitude=12.107447, longitude=-86.256957,
        floorLevel=2, isOutdoorAccessPoint=False
    ))
    subgraph.addNode(Node(
        nodeId="p_room_204",
        name="Aula P204",
        category=CampusCategory.CLASSROOM,
        xPercent=35.5, yPercent=27.0,
        latitude=12.107434, longitude=-86.257043,
        floorLevel=2, isOutdoorAccessPoint=False
    ))
    subgraph.addNode(Node(
        nodeId="p_room_205",
        name="Aula P205",
        category=CampusCategory.CLASSROOM,
        xPercent=36.5, yPercent=27.0,
        latitude=12.107492, longitude=-86.257090,
        floorLevel=2, isOutdoorAccessPoint=False
    ))
    subgraph.addNode(Node(
        nodeId="p_room_206",
        name="Aula P206",
        category=CampusCategory.CLASSROOM,
        xPercent=37.5, yPercent=27.0,
        latitude=12.107413, longitude=-86.257153,
        floorLevel=2, isOutdoorAccessPoint=False
    ))
    subgraph.addNode(Node(
        nodeId="p_room_207",
        name="Aula P207",
        category=CampusCategory.CLASSROOM,
        xPercent=38.5, yPercent=27.0,
        latitude=12.107427, longitude=-86.257217,
        floorLevel=2, isOutdoorAccessPoint=False
    ))
    subgraph.addNode(Node(
        nodeId="p_room_208",
        name="Aula P208",
        category=CampusCategory.CLASSROOM,
        xPercent=39.5, yPercent=27.0,
        latitude=12.107402, longitude=-86.257297,
        floorLevel=2, isOutdoorAccessPoint=False
    ))
    subgraph.addNode(Node(
        nodeId="p_fountain_f2_west",
        name="Bebedero de Agua (Edificio P - Piso 2 Oeste)",
        category=CampusCategory.DRINKING_FOUNTAIN,
        xPercent=40.0, yPercent=27.0,
        latitude=12.107407, longitude=-86.257298,
        floorLevel=2, isOutdoorAccessPoint=False
    ))
    subgraph.addNode(Node(
        nodeId="p_restrooms_men_f2",
        name="Baños Hombres (Edificio P - Piso 2)",
        category=CampusCategory.RESTROOM,
        xPercent=40.5, yPercent=27.0,
        latitude=12.107480, longitude=-86.257337,
        floorLevel=2, isOutdoorAccessPoint=False
    ))
    subgraph.addNode(Node(
        nodeId="p_restrooms_women_f2",
        name="Baños Mujeres (Edificio P - Piso 2)",
        category=CampusCategory.RESTROOM,
        xPercent=40.7, yPercent=27.0,
        latitude=12.107480, longitude=-86.257337,
        floorLevel=2, isOutdoorAccessPoint=False
    ))
    subgraph.addNode(Node(
        nodeId="p_stairs_f2_east",
        name="Escaleras Este del P (Piso 2)",
        category=CampusCategory.STAIRS,
        xPercent=32.7, yPercent=27.0,
        latitude=12.107470, longitude=-86.256753,
        floorLevel=2, isOutdoorAccessPoint=False
    ))
    subgraph.addNode(Node(
        nodeId="p_stairs_f2_west",
        name="Escaleras Oeste del P (Piso 2)",
        category=CampusCategory.STAIRS,
        xPercent=41.0, yPercent=27.0,
        latitude=12.107410, longitude=-86.257431,
        floorLevel=2, isOutdoorAccessPoint=False
    ))

    # =========================================================================
    # FLOOR 3 (TERCER PISO) — True P301..P308 aligned to coordenadas.txt
    # =========================================================================
    subgraph.addNode(Node(
        nodeId="p_room_301",
        name="Aula P301",
        category=CampusCategory.CLASSROOM,
        xPercent=33.0, yPercent=27.0,
        latitude=12.107461, longitude=-86.256717,
        floorLevel=3, isOutdoorAccessPoint=False
    ))
    subgraph.addNode(Node(
        nodeId="p_fountain_f3",
        name="Bebedero de Agua (Edificio P - Piso 3 Este)",
        category=CampusCategory.DRINKING_FOUNTAIN,
        xPercent=33.2, yPercent=27.0,
        latitude=12.107434, longitude=-86.256751,
        floorLevel=3, isOutdoorAccessPoint=False
    ))
    subgraph.addNode(Node(
        nodeId="p_room_302",
        name="Aula P302",
        category=CampusCategory.CLASSROOM,
        xPercent=33.8, yPercent=27.0,
        latitude=12.107462, longitude=-86.256862,
        floorLevel=3, isOutdoorAccessPoint=False
    ))
    subgraph.addNode(Node(
        nodeId="p_room_303",
        name="Aula P303",
        category=CampusCategory.CLASSROOM,
        xPercent=34.6, yPercent=27.0,
        latitude=12.107443, longitude=-86.256934,
        floorLevel=3, isOutdoorAccessPoint=False
    ))
    subgraph.addNode(Node(
        nodeId="p_room_304",
        name="Aula P304",
        category=CampusCategory.CLASSROOM,
        xPercent=35.4, yPercent=27.0,
        latitude=12.107442, longitude=-86.256936,
        floorLevel=3, isOutdoorAccessPoint=False
    ))
    subgraph.addNode(Node(
        nodeId="p_room_305",
        name="Aula P305",
        category=CampusCategory.CLASSROOM,
        xPercent=36.3, yPercent=27.0,
        latitude=12.107443, longitude=-86.256999,
        floorLevel=3, isOutdoorAccessPoint=False
    ))
    subgraph.addNode(Node(
        nodeId="p_room_306",
        name="Aula P306",
        category=CampusCategory.CLASSROOM,
        xPercent=37.4, yPercent=27.0,
        latitude=12.107454, longitude=-86.257114,
        floorLevel=3, isOutdoorAccessPoint=False
    ))
    subgraph.addNode(Node(
        nodeId="p_room_307",
        name="Aula P307",
        category=CampusCategory.CLASSROOM,
        xPercent=38.4, yPercent=27.0,
        latitude=12.107461, longitude=-86.257145,
        floorLevel=3, isOutdoorAccessPoint=False
    ))
    subgraph.addNode(Node(
        nodeId="p_room_308",
        name="Aula P308",
        category=CampusCategory.CLASSROOM,
        xPercent=39.3, yPercent=27.0,
        latitude=12.107435, longitude=-86.257136,
        floorLevel=3, isOutdoorAccessPoint=False
    ))
    subgraph.addNode(Node(
        nodeId="p_fountain_f3_west",
        name="Bebedero de Agua (Edificio P - Piso 3 Oeste)",
        category=CampusCategory.DRINKING_FOUNTAIN,
        xPercent=39.8, yPercent=27.0,
        latitude=12.107452, longitude=-86.257162,
        floorLevel=3, isOutdoorAccessPoint=False
    ))
    subgraph.addNode(Node(
        nodeId="p_restrooms_men_f3",
        name="Baños Hombres (Edificio P - Piso 3)",
        category=CampusCategory.RESTROOM,
        xPercent=40.3, yPercent=27.0,
        latitude=12.107468, longitude=-86.257189,
        floorLevel=3, isOutdoorAccessPoint=False
    ))
    subgraph.addNode(Node(
        nodeId="p_restrooms_women_f3",
        name="Baños Mujeres (Edificio P - Piso 3)",
        category=CampusCategory.RESTROOM,
        xPercent=40.5, yPercent=27.0,
        latitude=12.107468, longitude=-86.257189,
        floorLevel=3, isOutdoorAccessPoint=False
    ))
    subgraph.addNode(Node(
        nodeId="p_stairs_f3_east",
        name="Escaleras Este del P (Piso 3)",
        category=CampusCategory.STAIRS,
        xPercent=32.7, yPercent=27.0,
        latitude=12.107470, longitude=-86.256753,
        floorLevel=3, isOutdoorAccessPoint=False
    ))
    subgraph.addNode(Node(
        nodeId="p_stairs_f3_west",
        name="Escaleras Oeste del P (Piso 3)",
        category=CampusCategory.STAIRS,
        xPercent=41.0, yPercent=27.0,
        latitude=12.107410, longitude=-86.257431,
        floorLevel=3, isOutdoorAccessPoint=False
    ))

    # =========================================================================
    # FLOOR 4 (CUARTO PISO - ANEXO SUPERIOR P401)
    # =========================================================================
    subgraph.addNode(Node(
        nodeId="p_room_401",
        name="Aula P401",
        category=CampusCategory.CLASSROOM,
        xPercent=33.0, yPercent=27.0,
        latitude=12.107470, longitude=-86.256753,
        floorLevel=4, isOutdoorAccessPoint=False
    ))
    subgraph.addNode(Node(
        nodeId="p_stairs_f4_east",
        name="Escaleras del Anexo del P (Piso 4)",
        category=CampusCategory.STAIRS,
        xPercent=32.7, yPercent=27.0,
        latitude=12.107470, longitude=-86.256753,
        floorLevel=4, isOutdoorAccessPoint=False
    ))

    # =========================================================================
    # FLOOR 5 (QUINTO PISO - OBSERVATORIO COPÉRNICO)
    # =========================================================================
    subgraph.addNode(Node(
        nodeId="p_observatory_501",
        name="Observatorio Copérnico (P501)",
        category=CampusCategory.CLASSROOM,
        xPercent=33.0, yPercent=27.0,
        latitude=12.107470, longitude=-86.256753,
        floorLevel=5, isOutdoorAccessPoint=False
    ))
    subgraph.addNode(Node(
        nodeId="p_stairs_f5_east",
        name="Escaleras del Observatorio del P (Piso 5)",
        category=CampusCategory.STAIRS,
        xPercent=32.7, yPercent=27.0,
        latitude=12.107470, longitude=-86.256753,
        floorLevel=5, isOutdoorAccessPoint=False
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
        "p_stairs_f1_east", "p_weather_station", 2.0, isAccessible=True,
        forwardInstruction="Avanza hacia la Estación de Meteorología junto a las escaleras este.",
        backwardInstruction="Dirígete hacia las escaleras este del primer piso."
    )
    subgraph.addBidirectionalCorridor(
        "p_weather_station", "p_room_101", 2.0, isAccessible=True,
        forwardInstruction="Avanza hacia el Aula P101.",
        backwardInstruction="Regresa hacia la Estación de Meteorología."
    )
    subgraph.addBidirectionalCorridor(
        "p_room_101", "p_fountain_f1", 1.5, isAccessible=True,
        forwardInstruction="Avanza hacia el bebedero este junto al Aula P101.",
        backwardInstruction="Regresa al Aula P101."
    )
    subgraph.addBidirectionalCorridor(
        "p_fountain_f1", "p_room_102", 5.4, isAccessible=True,
        forwardInstruction="Camina por el pasillo hacia el Aula P102.",
        backwardInstruction="Camina por el pasillo hacia el bebedero y el Aula P101."
    )
    subgraph.addBidirectionalCorridor(
        "p_room_102", "p_room_103", 17.9, isAccessible=True,
        forwardInstruction="Avanza por el pasillo principal hacia el Aula P103.",
        backwardInstruction="Avanza por el pasillo hacia el Aula P102."
    )
    subgraph.addBidirectionalCorridor(
        "p_room_103", "p_room_104", 4.1, isAccessible=True,
        forwardInstruction="Avanza hacia el Aula P104.",
        backwardInstruction="Avanza hacia el Aula P103."
    )
    subgraph.addBidirectionalCorridor(
        "p_room_104", "p_room_105", 18.3, isAccessible=True,
        forwardInstruction="Continúa por el pasillo central hacia el Aula P105.",
        backwardInstruction="Continúa hacia el Aula P104."
    )
    subgraph.addBidirectionalCorridor(
        "p_room_105", "p_room_106", 6.0, isAccessible=True,
        forwardInstruction="Avanza hacia el Aula P106.",
        backwardInstruction="Avanza hacia el Aula P105."
    )
    subgraph.addBidirectionalCorridor(
        "p_room_106", "p_room_107", 7.6, isAccessible=True,
        forwardInstruction="Camina hacia el Aula P107.",
        backwardInstruction="Camina hacia el Aula P106."
    )
    subgraph.addBidirectionalCorridor(
        "p_room_107", "p_room_108", 7.6, isAccessible=True,
        forwardInstruction="Avanza hacia el Aula P108.",
        backwardInstruction="Avanza hacia el Aula P107."
    )
    subgraph.addBidirectionalCorridor(
        "p_room_108", "p_fountain_f1_west", 12.0, isAccessible=True,
        forwardInstruction="Camina hacia el bebedero oeste del primer piso.",
        backwardInstruction="Camina hacia el Aula P108."
    )
    subgraph.addBidirectionalCorridor(
        "p_fountain_f1_west", "p_restrooms_men_f1", 11.8, isAccessible=True,
        forwardInstruction="Avanza hacia los baños de hombres del primer piso.",
        backwardInstruction="Avanza hacia el bebedero oeste del primer piso."
    )
    subgraph.addBidirectionalCorridor(
        "p_restrooms_men_f1", "p_restrooms_women_f1", 2.0, isAccessible=True,
        forwardInstruction="Accede a los baños de mujeres del primer piso.",
        backwardInstruction="Accede a los baños de hombres del primer piso."
    )
    subgraph.addBidirectionalCorridor(
        "p_restrooms_women_f1", "p_stairs_f1_west", 3.6, isAccessible=True,
        forwardInstruction="Gira hacia las escaleras oeste del primer piso.",
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
        backwardInstruction="Entra por el acceso oeste accesible hacia el Aula P108."
    )

    # =========================================================================
    # CORRIDOR WALKWAYS & EDGES: FLOOR 2
    # =========================================================================
    subgraph.addBidirectionalCorridor(
        "p_stairs_f2_east", "p_room_201", 8.6, isAccessible=True,
        forwardInstruction="Avanza por el pasillo hacia el Aula P201.",
        backwardInstruction="Dirígete hacia el descanso de las escaleras este en el Piso 2."
    )
    subgraph.addBidirectionalCorridor(
        "p_room_201", "p_fountain_f2_east", 8.6, isAccessible=True,
        forwardInstruction="Camina hacia el bebedero este del segundo piso.",
        backwardInstruction="Camina hacia el Aula P201."
    )
    subgraph.addBidirectionalCorridor(
        "p_fountain_f2_east", "p_room_202", 4.0, isAccessible=True,
        forwardInstruction="Avanza hacia el Aula P202.",
        backwardInstruction="Avanza hacia el bebedero este."
    )
    subgraph.addBidirectionalCorridor(
        "p_room_202", "p_room_203", 15.4, isAccessible=True,
        forwardInstruction="Camina por el pasillo central hacia el Aula P203.",
        backwardInstruction="Camina hacia el Aula P202."
    )
    subgraph.addBidirectionalCorridor(
        "p_room_203", "p_room_204", 9.5, isAccessible=True,
        forwardInstruction="Avanza hacia el Aula P204.",
        backwardInstruction="Avanza hacia el Aula P203."
    )
    subgraph.addBidirectionalCorridor(
        "p_room_204", "p_room_205", 8.2, isAccessible=True,
        forwardInstruction="Continúa hacia el Aula P205.",
        backwardInstruction="Continúa hacia el Aula P204."
    )
    subgraph.addBidirectionalCorridor(
        "p_room_205", "p_room_206", 11.1, isAccessible=True,
        forwardInstruction="Avanza hacia el Aula P206.",
        backwardInstruction="Avanza hacia el Aula P205."
    )
    subgraph.addBidirectionalCorridor(
        "p_room_206", "p_room_207", 7.1, isAccessible=True,
        forwardInstruction="Camina hacia el Aula P207.",
        backwardInstruction="Camina hacia el Aula P206."
    )
    subgraph.addBidirectionalCorridor(
        "p_room_207", "p_room_208", 9.1, isAccessible=True,
        forwardInstruction="Avanza hacia el Aula P208.",
        backwardInstruction="Avanza hacia el Aula P207."
    )
    subgraph.addBidirectionalCorridor(
        "p_room_208", "p_fountain_f2_west", 1.5, isAccessible=True,
        forwardInstruction="Avanza al bebedero oeste del segundo piso.",
        backwardInstruction="Avanza hacia el Aula P208."
    )
    subgraph.addBidirectionalCorridor(
        "p_fountain_f2_west", "p_restrooms_men_f2", 9.2, isAccessible=True,
        forwardInstruction="Avanza hacia los baños de hombres del segundo piso.",
        backwardInstruction="Dirígete hacia el bebedero oeste."
    )
    subgraph.addBidirectionalCorridor(
        "p_restrooms_men_f2", "p_restrooms_women_f2", 2.0, isAccessible=True,
        forwardInstruction="Accede a los baños de mujeres del segundo piso.",
        backwardInstruction="Accede a los baños de hombres del segundo piso."
    )
    subgraph.addBidirectionalCorridor(
        "p_restrooms_women_f2", "p_stairs_f2_west", 5.0, isAccessible=True,
        forwardInstruction="Avanza hacia las escaleras oeste del segundo piso.",
        backwardInstruction="Avanza hacia los baños del segundo piso."
    )

    # =========================================================================
    # CORRIDOR WALKWAYS & EDGES: FLOOR 3 (P301..P308)
    # =========================================================================
    subgraph.addBidirectionalCorridor(
        "p_stairs_f3_east", "p_room_301", 4.8, isAccessible=True,
        forwardInstruction="Avanza hacia el Aula P301.",
        backwardInstruction="Dirígete hacia las escaleras este del Piso 3."
    )
    subgraph.addBidirectionalCorridor(
        "p_room_301", "p_fountain_f3", 4.8, isAccessible=True,
        forwardInstruction="Avanza hacia el bebedero este del tercer piso.",
        backwardInstruction="Avanza hacia el Aula P301."
    )
    subgraph.addBidirectionalCorridor(
        "p_fountain_f3", "p_room_302", 12.5, isAccessible=True,
        forwardInstruction="Camina hacia el Aula P302.",
        backwardInstruction="Camina hacia el bebedero del tercer piso."
    )
    subgraph.addBidirectionalCorridor(
        "p_room_302", "p_room_303", 8.1, isAccessible=True,
        forwardInstruction="Avanza hacia el Aula P303.",
        backwardInstruction="Avanza hacia el Aula P302."
    )
    subgraph.addBidirectionalCorridor(
        "p_room_303", "p_room_304", 2.0, isAccessible=True,
        forwardInstruction="Continúa al Aula P304 contigua.",
        backwardInstruction="Regresa al Aula P303."
    )
    subgraph.addBidirectionalCorridor(
        "p_room_304", "p_room_305", 6.9, isAccessible=True,
        forwardInstruction="Avanza hacia el Aula P305.",
        backwardInstruction="Avanza hacia el Aula P304."
    )
    subgraph.addBidirectionalCorridor(
        "p_room_305", "p_room_306", 12.6, isAccessible=True,
        forwardInstruction="Camina por el pasillo central hacia el Aula P306.",
        backwardInstruction="Camina hacia el Aula P305."
    )
    subgraph.addBidirectionalCorridor(
        "p_room_306", "p_room_307", 3.5, isAccessible=True,
        forwardInstruction="Avanza hacia el Aula P307.",
        backwardInstruction="Avanza hacia el Aula P306."
    )
    subgraph.addBidirectionalCorridor(
        "p_room_307", "p_room_308", 3.1, isAccessible=True,
        forwardInstruction="Avanza hacia el Aula P308.",
        backwardInstruction="Avanza hacia el Aula P307."
    )
    subgraph.addBidirectionalCorridor(
        "p_room_308", "p_fountain_f3_west", 3.5, isAccessible=True,
        forwardInstruction="Avanza hacia el bebedero oeste del tercer piso.",
        backwardInstruction="Avanza hacia el Aula P308."
    )
    subgraph.addBidirectionalCorridor(
        "p_fountain_f3_west", "p_restrooms_men_f3", 3.5, isAccessible=True,
        forwardInstruction="Camina hacia los baños de hombres del tercer piso.",
        backwardInstruction="Camina hacia el bebedero oeste del tercer piso."
    )
    subgraph.addBidirectionalCorridor(
        "p_restrooms_men_f3", "p_restrooms_women_f3", 2.0, isAccessible=True,
        forwardInstruction="Accede a los baños de mujeres del tercer piso.",
        backwardInstruction="Accede a los baños de hombres del tercer piso."
    )
    subgraph.addBidirectionalCorridor(
        "p_restrooms_women_f3", "p_stairs_f3_west", 6.0, isAccessible=True,
        forwardInstruction="Avanza hacia las escaleras oeste del tercer piso.",
        backwardInstruction="Avanza hacia los baños del tercer piso."
    )

    # =========================================================================
    # VERTICAL STAIR CONNECTIONS (EAST & WEST STAIRWELLS)
    # =========================================================================
    subgraph.addVerticalConnection(
        lowerNodeId="p_stairs_f1_east",
        upperNodeId="p_stairs_f2_east",
        distanceMeters=12.0,
        isAccessible=False,
        upInstruction="Sube por las escaleras este hacia el Piso 2 del Edificio P.",
        downInstruction="Baja por las escaleras este hacia el Piso 1 del Edificio P."
    )
    subgraph.addVerticalConnection(
        lowerNodeId="p_stairs_f2_east",
        upperNodeId="p_stairs_f3_east",
        distanceMeters=12.0,
        isAccessible=False,
        upInstruction="Sube por las escaleras este hacia el Piso 3 del Edificio P.",
        downInstruction="Baja por las escaleras este hacia el Piso 2 del Edificio P."
    )
    subgraph.addVerticalConnection(
        lowerNodeId="p_stairs_f3_east",
        upperNodeId="p_stairs_f4_east",
        distanceMeters=10.5,
        isAccessible=False,
        upInstruction="Sube por las escaleras hacia el Piso 4 (Aula P401).",
        downInstruction="Baja por las escaleras hacia el Piso 3."
    )
    subgraph.addVerticalConnection(
        lowerNodeId="p_stairs_f4_east",
        upperNodeId="p_stairs_f5_east",
        distanceMeters=10.5,
        isAccessible=False,
        upInstruction="Sube por las escaleras hacia el Piso 5 (Observatorio Copérnico).",
        downInstruction="Baja por las escaleras hacia el Piso 4 (Aula P401)."
    )
    subgraph.addBidirectionalCorridor(
        "p_stairs_f4_east", "p_room_401", 4.0, isAccessible=False,
        forwardInstruction="Entra al Aula P401 por la puerta izquierda.",
        backwardInstruction="Sal del Aula P401 hacia las escaleras del 4to piso."
    )
    subgraph.addBidirectionalCorridor(
        "p_stairs_f5_east", "p_observatory_501", 4.0, isAccessible=False,
        forwardInstruction="Entra al Observatorio Copérnico (P501) por la puerta izquierda.",
        backwardInstruction="Sal del Observatorio Copérnico hacia las escaleras del 5to piso."
    )
    subgraph.addVerticalConnection(
        lowerNodeId="p_stairs_f1_west",
        upperNodeId="p_stairs_f2_west",
        distanceMeters=12.0,
        isAccessible=False,
        upInstruction="Sube por las escaleras oeste hacia el Piso 2 del Edificio P.",
        downInstruction="Baja por las escaleras oeste hacia el Piso 1 del Edificio P."
    )
    subgraph.addVerticalConnection(
        lowerNodeId="p_stairs_f2_west",
        upperNodeId="p_stairs_f3_west",
        distanceMeters=12.0,
        isAccessible=False,
        upInstruction="Sube por las escaleras oeste hacia el Piso 3 del Edificio P.",
        downInstruction="Baja por las escaleras oeste hacia el Piso 2 del Edificio P."
    )

    # Room & landmark aliases (includes hyphenated forms for search tolerance)
    aliases = {
        "estacion de meteorologia": "p_weather_station", "meteorologia": "p_weather_station", "weatherStationP": "p_weather_station",
        "p101": "p_room_101", "p-101": "p_room_101", "classroomP101": "p_room_101",
        "p102": "p_room_102", "p-102": "p_room_102", "classroomP102": "p_room_102",
        "p103": "p_room_103", "p-103": "p_room_103", "classroomP103": "p_room_103",
        "p104": "p_room_104", "p-104": "p_room_104", "classroomP104": "p_room_104",
        "p105": "p_room_105", "p-105": "p_room_105", "classroomP105": "p_room_105",
        "p106": "p_room_106", "p-106": "p_room_106", "classroomP106": "p_room_106",
        "p107": "p_room_107", "p-107": "p_room_107", "classroomP107": "p_room_107",
        "p108": "p_room_108", "p-108": "p_room_108", "classroomP108": "p_room_108",
        "p201": "p_room_201", "p-201": "p_room_201", "classroomP201": "p_room_201",
        "p202": "p_room_202", "p-202": "p_room_202", "classroomP202": "p_room_202",
        "p203": "p_room_203", "p-203": "p_room_203", "classroomP203": "p_room_203",
        "p204": "p_room_204", "p-204": "p_room_204", "classroomP204": "p_room_204",
        "p205": "p_room_205", "p-205": "p_room_205", "classroomP205": "p_room_205",
        "p206": "p_room_206", "p-206": "p_room_206", "classroomP206": "p_room_206",
        "p207": "p_room_207", "p-207": "p_room_207", "classroomP207": "p_room_207",
        "p208": "p_room_208", "p-208": "p_room_208", "classroomP208": "p_room_208",
        "p301": "p_room_301", "p-301": "p_room_301", "classroomP301": "p_room_301",
        "p302": "p_room_302", "p-302": "p_room_302", "classroomP302": "p_room_302", "p_room_301_b": "p_room_302",
        "p303": "p_room_303", "p-303": "p_room_303", "classroomP303": "p_room_303",
        "p304": "p_room_304", "p-304": "p_room_304", "classroomP304": "p_room_304",
        "p305": "p_room_305", "p-305": "p_room_305", "classroomP305": "p_room_305",
        "p306": "p_room_306", "p-306": "p_room_306", "classroomP306": "p_room_306",
        "p307": "p_room_307", "p-307": "p_room_307", "classroomP307": "p_room_307",
        "p308": "p_room_308", "p-308": "p_room_308", "classroomP308": "p_room_308", "p_room_306_b": "p_room_308",
        "p401": "p_room_401", "p-401": "p_room_401", "aula 401": "p_room_401", "classroomP401": "p_room_401",
        "observatorio": "p_observatory_501", "observatorio copernico": "p_observatory_501",
        "copernico": "p_observatory_501", "observatory": "p_observatory_501",
        "p501": "p_observatory_501", "p-501": "p_observatory_501", "copernicusObservatoryP": "p_observatory_501",
        "rampa p": "p_ramp_parking", "rampParkingP": "p_ramp_parking",
        "banos p": "p_restrooms_men_f1", "baños p": "p_restrooms_men_f1", "p_restrooms_f1": "p_restrooms_men_f1",
        "restroomsMenP1": "p_restrooms_men_f1", "restroomsWomenP1": "p_restrooms_women_f1",
        "p_restrooms_f2": "p_restrooms_men_f2", "restroomsMenP2": "p_restrooms_men_f2", "restroomsWomenP2": "p_restrooms_women_f2",
        "p_restrooms_f3": "p_restrooms_men_f3", "restroomsMenP3": "p_restrooms_men_f3", "restroomsWomenP3": "p_restrooms_women_f3",
        "drinkingFountainP1": "p_fountain_f1", "drinkingFountainP1West": "p_fountain_f1_west",
        "drinkingFountainP2East": "p_fountain_f2_east", "drinkingFountainP2West": "p_fountain_f2_west",
        "drinkingFountainP3": "p_fountain_f3", "drinkingFountainP3West": "p_fountain_f3_west",
    }
    for alias, nid in aliases.items():
        subgraph.registerRoomAlias(alias, nid)

    return subgraph


# Singleton instance of Building P child graph
buildingPSubgraph = buildBuildingPSubgraph()
