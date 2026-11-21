"""
buildingJ.py
================================================================================
BUILDING J (LABORATORIOS DE ODONTOLOGÍA) SUBGRAPH / CHILD GRAPH
================================================================================
Single-floor indoor child graph representation for Building J (Edificio J -
Laboratorios de Odontología Preclínica), including:
- Entrada Principal (12.108126, -86.256780)
- Lab odonto J101 (12.108126, -86.256780)
- Lab odonto J102 (12.108094, -86.256756)
- Baños mujeres (12.108070, -86.256815)
- Baños hombres (12.108030, -86.256830)
================================================================================
"""

from backend.graph.directedGraph import Node
from backend.data.campusCategories import CampusCategory
from backend.graph.geoUtils import CampusGeoUtils
from .buildingSubgraph import BuildingSubgraph


def _calcDist(lat1: float, lng1: float, lat2: float, lng2: float, minDist: float = 2.0) -> float:
    """Helper to calculate distance in meters, enforcing a sensible minimum for indoor steps."""
    d = CampusGeoUtils.calculateHaversineDistance(lat1, lng1, lat2, lng2)
    return max(minDist, round(d, 1))


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
        entranceNodeIds=["j_entrance"],
        description="Edificio J de Laboratorios de Odontología Preclínica y Simulación de la UAM."
    )

    # =========================================================================
    # FLOOR 1 (PLANTA ÚNICA)
    # =========================================================================

    # 1. Acceso Principal Edificio J
    subgraph.addNode(Node(
        nodeId="j_entrance",
        name="Entrada Principal Edificio J",
        category=CampusCategory.DENTAL_LAB,
        xPercent=29.0, yPercent=44.0,
        latitude=12.108126, longitude=-86.256780,
        floorLevel=1, isOutdoorAccessPoint=True
    ))

    # 2. Lab Odontología J101
    subgraph.addNode(Node(
        nodeId="j_lab_101",
        name="Laboratorio de Odontología J-101",
        category=CampusCategory.DENTAL_LAB,
        xPercent=29.0, yPercent=44.0,
        latitude=12.108126, longitude=-86.256780,
        floorLevel=1, isOutdoorAccessPoint=False
    ))

    # 3. Lab Odontología J102
    subgraph.addNode(Node(
        nodeId="j_lab_102",
        name="Laboratorio de Odontología J-102",
        category=CampusCategory.DENTAL_LAB,
        xPercent=29.4, yPercent=44.4,
        latitude=12.108094, longitude=-86.256756,
        floorLevel=1, isOutdoorAccessPoint=False
    ))

    # 4. Baños de Mujeres
    subgraph.addNode(Node(
        nodeId="j_restrooms_women",
        name="Servicios Sanitarios Mujeres (Edificio J)",
        category=CampusCategory.RESTROOM,
        xPercent=28.6, yPercent=44.6,
        latitude=12.108070, longitude=-86.256815,
        floorLevel=1, isOutdoorAccessPoint=False
    ))

    # 5. Baños de Hombres
    subgraph.addNode(Node(
        nodeId="j_restrooms_men",
        name="Servicios Sanitarios Hombres (Edificio J)",
        category=CampusCategory.RESTROOM,
        xPercent=28.3, yPercent=44.9,
        latitude=12.108030, longitude=-86.256830,
        floorLevel=1, isOutdoorAccessPoint=False
    ))

    # =========================================================================
    # CORRIDORS / WALKWAYS (ACCESSIBLE - SINGLE FLOOR)
    # =========================================================================

    # Entrada <-> Lab J-101
    subgraph.addBidirectionalCorridor(
        "j_entrance", "j_lab_101",
        distanceMeters=2.0,
        isAccessible=True,
        forwardInstruction="Ingresa al Laboratorio de Odontología J-101.",
        backwardInstruction="Sal hacia la entrada principal del Edificio J."
    )

    # Entrada <-> Lab J-102 (4.4m Haversine)
    distEntToJ102 = _calcDist(12.108126, -86.256780, 12.108094, -86.256756, minDist=4.4)
    subgraph.addBidirectionalCorridor(
        "j_entrance", "j_lab_102",
        distanceMeters=distEntToJ102,
        isAccessible=True,
        forwardInstruction=f"Avanza {distEntToJ102:.0f}m al sureste hacia el Laboratorio de Odontología J-102.",
        backwardInstruction=f"Camina {distEntToJ102:.0f}m al noroeste hacia la entrada del Edificio J."
    )

    # Lab J-101 <-> Lab J-102
    subgraph.addBidirectionalCorridor(
        "j_lab_101", "j_lab_102",
        distanceMeters=distEntToJ102,
        isAccessible=True,
        forwardInstruction=f"Avanza {distEntToJ102:.0f}m por el pasillo hacia el Laboratorio J-102.",
        backwardInstruction=f"Avanza {distEntToJ102:.0f}m hacia el Laboratorio J-101."
    )

    # Entrada <-> Baños de Mujeres (7.3m Haversine)
    distEntToWomen = _calcDist(12.108126, -86.256780, 12.108070, -86.256815, minDist=7.3)
    subgraph.addBidirectionalCorridor(
        "j_entrance", "j_restrooms_women",
        distanceMeters=distEntToWomen,
        isAccessible=True,
        forwardInstruction=f"Camina {distEntToWomen:.0f}m al suroeste por el pasillo hacia los servicios sanitarios de mujeres.",
        backwardInstruction=f"Regresa {distEntToWomen:.0f}m hacia la entrada y laboratorios de odontología."
    )

    # Baños de Mujeres <-> Baños de Hombres (4.7m Haversine)
    distWomenToMen = _calcDist(12.108070, -86.256815, 12.108030, -86.256830, minDist=4.7)
    subgraph.addBidirectionalCorridor(
        "j_restrooms_women", "j_restrooms_men",
        distanceMeters=distWomenToMen,
        isAccessible=True,
        forwardInstruction="Avanza unos pasos hacia los servicios sanitarios de hombres.",
        backwardInstruction="Avanza unos pasos hacia los servicios sanitarios de mujeres."
    )

    # Lab J-102 <-> Baños de Mujeres (7.0m Haversine)
    distJ102ToWomen = _calcDist(12.108094, -86.256756, 12.108070, -86.256815, minDist=7.0)
    subgraph.addBidirectionalCorridor(
        "j_lab_102", "j_restrooms_women",
        distanceMeters=distJ102ToWomen,
        isAccessible=True,
        forwardInstruction=f"Camina {distJ102ToWomen:.0f}m hacia los servicios sanitarios de mujeres.",
        backwardInstruction=f"Avanza {distJ102ToWomen:.0f}m hacia el Laboratorio J-102."
    )

    return subgraph


buildingJSubgraph = buildBuildingJSubgraph()
