"""
buildingJ.py
================================================================================
BUILDING J (LABORATORIOS DE ODONTOLOGÍA) SUBGRAPH / CHILD GRAPH
================================================================================
Single-floor indoor child graph representation for Building J (Edificio J -
Laboratorios de Odontología Preclínica), strictly ordered per buildings.txt and
aligned with coordenadas.txt:
- Lab odonto J101 (12.108126, -86.256780)
- Lab odonto J102 (12.108094, -86.256756)
- Baños hombres (12.108030, -86.256830)
- Baños mujeres (12.108070, -86.256815)
- Mapa UAM físico en Edificio J (12.108097, -86.256693)
- Entrada Principal (12.108126, -86.256780)
================================================================================
"""

from backend.graph.directedGraph import Node
from backend.data.campusCategories import CampusCategory
from .buildingSubgraph import BuildingSubgraph, calcIndoorDistance as _calcDist


def buildBuildingJSubgraph() -> BuildingSubgraph:
    """
    Constructs the official child graph for Building J (Single Floor).
    """
    subgraph = BuildingSubgraph(
        buildingId="buildingJ",
        name="Edificio J (Laboratorios de Odontología)",
        code="J",
        floors=[1],
        macroNodeId="buildingJ",
        entranceNodeIds=["j_entrance", "j_uam_map"],
        description="Edificio J: Laboratorios de Odontología J101 y J102, Baños Hombres y Mujeres y Mapa UAM."
    )

    # =========================================================================
    # FLOOR 1 (PLANTA ÚNICA) — Exact order from buildings.txt
    # =========================================================================
    subgraph.addNode(Node(
        nodeId="j_lab_101",
        name="Laboratorio de Odontología J101",
        category=CampusCategory.DENTAL_LAB,
        xPercent=29.0, yPercent=44.0,
        latitude=12.108126, longitude=-86.256780,
        floorLevel=1, isOutdoorAccessPoint=False
    ))
    subgraph.addNode(Node(
        nodeId="j_lab_102",
        name="Laboratorio de Odontología J102",
        category=CampusCategory.DENTAL_LAB,
        xPercent=29.4, yPercent=44.4,
        latitude=12.108094, longitude=-86.256756,
        floorLevel=1, isOutdoorAccessPoint=False
    ))
    subgraph.addNode(Node(
        nodeId="j_restrooms_men",
        name="Baños Hombres (Edificio J)",
        category=CampusCategory.RESTROOM,
        xPercent=28.3, yPercent=44.9,
        latitude=12.108030, longitude=-86.256830,
        floorLevel=1, isOutdoorAccessPoint=False
    ))
    subgraph.addNode(Node(
        nodeId="j_restrooms_women",
        name="Baños Mujeres (Edificio J)",
        category=CampusCategory.RESTROOM,
        xPercent=28.6, yPercent=44.6,
        latitude=12.108070, longitude=-86.256815,
        floorLevel=1, isOutdoorAccessPoint=False
    ))
    subgraph.addNode(Node(
        nodeId="j_uam_map",
        name="Mapa UAM (Edificio J)",
        category=CampusCategory.ADMINISTRATIVE,
        xPercent=28.8, yPercent=44.2,
        latitude=12.108097, longitude=-86.256693,
        floorLevel=1, isOutdoorAccessPoint=True
    ))
    subgraph.addNode(Node(
        nodeId="j_entrance",
        name="Entrada Principal Edificio J",
        category=CampusCategory.DENTAL_LAB,
        xPercent=29.0, yPercent=44.0,
        latitude=12.108126, longitude=-86.256780,
        floorLevel=1, isOutdoorAccessPoint=True
    ))

    # =========================================================================
    # CORRIDORS / WALKWAYS (ACCESSIBLE - SINGLE FLOOR)
    # =========================================================================
    subgraph.addBidirectionalCorridor(
        "j_entrance", "j_lab_101",
        distanceMeters=2.0,
        isAccessible=True,
        forwardInstruction="Ingresa al Laboratorio de Odontología J101.",
        backwardInstruction="Sal hacia la entrada principal del Edificio J."
    )

    distEntToMap = _calcDist(12.108126, -86.256780, 12.108097, -86.256693, minDist=9.0)
    subgraph.addBidirectionalCorridor(
        "j_entrance", "j_uam_map",
        distanceMeters=distEntToMap,
        isAccessible=True,
        forwardInstruction="Avanza hacia el Mapa UAM físico del Edificio J.",
        backwardInstruction="Regresa hacia la entrada principal del Edificio J."
    )

    distEntToJ102 = _calcDist(12.108126, -86.256780, 12.108094, -86.256756, minDist=4.4)
    subgraph.addBidirectionalCorridor(
        "j_entrance", "j_lab_102",
        distanceMeters=distEntToJ102,
        isAccessible=True,
        forwardInstruction="Avanza hacia el Laboratorio de Odontología J102.",
        backwardInstruction="Camina hacia la entrada del Edificio J."
    )

    subgraph.addBidirectionalCorridor(
        "j_lab_101", "j_lab_102",
        distanceMeters=distEntToJ102,
        isAccessible=True,
        forwardInstruction="Avanza por el pasillo hacia el Laboratorio J102.",
        backwardInstruction="Avanza hacia el Laboratorio J101."
    )

    distEntToWomen = _calcDist(12.108126, -86.256780, 12.108070, -86.256815, minDist=7.3)
    subgraph.addBidirectionalCorridor(
        "j_entrance", "j_restrooms_women",
        distanceMeters=distEntToWomen,
        isAccessible=True,
        forwardInstruction="Camina por el pasillo hacia los servicios sanitarios de mujeres.",
        backwardInstruction="Regresa hacia la entrada y laboratorios de odontología."
    )

    distWomenToMen = _calcDist(12.108070, -86.256815, 12.108030, -86.256830, minDist=4.7)
    subgraph.addBidirectionalCorridor(
        "j_restrooms_women", "j_restrooms_men",
        distanceMeters=distWomenToMen,
        isAccessible=True,
        forwardInstruction="Avanza unos pasos hacia los servicios sanitarios de hombres.",
        backwardInstruction="Avanza unos pasos hacia los servicios sanitarios de mujeres."
    )

    distJ102ToWomen = _calcDist(12.108094, -86.256756, 12.108070, -86.256815, minDist=7.0)
    subgraph.addBidirectionalCorridor(
        "j_lab_102", "j_restrooms_women",
        distanceMeters=distJ102ToWomen,
        isAccessible=True,
        forwardInstruction="Camina hacia los servicios sanitarios de mujeres.",
        backwardInstruction="Avanza hacia el Laboratorio J102."
    )

    aliases = {
        "j101": "j_lab_101", "j-101": "j_lab_101", "lab odonto j101": "j_lab_101", "dentalLabJ101": "j_lab_101",
        "j102": "j_lab_102", "j-102": "j_lab_102", "lab odonto j102": "j_lab_102", "dentalLabJ102": "j_lab_102",
        "hombres": "j_restrooms_men", "banos hombres": "j_restrooms_men", "baños hombres": "j_restrooms_men", "restroomsMenJ": "j_restrooms_men",
        "mujeres": "j_restrooms_women", "banos mujeres": "j_restrooms_women", "baños mujeres": "j_restrooms_women", "restroomsWomenJ": "j_restrooms_women",
        "mapa j": "j_uam_map", "mapa uam j": "j_uam_map", "uamMapJ": "j_uam_map",
        "entrada j": "j_entrance", "entranceJ": "j_entrance",
    }
    for alias, nid in aliases.items():
        subgraph.registerRoomAlias(alias, nid)

    return subgraph


buildingJSubgraph = buildBuildingJSubgraph()
