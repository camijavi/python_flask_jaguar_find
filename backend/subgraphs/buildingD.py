"""
buildingD.py
================================================================================
BUILDING D (ODONTOLOGÍA DIGITAL) SUBGRAPH / CHILD GRAPH
================================================================================
Single-floor indoor child graph representation for Building D (Edificio D -
Odontología Digital CAM-CAM), including:
- Aula D102 (12.108029, -86.256911)
- Laboratorio de odontología digital CAM-CAM (12.108046, -86.256819)
- Oficina de Servicio al cliente (12.108128, -86.256945)
- Sala de Reunión (12.108128, -86.256945)
- Mapa UAM (12.108128, -86.256945) - Entrada principal y directorio
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


def buildBuildingDSubgraph() -> BuildingSubgraph:
    """
    Constructs the official child graph for Building D (Just one floor).
    """
    subgraph = BuildingSubgraph(
        buildingId="buildingD",
        name="Edificio D (Odontología Digital)",
        code="D",
        floors=[1],
        macroNodeId="buildingD",
        entranceNodeIds=["d_uam_map"],
        description="Edificio D de Odontología Digital (CAM-CAM), Aulas y Atención al Cliente de la UAM."
    )

    # =========================================================================
    # FLOOR 1 (PLANTA ÚNICA)
    # =========================================================================

    # 1. Mapa UAM (Entrada principal y señalización exterior)
    subgraph.addNode(Node(
        nodeId="d_uam_map",
        name="Mapa UAM (Entrada Edificio D)",
        category=CampusCategory.ADMINISTRATIVE,
        xPercent=30.0, yPercent=43.0,
        latitude=12.108128, longitude=-86.256945,
        floorLevel=1, isOutdoorAccessPoint=True
    ))

    # 2. Oficina de Servicio al cliente
    subgraph.addNode(Node(
        nodeId="d_customer_service",
        name="Oficina de Servicio al Cliente",
        category=CampusCategory.ADMINISTRATIVE,
        xPercent=30.2, yPercent=43.2,
        latitude=12.108128, longitude=-86.256945,
        floorLevel=1, isOutdoorAccessPoint=False
    ))

    # 3. Sala de Reunión
    subgraph.addNode(Node(
        nodeId="d_meeting_room",
        name="Sala de Reunión (Edificio D)",
        category=CampusCategory.ADMINISTRATIVE,
        xPercent=30.4, yPercent=43.4,
        latitude=12.108128, longitude=-86.256945,
        floorLevel=1, isOutdoorAccessPoint=False
    ))

    # 4. Aula D102
    subgraph.addNode(Node(
        nodeId="d_room_102",
        name="Aula D-102",
        category=CampusCategory.CLASSROOM,
        xPercent=31.2, yPercent=44.5,
        latitude=12.108029, longitude=-86.256911,
        floorLevel=1, isOutdoorAccessPoint=False
    ))

    # 5. Laboratorio de odontología digital CAM-CAM
    subgraph.addNode(Node(
        nodeId="d_lab_cam_cam",
        name="Laboratorio de Odontología Digital CAM-CAM",
        category=CampusCategory.DENTAL_LAB,
        xPercent=32.2, yPercent=44.8,
        latitude=12.108046, longitude=-86.256819,
        floorLevel=1, isOutdoorAccessPoint=False
    ))

    # =========================================================================
    # CORRIDORS / WALKWAYS (ACCESSIBLE - SINGLE FLOOR)
    # =========================================================================

    # Lobby: Mapa UAM <-> Servicio al Cliente
    subgraph.addBidirectionalCorridor(
        "d_uam_map", "d_customer_service",
        distanceMeters=2.0,
        isAccessible=True,
        forwardInstruction="Avanza hacia la Oficina de Servicio al Cliente.",
        backwardInstruction="Camina hacia el Mapa UAM y salida del edificio."
    )

    # Lobby: Servicio al Cliente <-> Sala de Reunión
    subgraph.addBidirectionalCorridor(
        "d_customer_service", "d_meeting_room",
        distanceMeters=3.0,
        isAccessible=True,
        forwardInstruction="Dirígete a la Sala de Reunión adyacente a Servicio al Cliente.",
        backwardInstruction="Regresa al área de Servicio al Cliente."
    )

    # Lobby: Mapa UAM <-> Sala de Reunión
    subgraph.addBidirectionalCorridor(
        "d_uam_map", "d_meeting_room",
        distanceMeters=3.5,
        isAccessible=True,
        forwardInstruction="Camina hacia la Sala de Reunión en el vestíbulo.",
        backwardInstruction="Regresa al Mapa UAM y acceso principal."
    )

    # Pasillo: Mapa UAM <-> Aula D-102
    # Distancia Haversine real: ~11.6m
    distMapToD102 = _calcDist(12.108128, -86.256945, 12.108029, -86.256911, minDist=11.6)
    subgraph.addBidirectionalCorridor(
        "d_uam_map", "d_room_102",
        distanceMeters=distMapToD102,
        isAccessible=True,
        forwardInstruction=f"Avanza {distMapToD102:.0f}m al sur por el pasillo interior hacia el Aula D-102.",
        backwardInstruction=f"Camina {distMapToD102:.0f}m al norte hacia el lobby y Mapa UAM."
    )

    # Pasillo: Aula D-102 <-> Laboratorio CAM-CAM
    # Distancia Haversine real: ~10.2m
    distD102ToCam = _calcDist(12.108029, -86.256911, 12.108046, -86.256819, minDist=10.2)
    subgraph.addBidirectionalCorridor(
        "d_room_102", "d_lab_cam_cam",
        distanceMeters=distD102ToCam,
        isAccessible=True,
        forwardInstruction=f"Avanza {distD102ToCam:.0f}m al este por el pasillo hacia el Laboratorio CAM-CAM.",
        backwardInstruction=f"Camina {distD102ToCam:.0f}m al oeste hacia el Aula D-102."
    )

    # Pasillo: Mapa UAM <-> Laboratorio CAM-CAM (Conexión directa por corredor este)
    distMapToCam = _calcDist(12.108128, -86.256945, 12.108046, -86.256819, minDist=16.5)
    subgraph.addBidirectionalCorridor(
        "d_uam_map", "d_lab_cam_cam",
        distanceMeters=distMapToCam,
        isAccessible=True,
        forwardInstruction=f"Camina {distMapToCam:.0f}m hacia el Laboratorio de Odontología Digital CAM-CAM.",
        backwardInstruction=f"Regresa {distMapToCam:.0f}m hacia la entrada principal y Mapa UAM."
    )

    # Servicio al Cliente <-> Aula D-102
    subgraph.addBidirectionalCorridor(
        "d_customer_service", "d_room_102",
        distanceMeters=distMapToD102,
        isAccessible=True,
        forwardInstruction=f"Avanza {distMapToD102:.0f}m hacia el Aula D-102.",
        backwardInstruction=f"Camina hacia la Oficina de Servicio al Cliente."
    )

    return subgraph


buildingDSubgraph = buildBuildingDSubgraph()
