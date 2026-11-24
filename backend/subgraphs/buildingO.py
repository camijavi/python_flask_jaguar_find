"""
buildingO.py
================================================================================
BUILDING O (FACULTAD DE INGENIERÍA Y ARQUITECTURA) SUBGRAPH / CHILD GRAPH
================================================================================
Indoor child graph representation for Building O (Edificio O - FIA), including:
Floor 1:
- Facultad de Ingeniería y Arquitectura: 12.107664, -86.257761 (O-101)
- Lab mecánica de suelos: 12.107535, -86.257643 (O-102)
- Área de exhibición: 12.107518, -86.257615
- Lab resistencia de materiales: 12.107502, -86.257586 (O-104)
- Área de mezclado: 12.107490, -86.257570
- Área de curado: 12.107485, -86.257560
- Técnicos de lab: 12.107510, -86.257575
- Lab mecánica de fluidos: 12.107515, -86.257550
- Baños hombres: 12.108151, -86.257888
- Baños mujeres: 12.108151, -86.257888
- Sala de maestros FIA (anexo norte): 12.108229, -86.257948
- Coordinación de gestión integral de riesgos de desastres (O-105): 12.107545, -86.257437
- Mapa UAM: 12.107478, -86.257555
- Escaleras O (Piso 1): 12.107554, -86.257487
- Escaleras del O al parqueo: 12.107591, -86.257458
- Rampa del O a la acera del parqueo: 12.107612, -86.257442
- De la acera al parqueo del O: 12.107675, -86.257388

Floor 2:
- Lab redes O201: 12.107520, -86.257586
- Aula O202: 12.107741, -86.257507
- Sala de tutoría: 12.107632, -86.257548
- Centro de inteligencia artificial y robótica (CIAR): 12.107599, -86.257561
- Centro de Redes: 12.107550, -86.257575
- Robótica: 12.107585, -86.257567
- Bebedero de agua (Piso 2): 12.107585, -86.257567
- Escaleras O (Piso 2): 12.107554, -86.257487
================================================================================
"""

from backend.graph.directedGraph import Node
from backend.data.campusCategories import CampusCategory
from .buildingSubgraph import BuildingSubgraph, calcIndoorDistance as _calcDist


