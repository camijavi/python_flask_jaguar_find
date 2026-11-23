"""
buildingI.py
================================================================================
BUILDING I (RECTORÍA, PRESIDENCIA & BIBLIOTECA PABLO ANTONIO CUADRA) SUBGRAPH
================================================================================
Single-floor indoor & accessible ramp child graph built from official field GPS
measurements (coordenadas.txt) and room directory (buildings.txt).
Weighted, Directed, Non-Complete Graph G = (V, E, W).
================================================================================
"""

from backend.graph.directedGraph import Node
from backend.data.campusCategories import CampusCategory
from backend.graph.geoUtils import CampusGeoUtils
from .buildingSubgraph import BuildingSubgraph


def _calcDist(lat1: float, lng1: float, lat2: float, lng2: float, minDist: float = 2.5) -> float:
    d = CampusGeoUtils.calculateHaversineDistance(lat1, lng1, lat2, lng2)
    return max(minDist, round(d, 1))


def buildBuildingISubgraph() -> BuildingSubgraph:
    subgraph = BuildingSubgraph(
        buildingId="buildingI",
        name="Edificio I (Rectoría & Biblioteca Pablo Antonio Cuadra)",
        code="I",
        floors=[1],
        macroNodeId="buildingI",
        entranceNodeIds=["i_ramp_street", "i_ramp_jaguar_start", "i_stairs_lib_street", "i_ramp_lib"],
        description="Edificio I: Rectoría, Presidencia, Vicepresidencia, Dirección Académica, Secretaría General, Biblioteca Pablo Antonio Cuadra y sus rampas de acceso."
    )

    subgraph.addNode(Node(
        nodeId="i_ramp_jaguar_start",
        name="Inicio Rampa hacia Edificio I (camino Jaguar Center)",
        category=CampusCategory.ACCESSIBLE_RAMP,
        xPercent=60.5, yPercent=67.0,
        latitude=12.108893, longitude=-86.257875,
        floorLevel=1, isOutdoorAccessPoint=True,
        portalKind="ramp", buildingId="buildingI"
    ))
    subgraph.addNode(Node(
        nodeId="i_ramp_street",
        name="Rampa de la Calle hacia Edificio I",
        category=CampusCategory.ACCESSIBLE_RAMP,
        xPercent=61.3, yPercent=73.3,
        latitude=12.109096, longitude=-86.257858,
        floorLevel=1, isOutdoorAccessPoint=True,
        portalKind="ramp", buildingId="buildingI"
    ))
    subgraph.addNode(Node(
        nodeId="i_ramp_sidewalk_lib",
        name="Paso de Rampa hacia Acera de Biblioteca",
        category=CampusCategory.ACCESSIBLE_RAMP,
        xPercent=62.0, yPercent=75.0,
        latitude=12.109163, longitude=-86.257867,
        floorLevel=1, isOutdoorAccessPoint=True,
        portalKind="ramp", buildingId="buildingI"
    ))
    subgraph.addNode(Node(
        nodeId="i_vicepresidencia",
        name="Vicepresidencia y Mapa UAM",
        category=CampusCategory.ADMINISTRATIVE,
        xPercent=62.5, yPercent=73.8,
        latitude=12.109119, longitude=-86.257918,
        floorLevel=1, isOutdoorAccessPoint=False,
        buildingId="buildingI"
    ))
    subgraph.addNode(Node(
        nodeId="i_dir_academica",
        name="Dirección Académica",
        category=CampusCategory.ADMINISTRATIVE,
        xPercent=62.8, yPercent=74.8,
        latitude=12.109152, longitude=-86.257914,
        floorLevel=1, isOutdoorAccessPoint=False,
        buildingId="buildingI"
    ))
    subgraph.addNode(Node(
        nodeId="i_ramp_end",
        name="Fin de Rampa Edificio I (Pasillo Principal)",
        category=CampusCategory.ACCESSIBLE_RAMP,
        xPercent=63.2, yPercent=75.2,
        latitude=12.109166, longitude=-86.257969,
        floorLevel=1, isOutdoorAccessPoint=False,
        portalKind="ramp", buildingId="buildingI"
    ))
    subgraph.addNode(Node(
        nodeId="i_fountain",
        name="Bebedero de Agua (Edificio I)",
        category=CampusCategory.DRINKING_FOUNTAIN,
        xPercent=63.5, yPercent=75.5,
        latitude=12.109180, longitude=-86.257947,
        floorLevel=1, isOutdoorAccessPoint=False,
        buildingId="buildingI"
    ))
    subgraph.addNode(Node(
        nodeId="i_rectoria",
        name="Rectoría, Gerencia General y Secretaría General",
        category=CampusCategory.ADMINISTRATIVE,
        xPercent=64.7, yPercent=76.5,
        latitude=12.109237, longitude=-86.258051,
        floorLevel=1, isOutdoorAccessPoint=False,
        buildingId="buildingI"
    ))
    subgraph.addNode(Node(
        nodeId="i_mapa_uam",
        name="Mapa UAM (Edificio I)",
        category=CampusCategory.ADMINISTRATIVE,
        xPercent=64.5, yPercent=77.5,
        latitude=12.109270, longitude=-86.258021,
        floorLevel=1, isOutdoorAccessPoint=False,
        buildingId="buildingI"
    ))
    subgraph.addNode(Node(
        nodeId="i_presidencia",
        name="Presidencia UAM, Sala de Directores y Relaciones Públicas",
        category=CampusCategory.ADMINISTRATIVE,
        xPercent=66.5, yPercent=77.2,
        latitude=12.109255, longitude=-86.258170,
        floorLevel=1, isOutdoorAccessPoint=False,
        buildingId="buildingI"
    ))
    subgraph.addNode(Node(
        nodeId="i_stairs_lib_street",
        name="Escaleras de la Calle a Biblioteca Central",
        category=CampusCategory.STAIRS,
        xPercent=62.5, yPercent=82.0,
        latitude=12.109467, longitude=-86.257868,
        floorLevel=1, isOutdoorAccessPoint=True,
        portalKind="stairs", buildingId="buildingI"
    ))
    subgraph.addNode(Node(
        nodeId="i_biblioteca",
        name="Biblioteca Central Pablo Antonio Cuadra (Acceso)",
        category=CampusCategory.ADMINISTRATIVE,
        xPercent=64.5, yPercent=83.0,
        latitude=12.109547, longitude=-86.257996,
        floorLevel=1, isOutdoorAccessPoint=True,
        portalKind="door", buildingId="buildingI"
    ))
    subgraph.addNode(Node(
        nodeId="i_stairs_lib_front",
        name="Escaleras frente a Puerta de Biblioteca",
        category=CampusCategory.STAIRS,
        xPercent=65.5, yPercent=83.5,
        latitude=12.109603, longitude=-86.258056,
        floorLevel=1, isOutdoorAccessPoint=True,
        portalKind="stairs", buildingId="buildingI"
    ))
    subgraph.addNode(Node(
        nodeId="i_ramp_lib",
        name="Rampa Accesible de Biblioteca Central",
        category=CampusCategory.ACCESSIBLE_RAMP,
        xPercent=67.5, yPercent=83.2,
        latitude=12.109574, longitude=-86.258239,
        floorLevel=1, isOutdoorAccessPoint=True,
        portalKind="ramp", buildingId="buildingI"
    ))
    subgraph.addNode(Node(
        nodeId="i_restrooms_lib",
        name="Servicios Sanitarios Biblioteca (Izquierda Hombres, Derecha Mujeres)",
        category=CampusCategory.RESTROOM,
        xPercent=68.5, yPercent=82.5,
        latitude=12.109526, longitude=-86.258323,
        floorLevel=1, isOutdoorAccessPoint=False,
        buildingId="buildingI"
    ))

    # Accessible ramp corridors & hallways
    accEdges = [
        ("i_ramp_jaguar_start", "i_ramp_street"),
        ("i_ramp_street", "i_ramp_sidewalk_lib"),
        ("i_ramp_street", "i_vicepresidencia"),
        ("i_vicepresidencia", "i_dir_academica"),
        ("i_dir_academica", "i_ramp_end"),
        ("i_ramp_sidewalk_lib", "i_ramp_end"),
        ("i_ramp_end", "i_fountain"),
        ("i_fountain", "i_rectoria"),
        ("i_rectoria", "i_mapa_uam"),
        ("i_rectoria", "i_presidencia"),
        ("i_mapa_uam", "i_biblioteca"),
        ("i_biblioteca", "i_ramp_lib"),
        ("i_ramp_lib", "i_restrooms_lib"),
        ("i_biblioteca", "i_restrooms_lib"),
    ]
    for u, v in accEdges:
        nU, nV = subgraph.getNode(u), subgraph.getNode(v)
        wType = "ramp" if ("ramp" in u or "ramp" in v) else "indoor"
        subgraph.addBidirectionalCorridor(u, v, _calcDist(nU.latitude, nU.longitude, nV.latitude, nV.longitude), isAccessible=True)

    # Stairs edges (isAccessible = False)
    stairEdges = [
        ("i_stairs_lib_street", "i_biblioteca"),
        ("i_stairs_lib_front", "i_biblioteca"),
    ]
    for u, v in stairEdges:
        nU, nV = subgraph.getNode(u), subgraph.getNode(v)
        subgraph.addBidirectionalCorridor(u, v, _calcDist(nU.latitude, nU.longitude, nV.latitude, nV.longitude), isAccessible=False)

    aliases = {
        "rectoria": "i_rectoria", "gerencia general": "i_rectoria", "secretaria general": "i_rectoria",
        "presidencia": "i_presidencia", "sala de directores": "i_presidencia", "relaciones publicas": "i_presidencia",
        "vicepresidencia": "i_vicepresidencia", "direccion academica": "i_dir_academica",
        "biblioteca": "i_biblioteca", "biblioteca central": "i_biblioteca", "pablo antonio cuadra": "i_biblioteca",
        "baños biblioteca": "i_restrooms_lib", "banos biblioteca": "i_restrooms_lib",
        "rampa biblioteca": "i_ramp_lib", "rampa i": "i_ramp_street",
    }
    for alias, nid in aliases.items():
        subgraph.registerRoomAlias(alias, nid)

    return subgraph


buildingISubgraph = buildBuildingISubgraph()
