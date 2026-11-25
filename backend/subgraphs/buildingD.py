"""
buildingD.py
================================================================================
BUILDING D (ODONTOLOGÍA DIGITAL) SUBGRAPH / CHILD GRAPH
================================================================================
Single-floor indoor child graph representation for Building D (Edificio D -
Odontología Digital CAM-CAM), strictly ordered per buildings.txt and aligned
with coordenadas.txt:
- Aula D102 (12.108029, -86.256911)
- Laboratorio de odontología digital CAM-CAM (12.108046, -86.256819)
- Oficina de Servicio al cliente (12.108128, -86.256945)
- Sala de Reunión (12.108128, -86.256945)
- Mapa UAM (12.108128, -86.256945) - Entrada principal y directorio
================================================================================
"""

from backend.graph.directedGraph import Node
from backend.data.campusCategories import CampusCategory
from .buildingSubgraph import BuildingSubgraph, calcIndoorDistance as _calcDist


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
        description="Edificio D: Aula D102, Laboratorio de Odontología Digital CAM-CAM, Oficina de Servicio al Cliente y Sala de Reunión."
    )

    # =========================================================================
    # FLOOR 1 (PLANTA ÚNICA) — Exact order from buildings.txt
    # =========================================================================
    subgraph.addNode(Node(
        nodeId="d_room_102",
        name="Aula D102",
        category=CampusCategory.CLASSROOM,
        xPercent=31.2, yPercent=44.5,
        latitude=12.108029, longitude=-86.256911,
        floorLevel=1, isOutdoorAccessPoint=False
    ))
    subgraph.addNode(Node(
        nodeId="d_lab_cam_cam",
        name="Laboratorio de Odontología Digital CAM-CAM",
        category=CampusCategory.DENTAL_LAB,
        xPercent=32.2, yPercent=44.8,
        latitude=12.108046, longitude=-86.256819,
        floorLevel=1, isOutdoorAccessPoint=False
    ))
    subgraph.addNode(Node(
        nodeId="d_customer_service",
        name="Oficina de Servicio al Cliente",
        category=CampusCategory.ADMINISTRATIVE,
        xPercent=30.2, yPercent=43.2,
        latitude=12.108128, longitude=-86.256945,
        floorLevel=1, isOutdoorAccessPoint=False
    ))
    subgraph.addNode(Node(
        nodeId="d_meeting_room",
        name="Sala de Reunión (Edificio D)",
        category=CampusCategory.ADMINISTRATIVE,
        xPercent=30.4, yPercent=43.4,
        latitude=12.108128, longitude=-86.256945,
        floorLevel=1, isOutdoorAccessPoint=False
    ))
    subgraph.addNode(Node(
        nodeId="d_uam_map",
        name="Mapa UAM (Entrada Edificio D)",
        category=CampusCategory.ADMINISTRATIVE,
        xPercent=30.0, yPercent=43.0,
        latitude=12.108128, longitude=-86.256945,
        floorLevel=1, isOutdoorAccessPoint=True
    ))

    # =========================================================================
    # CORRIDORS / WALKWAYS (ACCESSIBLE - SINGLE FLOOR)
    # =========================================================================
    subgraph.addBidirectionalCorridor(
        "d_uam_map", "d_customer_service",
        distanceMeters=2.0,
        isAccessible=True,
        forwardInstruction="Avanza hacia la Oficina de Servicio al Cliente.",
        backwardInstruction="Camina hacia el Mapa UAM y salida del edificio."
    )
    subgraph.addBidirectionalCorridor(
        "d_customer_service", "d_meeting_room",
        distanceMeters=3.0,
        isAccessible=True,
        forwardInstruction="Dirígete a la Sala de Reunión adyacente a Servicio al Cliente.",
        backwardInstruction="Regresa al área de Servicio al Cliente."
    )
    subgraph.addBidirectionalCorridor(
        "d_uam_map", "d_meeting_room",
        distanceMeters=3.5,
        isAccessible=True,
        forwardInstruction="Camina hacia la Sala de Reunión en el vestíbulo.",
        backwardInstruction="Regresa al Mapa UAM y acceso principal."
    )

    distMapToD102 = _calcDist(12.108128, -86.256945, 12.108029, -86.256911, minDist=11.6)
    subgraph.addBidirectionalCorridor(
        "d_uam_map", "d_room_102",
        distanceMeters=distMapToD102,
        isAccessible=True,
        forwardInstruction="Avanza por el pasillo interior hacia el Aula D102.",
        backwardInstruction="Camina hacia el lobby y Mapa UAM."
    )

    distD102ToCam = _calcDist(12.108029, -86.256911, 12.108046, -86.256819, minDist=10.2)
    subgraph.addBidirectionalCorridor(
        "d_room_102", "d_lab_cam_cam",
        distanceMeters=distD102ToCam,
        isAccessible=True,
        forwardInstruction="Avanza por el pasillo hacia el Laboratorio de Odontología Digital CAM-CAM.",
        backwardInstruction="Camina hacia el Aula D102."
    )

    distMapToCam = _calcDist(12.108128, -86.256945, 12.108046, -86.256819, minDist=16.5)
    subgraph.addBidirectionalCorridor(
        "d_uam_map", "d_lab_cam_cam",
        distanceMeters=distMapToCam,
        isAccessible=True,
        forwardInstruction="Camina hacia el Laboratorio de Odontología Digital CAM-CAM.",
        backwardInstruction="Regresa hacia la entrada principal y Mapa UAM."
    )

    subgraph.addBidirectionalCorridor(
        "d_customer_service", "d_room_102",
        distanceMeters=distMapToD102,
        isAccessible=True,
        forwardInstruction="Avanza hacia el Aula D102.",
        backwardInstruction="Camina hacia la Oficina de Servicio al Cliente."
    )

    aliases = {
        "d102": "d_room_102", "d-102": "d_room_102", "aula d102": "d_room_102", "classroomD102": "d_room_102",
        "cam-cam": "d_lab_cam_cam", "cam cam": "d_lab_cam_cam", "odontologia digital": "d_lab_cam_cam", "camCamLabD": "d_lab_cam_cam",
        "servicio al cliente": "d_customer_service", "oficina de servicio al cliente": "d_customer_service", "customerServiceD": "d_customer_service",
        "sala de reunion": "d_meeting_room", "reunion": "d_meeting_room", "meetingRoomD": "d_meeting_room",
        "mapa d": "d_uam_map", "mapa uam d": "d_uam_map", "uamMapD": "d_uam_map",
    }
    for alias, nid in aliases.items():
        subgraph.registerRoomAlias(alias, nid)

    return subgraph


buildingDSubgraph = buildBuildingDSubgraph()