def buildBuildingOSubgraph() -> BuildingSubgraph:
    """
    Constructs the official child graph for Building O (Facultad de Ingeniería y Arquitectura).
    Covers Floor 1 (Labs, Decanatura FIA, Anexo Norte, Parqueo) and Floor 2 (CIAR, Robótica, Redes, Tutoría).
    """
    subgraph = BuildingSubgraph(
        buildingId="buildingO",
        name="Edificio O (Facultad de Ingeniería y Arquitectura)",
        code="O",
        floors=[1, 2],
        macroNodeId="buildingO",
        entranceNodeIds=["o_mapa_uam", "o_ramp_parking", "o_stairs_parking", "o_fia_101"],
        description="Edificio O de la Facultad de Ingeniería y Arquitectura (FIA), Laboratorios de Ingeniería Civil, CIAR, Robótica y Redes."
    )

    # =========================================================================
    # FLOOR 1 (PLANTA BAJA)
    # =========================================================================

    # 1. Mapa UAM (Directorio y Entrada Principal)
    subgraph.addNode(Node(
        nodeId="o_mapa_uam",
        name="Mapa UAM (Entrada Edificio O)",
        category=CampusCategory.ADMINISTRATIVE,
        xPercent=43.0, yPercent=32.0,
        latitude=12.107478, longitude=-86.257555,
        floorLevel=1, isOutdoorAccessPoint=True
    ))

    # 2. Facultad de Ingeniería y Arquitectura (O-101) - Decanatura
    subgraph.addNode(Node(
        nodeId="o_fia_101",
        name="Facultad de Ingeniería y Arquitectura (O-101)",
        category=CampusCategory.FACULTY,
        xPercent=42.5, yPercent=31.5,
        latitude=12.107664, longitude=-86.257761,
        floorLevel=1, isOutdoorAccessPoint=True
    ))

    # 3. Lab Mecánica de Suelos (O-102)
    subgraph.addNode(Node(
        nodeId="o_lab_suelos_102",
        name="Laboratorio de Mecánica de Suelos (O-102)",
        category=CampusCategory.FACULTY,
        xPercent=42.8, yPercent=31.8,
        latitude=12.107535, longitude=-86.257643,
        floorLevel=1, isOutdoorAccessPoint=False
    ))

    # 4. Área de Exhibición
    subgraph.addNode(Node(
        nodeId="o_exhibition_area",
        name="Área de Exhibición (Edificio O)",
        category=CampusCategory.FACULTY,
        xPercent=42.9, yPercent=31.9,
        latitude=12.107518, longitude=-86.257615,
        floorLevel=1, isOutdoorAccessPoint=False
    ))

    # 5. Lab Resistencia de Materiales (O-104)
    subgraph.addNode(Node(
        nodeId="o_lab_materiales_104",
        name="Laboratorio de Resistencia de Materiales (O-104)",
        category=CampusCategory.FACULTY,
        xPercent=43.1, yPercent=32.1,
        latitude=12.107502, longitude=-86.257586,
        floorLevel=1, isOutdoorAccessPoint=False
    ))

    # 6. Área de Mezclado
    subgraph.addNode(Node(
        nodeId="o_mixing_area",
        name="Área de Mezclado (Lab Materiales)",
        category=CampusCategory.FACULTY,
        xPercent=43.1, yPercent=32.2,
        latitude=12.107490, longitude=-86.257570,
        floorLevel=1, isOutdoorAccessPoint=False
    ))

    # 7. Área de Curado
    subgraph.addNode(Node(
        nodeId="o_curing_area",
        name="Área de Curado (Lab Materiales)",
        category=CampusCategory.FACULTY,
        xPercent=43.2, yPercent=32.3,
        latitude=12.107485, longitude=-86.257560,
        floorLevel=1, isOutdoorAccessPoint=False
    ))

    # 8. Técnicos de Laboratorio
    subgraph.addNode(Node(
        nodeId="o_lab_technicians",
        name="Oficina de Técnicos de Laboratorio",
        category=CampusCategory.ADMINISTRATIVE,
        xPercent=43.1, yPercent=32.0,
        latitude=12.107510, longitude=-86.257575,
        floorLevel=1, isOutdoorAccessPoint=False
    ))

    # 9. Lab Mecánica de Fluidos
    subgraph.addNode(Node(
        nodeId="o_lab_fluidos",
        name="Laboratorio de Mecánica de Fluidos",
        category=CampusCategory.FACULTY,
        xPercent=43.2, yPercent=32.1,
        latitude=12.107515, longitude=-86.257550,
        floorLevel=1, isOutdoorAccessPoint=False
    ))

    # 10. Coordinación de Gestión Integral de Riesgos de Desastres (O-105)
    subgraph.addNode(Node(
        nodeId="o_riesgos_105",
        name="Coordinación de Gestión Integral de Riesgos de Desastres (O-105)",
        category=CampusCategory.ADMINISTRATIVE,
        xPercent=43.3, yPercent=32.4,
        latitude=12.107545, longitude=-86.257437,
        floorLevel=1, isOutdoorAccessPoint=False
    ))

    # 11. Baños Hombres (Anexo FIA)
    subgraph.addNode(Node(
        nodeId="o_restrooms_men",
        name="Servicios Sanitarios Hombres (Anexo FIA)",
        category=CampusCategory.RESTROOM,
        xPercent=41.5, yPercent=30.0,
        latitude=12.108151, longitude=-86.257888,
        floorLevel=1, isOutdoorAccessPoint=False
    ))

    # 12. Baños Mujeres (Anexo FIA)
    subgraph.addNode(Node(
        nodeId="o_restrooms_women",
        name="Servicios Sanitarios Mujeres (Anexo FIA)",
        category=CampusCategory.RESTROOM,
        xPercent=41.5, yPercent=30.0,
        latitude=12.108151, longitude=-86.257888,
        floorLevel=1, isOutdoorAccessPoint=False
    ))

    # 13. Sala de Maestros FIA (Anexo Norte)
    subgraph.addNode(Node(
        nodeId="o_teachers_lounge",
        name="Sala de Maestros FIA (Anexo Norte)",
        category=CampusCategory.FACULTY,
        xPercent=41.3, yPercent=29.8,
        latitude=12.108229, longitude=-86.257948,
        floorLevel=1, isOutdoorAccessPoint=False
    ))

    # 14. Escaleras Interiores Edificio O (Piso 1)
    subgraph.addNode(Node(
        nodeId="o_stairs_f1",
        name="Escaleras Interiores Edificio O (Piso 1)",
        category=CampusCategory.STAIRS,
        xPercent=43.3, yPercent=32.2,
        latitude=12.107554, longitude=-86.257487,
        floorLevel=1, isOutdoorAccessPoint=False
    ))

    # 15. Escaleras del O al Parqueo
    subgraph.addNode(Node(
        nodeId="o_stairs_parking",
        name="Escaleras del O al Parqueo",
        category=CampusCategory.STAIRS,
        xPercent=43.4, yPercent=32.3,
        latitude=12.107591, longitude=-86.257458,
        floorLevel=1, isOutdoorAccessPoint=True
    ))

    # 16. Rampa del O a la Acera del Parqueo
    subgraph.addNode(Node(
        nodeId="o_ramp_parking",
        name="Rampa Accesible del O al Parqueo",
        category=CampusCategory.ACCESSIBLE_RAMP,
        xPercent=43.5, yPercent=32.4,
        latitude=12.107612, longitude=-86.257442,
        floorLevel=1, isOutdoorAccessPoint=True
    ))

    # 17. De la Acera al Parqueo del O
    subgraph.addNode(Node(
        nodeId="o_sidewalk_parking",
        name="Acera hacia Parqueo del Edificio O",
        category=CampusCategory.PARKING_LOT,
        xPercent=43.7, yPercent=32.6,
        latitude=12.107675, longitude=-86.257388,
        floorLevel=1, isOutdoorAccessPoint=True
    ))

    # =========================================================================
    # FLOOR 2 (SEGUNDO PISO)
    # =========================================================================

    # 18. Escaleras Interiores Edificio O (Piso 2)
    subgraph.addNode(Node(
        nodeId="o_stairs_f2",
        name="Escaleras Interiores Edificio O (Piso 2)",
        category=CampusCategory.STAIRS,
        xPercent=43.3, yPercent=32.2,
        latitude=12.107554, longitude=-86.257487,
        floorLevel=2, isOutdoorAccessPoint=False
    ))

    # 19. Lab Redes O-201
    subgraph.addNode(Node(
        nodeId="o_lab_redes_201",
        name="Laboratorio de Redes O-201",
        category=CampusCategory.CLASSROOM,
        xPercent=43.1, yPercent=32.1,
        latitude=12.107520, longitude=-86.257586,
        floorLevel=2, isOutdoorAccessPoint=False
    ))

    # 20. Centro de Redes
    subgraph.addNode(Node(
        nodeId="o_networks_center",
        name="Centro de Redes (Edificio O)",
        category=CampusCategory.ADMINISTRATIVE,
        xPercent=43.2, yPercent=32.1,
        latitude=12.107550, longitude=-86.257575,
        floorLevel=2, isOutdoorAccessPoint=False
    ))

    # 21. Centro de Inteligencia Artificial y Robótica (CIAR)
    subgraph.addNode(Node(
        nodeId="o_ciar",
        name="Centro de Inteligencia Artificial y Robótica (CIAR)",
        category=CampusCategory.FACULTY,
        xPercent=43.3, yPercent=32.0,
        latitude=12.107599, longitude=-86.257561,
        floorLevel=2, isOutdoorAccessPoint=False
    ))

    # 22. Robótica
    subgraph.addNode(Node(
        nodeId="o_robotics",
        name="Área de Robótica (CIAR)",
        category=CampusCategory.FACULTY,
        xPercent=43.3, yPercent=32.0,
        latitude=12.107585, longitude=-86.257567,
        floorLevel=2, isOutdoorAccessPoint=False
    ))

    # 23. Bebedero de Agua (Piso 2)
    subgraph.addNode(Node(
        nodeId="o_fountain_f2",
        name="Bebedero de Agua (Edificio O - Piso 2)",
        category=CampusCategory.DRINKING_FOUNTAIN,
        xPercent=43.3, yPercent=32.0,
        latitude=12.107585, longitude=-86.257567,
        floorLevel=2, isOutdoorAccessPoint=False
    ))

    # 24. Sala de Tutoría
    subgraph.addNode(Node(
        nodeId="o_tutoring_room",
        name="Sala de Tutoría FIA",
        category=CampusCategory.CLASSROOM,
        xPercent=43.4, yPercent=31.9,
        latitude=12.107632, longitude=-86.257548,
        floorLevel=2, isOutdoorAccessPoint=False
    ))

    # 25. Aula O-202
    subgraph.addNode(Node(
        nodeId="o_room_202",
        name="Aula O-202",
        category=CampusCategory.CLASSROOM,
        xPercent=43.6, yPercent=31.8,
        latitude=12.107741, longitude=-86.257507,
        floorLevel=2, isOutdoorAccessPoint=False
    ))

    # =========================================================================
    # CORRIDORS / WALKWAYS - FLOOR 1
    # =========================================================================

    # Lobby & Central Hallway: Mapa UAM <-> Lab Materiales O-104
    subgraph.addBidirectionalWalkway(
        "o_mapa_uam", "o_lab_materiales_104",
        _calcDist(12.107478, -86.257555, 12.107502, -86.257586, 4.3),
        isAccessible=True,
        forwardInstruction="Avanza 4m hacia el Laboratorio de Resistencia de Materiales (O-104).",
        backwardInstruction="Camina 4m hacia el Mapa UAM y directorio de entrada."
    )

    # Mapa UAM <-> Escaleras Interiores Piso 1
    subgraph.addBidirectionalWalkway(
        "o_mapa_uam", "o_stairs_f1",
        _calcDist(12.107478, -86.257555, 12.107554, -86.257487, 11.2),
        isAccessible=True,
        forwardInstruction="Avanza 11m por el pasillo hacia las escaleras interiores para subir al Piso 2.",
        backwardInstruction="Avanza 11m hacia el Mapa UAM en la entrada principal."
    )

    # Mapa UAM <-> Lab Mecánica de Suelos O-102
    subgraph.addBidirectionalWalkway(
        "o_mapa_uam", "o_lab_suelos_102",
        _calcDist(12.107478, -86.257555, 12.107535, -86.257643, 11.5),
        isAccessible=True,
        forwardInstruction="Camina 11m al noroeste hacia el Laboratorio de Mecánica de Suelos (O-102).",
        backwardInstruction="Camina 11m hacia el Mapa UAM y salida principal."
    )

    # Suelos O-102 <-> Área de Exhibición
    subgraph.addBidirectionalWalkway(
        "o_lab_suelos_102", "o_exhibition_area",
        4.2,
        isAccessible=True,
        forwardInstruction="Avanza 4m hacia el Área de Exhibición de proyectos.",
        backwardInstruction="Camina 4m hacia el Laboratorio de Mecánica de Suelos (O-102)."
    )

    # Área de Exhibición <-> Lab Materiales O-104
    subgraph.addBidirectionalWalkway(
        "o_exhibition_area", "o_lab_materiales_104",
        3.6,
        isAccessible=True,
        forwardInstruction="Avanza 4m hacia el Laboratorio de Resistencia de Materiales (O-104).",
        backwardInstruction="Avanza 4m hacia el Área de Exhibición."
    )

    # Suelos O-102 <-> Facultad de Ingeniería y Arquitectura (O-101)
    subgraph.addBidirectionalWalkway(
        "o_lab_suelos_102", "o_fia_101",
        _calcDist(12.107535, -86.257643, 12.107664, -86.257761, 19.2),
        isAccessible=True,
        forwardInstruction="Avanza 19m al noroeste hacia la Decanatura de la Facultad de Ingeniería y Arquitectura (O-101).",
        backwardInstruction="Avanza 19m hacia el Laboratorio de Mecánica de Suelos (O-102)."
    )

    # Materiales O-104 <-> Área de Mezclado
    subgraph.addBidirectionalWalkway(
        "o_lab_materiales_104", "o_mixing_area",
        2.8,
        isAccessible=True,
        forwardInstruction="Pasa al área de mezclado del laboratorio de materiales.",
        backwardInstruction="Regresa al Laboratorio de Resistencia de Materiales (O-104)."
    )

    # Área de Mezclado <-> Área de Curado
    subgraph.addBidirectionalWalkway(
        "o_mixing_area", "o_curing_area",
        2.0,
        isAccessible=True,
        forwardInstruction="Avanza 2m hacia el área de curado de probetas de concreto.",
        backwardInstruction="Avanza 2m hacia el área de mezclado."
    )

    # Área de Curado <-> Mapa UAM
    subgraph.addBidirectionalWalkway(
        "o_curing_area", "o_mapa_uam",
        2.5,
        isAccessible=True,
        forwardInstruction="Sal hacia el vestíbulo y Mapa UAM.",
        backwardInstruction="Entra al área de curado del laboratorio."
    )

    # Materiales O-104 <-> Técnicos de Lab
    subgraph.addBidirectionalWalkway(
        "o_lab_materiales_104", "o_lab_technicians",
        2.5,
        isAccessible=True,
        forwardInstruction="Avanza 2.5m hacia la Oficina de Técnicos de Laboratorio.",
        backwardInstruction="Regresa al Laboratorio de Resistencia de Materiales (O-104)."
    )

    # Técnicos de Lab <-> Lab Mecánica de Fluidos
    subgraph.addBidirectionalWalkway(
        "o_lab_technicians", "o_lab_fluidos",
        2.9,
        isAccessible=True,
        forwardInstruction="Avanza 3m hacia el Laboratorio de Mecánica de Fluidos.",
        backwardInstruction="Avanza 3m hacia la Oficina de Técnicos de Laboratorio."
    )

    # Lab Mecánica de Fluidos <-> Escaleras Interiores Piso 1
    subgraph.addBidirectionalWalkway(
        "o_lab_fluidos", "o_stairs_f1",
        8.2,
        isAccessible=True,
        forwardInstruction="Avanza 8m por el pasillo hacia las escaleras interiores del Edificio O.",
        backwardInstruction="Avanza 8m hacia el Laboratorio de Mecánica de Fluidos."
    )

    # Escaleras Interiores F1 <-> Coordinación de Riesgos (O-105)
    subgraph.addBidirectionalWalkway(
        "o_stairs_f1", "o_riesgos_105",
        _calcDist(12.107554, -86.257487, 12.107545, -86.257437, 5.5),
        isAccessible=True,
        forwardInstruction="Avanza 5.5m hacia la Coordinación de Gestión Integral de Riesgos de Desastres (O-105).",
        backwardInstruction="Avanza 5.5m hacia las escaleras interiores del Edificio O."
    )

    # Riesgos O-105 <-> Escaleras del O al Parqueo
    subgraph.addBidirectionalWalkway(
        "o_riesgos_105", "o_stairs_parking",
        _calcDist(12.107545, -86.257437, 12.107591, -86.257458, 5.6),
        isAccessible=False,
        forwardInstruction="Baja las escaleras exteriores hacia el parqueo del Edificio O.",
        backwardInstruction="Sube las escaleras exteriores hacia la Coordinación de Riesgos (O-105)."
    )

    # Riesgos O-105 <-> Rampa del O a la Acera del Parqueo
    subgraph.addBidirectionalWalkway(
        "o_riesgos_105", "o_ramp_parking",
        _calcDist(12.107545, -86.257437, 12.107612, -86.257442, 7.5),
        isAccessible=True,
        forwardInstruction="Avanza 7.5m por la rampa accesible hacia la acera del parqueo.",
        backwardInstruction="Sube por la rampa accesible hacia la entrada del Edificio O."
    )

    # Escaleras Parqueo <-> Rampa Parqueo
    subgraph.addBidirectionalWalkway(
        "o_stairs_parking", "o_ramp_parking",
        2.9,
        isAccessible=True,
        forwardInstruction="Avanza hacia la rampa accesible del parqueo.",
        backwardInstruction="Avanza hacia las escaleras del parqueo."
    )

    # Rampa Parqueo <-> Acera del Parqueo
    subgraph.addBidirectionalWalkway(
        "o_ramp_parking", "o_sidewalk_parking",
        _calcDist(12.107612, -86.257442, 12.107675, -86.257388, 9.1),
        isAccessible=True,
        forwardInstruction="Avanza 9m por la acera hacia el área de estacionamiento del Edificio O.",
        backwardInstruction="Avanza 9m por la acera hacia la rampa accesible del Edificio O."
    )

    # =========================================================================
    # FIA ANEXO NORTE (SALA DE MAESTROS & BAÑOS)
    # =========================================================================

    # Decanatura FIA O-101 <-> Baños Hombres/Mujeres (Anexo)
    subgraph.addBidirectionalWalkway(
        "o_fia_101", "o_restrooms_men",
        55.0,
        isAccessible=True,
        forwardInstruction="Avanza 55m al norte por el corredor exterior hacia los servicios sanitarios del anexo FIA.",
        backwardInstruction="Avanza 55m al sur hacia la Decanatura de Ingeniería y Arquitectura (O-101)."
    )

    # Baños Hombres <-> Baños Mujeres (Mismo bloque)
    subgraph.addBidirectionalWalkway(
        "o_restrooms_men", "o_restrooms_women",
        2.0,
        isAccessible=True,
        forwardInstruction="Accede a los servicios sanitarios de mujeres.",
        backwardInstruction="Accede a los servicios sanitarios de hombres."
    )

    # Baños Anexo <-> Sala de Maestros FIA (Anexo Norte)
    subgraph.addBidirectionalWalkway(
        "o_restrooms_women", "o_teachers_lounge",
        _calcDist(12.108151, -86.257888, 12.108229, -86.257948, 10.9),
        isAccessible=True,
        forwardInstruction="Avanza 11m al norte hacia la Sala de Maestros FIA (Anexo Norte).",
        backwardInstruction="Avanza 11m al sur hacia los servicios sanitarios del anexo FIA."
    )

    # =========================================================================
    # VERTICAL CONNECTION (FLOOR 1 <-> FLOOR 2 VIA ESCALERAS INTERIORES)
    # =========================================================================
    subgraph.addBidirectionalWalkway(
        "o_stairs_f1", "o_stairs_f2",
        4.0,
        isAccessible=False,
        forwardInstruction="Sube las escaleras del Edificio O al Segundo Piso (CIAR, Robótica, Redes, Tutoría).",
        backwardInstruction="Baja las escaleras del Edificio O a la Planta Baja (Laboratorios Civiles, Decanatura FIA)."
    )

    # =========================================================================
    # CORRIDORS / WALKWAYS - FLOOR 2 (SEGUNDO PISO)
    # =========================================================================

    # Escaleras Piso 2 <-> CIAR
    subgraph.addBidirectionalWalkway(
        "o_stairs_f2", "o_ciar",
        _calcDist(12.107554, -86.257487, 12.107599, -86.257561, 9.5),
        isAccessible=True,
        forwardInstruction="Avanza 9.5m por el pasillo hacia el Centro de Inteligencia Artificial y Robótica (CIAR).",
        backwardInstruction="Avanza 9.5m hacia las escaleras para descender al Piso 1."
    )

    # Escaleras Piso 2 <-> Centro de Redes
    subgraph.addBidirectionalWalkway(
        "o_stairs_f2", "o_networks_center",
        9.0,
        isAccessible=True,
        forwardInstruction="Avanza 9m por el pasillo hacia el Centro de Redes.",
        backwardInstruction="Avanza 9m hacia las escaleras interiores."
    )

    # Centro de Redes <-> Lab Redes O-201
    subgraph.addBidirectionalWalkway(
        "o_networks_center", "o_lab_redes_201",
        3.5,
        isAccessible=True,
        forwardInstruction="Entra al Laboratorio de Redes (O-201).",
        backwardInstruction="Sal al Centro de Redes."
    )

    # CIAR <-> Área de Robótica
    subgraph.addBidirectionalWalkway(
        "o_ciar", "o_robotics",
        _calcDist(12.107599, -86.257561, 12.107585, -86.257567, 1.7),
        isAccessible=True,
        forwardInstruction="Accede al área especializada de robótica del CIAR.",
        backwardInstruction="Regresa al área central del CIAR."
    )

    # Robótica <-> Bebedero Piso 2
    subgraph.addBidirectionalWalkway(
        "o_robotics", "o_fountain_f2",
        1.5,
        isAccessible=True,
        forwardInstruction="Avanza al bebedero de agua del Piso 2.",
        backwardInstruction="Avanza hacia el área de robótica."
    )

    # CIAR <-> Sala de Tutoría FIA
    subgraph.addBidirectionalWalkway(
        "o_ciar", "o_tutoring_room",
        _calcDist(12.107599, -86.257561, 12.107632, -86.257548, 3.9),
        isAccessible=True,
        forwardInstruction="Avanza 4m por el corredor hacia la Sala de Tutoría FIA.",
        backwardInstruction="Avanza 4m hacia el Centro de Inteligencia Artificial y Robótica (CIAR)."
    )

    # Sala de Tutoría <-> Aula O-202
    subgraph.addBidirectionalWalkway(
        "o_tutoring_room", "o_room_202",
        _calcDist(12.107632, -86.257548, 12.107741, -86.257507, 12.9),
        isAccessible=True,
        forwardInstruction="Avanza 13m hacia el Aula O-202 al final del pasillo norte.",
        backwardInstruction="Avanza 13m hacia la Sala de Tutoría FIA y CIAR."
    )

    # =========================================================================
    # ROOM QUERY SEARCH ALIASES & KEYWORDS
    # =========================================================================
    aliases = {
        # Floor 1
        "o-101": "o_fia_101",
        "o101": "o_fia_101",
        "fia": "o_fia_101",
        "ingenieria": "o_fia_101",
        "arquitectura": "o_fia_101",
        "decanatura fia": "o_fia_101",
        "facultad de ingenieria": "o_fia_101",

        "o-102": "o_lab_suelos_102",
        "o102": "o_lab_suelos_102",
        "suelos": "o_lab_suelos_102",
        "mecanica de suelos": "o_lab_suelos_102",
        "lab suelos": "o_lab_suelos_102",

        "exhibicion": "o_exhibition_area",
        "area de exhibicion": "o_exhibition_area",
        "exposicion": "o_exhibition_area",

        "o-104": "o_lab_materiales_104",
        "o104": "o_lab_materiales_104",
        "materiales": "o_lab_materiales_104",
        "resistencia de materiales": "o_lab_materiales_104",
        "lab materiales": "o_lab_materiales_104",

        "mezclado": "o_mixing_area",
        "area de mezclado": "o_mixing_area",

        "curado": "o_curing_area",
        "area de curado": "o_curing_area",
        "curado de concreto": "o_curing_area",

        "tecnicos": "o_lab_technicians",
        "tecnicos de lab": "o_lab_technicians",
        "oficina tecnicos": "o_lab_technicians",

        "fluidos": "o_lab_fluidos",
        "mecanica de fluidos": "o_lab_fluidos",
        "lab fluidos": "o_lab_fluidos",

        "baños hombres": "o_restrooms_men",
        "banos hombres": "o_restrooms_men",
        "sanitarios hombres": "o_restrooms_men",
        "baños": "o_restrooms_men",
        "banos": "o_restrooms_men",

        "baños mujeres": "o_restrooms_women",
        "banos mujeres": "o_restrooms_women",
        "sanitarios mujeres": "o_restrooms_women",

        "sala de maestros": "o_teachers_lounge",
        "maestros fia": "o_teachers_lounge",
        "profesores fia": "o_teachers_lounge",
        "anexo norte": "o_teachers_lounge",

        "o-105": "o_riesgos_105",
        "o105": "o_riesgos_105",
        "riesgos": "o_riesgos_105",
        "gestion de riesgos": "o_riesgos_105",
        "desastres": "o_riesgos_105",

        "mapa": "o_mapa_uam",
        "mapa uam": "o_mapa_uam",
        "directorio": "o_mapa_uam",

        "escaleras piso 1": "o_stairs_f1",
        "escaleras parqueo": "o_stairs_parking",
        "rampa": "o_ramp_parking",
        "rampa o": "o_ramp_parking",
        "rampa parqueo": "o_ramp_parking",
        "acera parqueo": "o_sidewalk_parking",
        "parqueo o": "o_sidewalk_parking",

        # Floor 2
        "o-201": "o_lab_redes_201",
        "o201": "o_lab_redes_201",
        "redes": "o_lab_redes_201",
        "lab redes": "o_lab_redes_201",

        "centro de redes": "o_networks_center",

        "ciar": "o_ciar",
        "inteligencia artificial": "o_ciar",
        "centro de inteligencia artificial": "o_ciar",

        "robotica": "o_robotics",
        "lab robotica": "o_robotics",

        "bebedero": "o_fountain_f2",
        "agua": "o_fountain_f2",
        "bebedero o": "o_fountain_f2",

        "tutoria": "o_tutoring_room",
        "sala de tutoria": "o_tutoring_room",
        "tutorias": "o_tutoring_room",

        "o-202": "o_room_202",
        "o202": "o_room_202",
        "aula o202": "o_room_202",
    }

    for alias, targetNodeId in aliases.items():
        subgraph.registerRoomAlias(alias, targetNodeId)

    return subgraph


# Singleton instance of Building O child graph
buildingOSubgraph = buildBuildingOSubgraph()
