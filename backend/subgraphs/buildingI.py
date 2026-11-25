"""
buildingI.py
================================================================================
BUILDING I (RECTORÍA, PRESIDENCIA & BIBLIOTECA PABLO ANTONIO CUADRA) SUBGRAPH
================================================================================
Single-floor indoor & accessible ramp child graph built strictly from official
UAM room directory (buildings.txt) and field GPS measurements (coordenadas.txt).
Weighted, Directed, Non-Complete Graph G = (V, E, W).
================================================================================
"""

from backend.graph.directedGraph import Node
from backend.data.campusCategories import CampusCategory
from .buildingSubgraph import BuildingSubgraph, makeIndoorDistanceCalculator

_calcDist = makeIndoorDistanceCalculator(2.5)


def buildBuildingISubgraph() -> BuildingSubgraph:
    subgraph = BuildingSubgraph(
        buildingId="buildingI",
        name="Edificio I (Rectoría & Biblioteca Pablo Antonio Cuadra)",
        code="I",
        floors=[1],
        macroNodeId="buildingI",
        entranceNodeIds=["i_ramp_street", "i_ramp_jaguar_start", "i_stairs_lib_street", "i_ramp_lib"],
        description="Edificio I: Vicepresidencia, Sala de Reunión Directores, Dirección Académica, Rectoría, Gerencia General, Secretaría General, Biblioteca Pablo Antonio Cuadra, Baños Biblioteca y Relaciones Públicas."
    )

    # =========================================================================
    # FLOOR 1 (PLANTA ÚNICA) — Exact order from buildings.txt
    # =========================================================================
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
        nodeId="i_sala_directores",
        name="Sala de Reunión Directores",
        category=CampusCategory.ADMINISTRATIVE,
        xPercent=66.2, yPercent=77.0,
        latitude=12.109255, longitude=-86.258170,
        floorLevel=1, isOutdoorAccessPoint=False,
        buildingId="buildingI"
    ))
    subgraph.addNode(Node(
        nodeId="i_dir_academica",
        name="Dirección Académica (Edificio I)",
        category=CampusCategory.ADMINISTRATIVE,
        xPercent=62.8, yPercent=74.8,
        latitude=12.109152, longitude=-86.257914,
        floorLevel=1, isOutdoorAccessPoint=False,
        buildingId="buildingI"
    ))
    subgraph.addNode(Node(
        nodeId="i_rectoria",
        name="Rectoría",
        category=CampusCategory.ADMINISTRATIVE,
        xPercent=64.7, yPercent=76.5,
        latitude=12.109237, longitude=-86.258051,
        floorLevel=1, isOutdoorAccessPoint=False,
        buildingId="buildingI"
    ))
    subgraph.addNode(Node(
        nodeId="i_gerencia_general",
        name="Gerencia General",
        category=CampusCategory.ADMINISTRATIVE,
        xPercent=64.9, yPercent=76.6,
        latitude=12.109237, longitude=-86.258051,
        floorLevel=1, isOutdoorAccessPoint=False,
        buildingId="buildingI"
    ))
    subgraph.addNode(Node(
        nodeId="i_secretaria_general",
        name="Secretaría General",
        category=CampusCategory.ADMINISTRATIVE,
        xPercent=65.1, yPercent=76.7,
        latitude=12.109237, longitude=-86.258051,
        floorLevel=1, isOutdoorAccessPoint=False,
        buildingId="buildingI"
    ))
    subgraph.addNode(Node(
        nodeId="i_oficina_reunion",
        name="Oficina / Sala de Reunión (Edificio I)",
        category=CampusCategory.ADMINISTRATIVE,
        xPercent=65.3, yPercent=76.8,
        latitude=12.109237, longitude=-86.258051,
        floorLevel=1, isOutdoorAccessPoint=False,
        buildingId="buildingI"
    ))
    subgraph.addNode(Node(
        nodeId="i_biblioteca",
        name="Biblioteca Pablo Antonio Cuadra",
        category=CampusCategory.ADMINISTRATIVE,
        xPercent=64.5, yPercent=83.0,
        latitude=12.109547, longitude=-86.257996,
        floorLevel=1, isOutdoorAccessPoint=True,
        portalKind="door", buildingId="buildingI"
    ))
    subgraph.addNode(Node(
        nodeId="i_restrooms_lib_men",
        name="Baños Biblioteca Hombres",
        category=CampusCategory.RESTROOM,
        xPercent=68.4, yPercent=82.5,
        latitude=12.109526, longitude=-86.258323,
        floorLevel=1, isOutdoorAccessPoint=False,
        buildingId="buildingI"
    ))
    subgraph.addNode(Node(
        nodeId="i_restrooms_lib_women",
        name="Baños Biblioteca Mujeres",
        category=CampusCategory.RESTROOM,
        xPercent=68.6, yPercent=82.5,
        latitude=12.109526, longitude=-86.258323,
        floorLevel=1, isOutdoorAccessPoint=False,
        buildingId="buildingI"
    ))
    subgraph.addNode(Node(
        nodeId="i_relaciones_publicas",
        name="Dirección de Relaciones Públicas",
        category=CampusCategory.ADMINISTRATIVE,
        xPercent=66.8, yPercent=77.4,
        latitude=12.109255, longitude=-86.258170,
        floorLevel=1, isOutdoorAccessPoint=False,
        buildingId="buildingI"
    ))
    # Supplementary landmarks, ramps & stairs from coordenadas.txt
    subgraph.addNode(Node(
        nodeId="i_presidencia",
        name="Presidencia UAM",
        category=CampusCategory.ADMINISTRATIVE,
        xPercent=66.5, yPercent=77.2,
        latitude=12.109255, longitude=-86.258170,
        floorLevel=1, isOutdoorAccessPoint=False,
        buildingId="buildingI"
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
        nodeId="i_mapa_uam",
        name="Mapa UAM (Edificio I)",
        category=CampusCategory.ADMINISTRATIVE,
        xPercent=64.5, yPercent=77.5,
        latitude=12.109270, longitude=-86.258021,
        floorLevel=1, isOutdoorAccessPoint=False,
        buildingId="buildingI"
    ))
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
        nodeId="i_ramp_end",
        name="Fin de Rampa Edificio I (Pasillo Principal)",
        category=CampusCategory.ACCESSIBLE_RAMP,
        xPercent=63.2, yPercent=75.2,
        latitude=12.109166, longitude=-86.257969,
        floorLevel=1, isOutdoorAccessPoint=False,
        portalKind="ramp", buildingId="buildingI"
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
        ("i_rectoria", "i_gerencia_general"),
        ("i_gerencia_general", "i_secretaria_general"),
        ("i_secretaria_general", "i_oficina_reunion"),
        ("i_rectoria", "i_mapa_uam"),
        ("i_rectoria", "i_presidencia"),
        ("i_presidencia", "i_sala_directores"),
        ("i_presidencia", "i_relaciones_publicas"),
        ("i_mapa_uam", "i_biblioteca"),
        ("i_biblioteca", "i_ramp_lib"),
        ("i_ramp_lib", "i_restrooms_lib_men"),
        ("i_biblioteca", "i_restrooms_lib_men"),
        ("i_restrooms_lib_men", "i_restrooms_lib_women"),
    ]
    for u, v in accEdges:
        nU, nV = subgraph.getNode(u), subgraph.getNode(v)
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
        "vicepresidencia": "i_vicepresidencia", "vicePresidencyI": "i_vicepresidencia",
        "sala de directores": "i_sala_directores", "sala de reunion directores": "i_sala_directores",
        "directorsMeetingRoomI": "i_sala_directores",
        "direccion academica": "i_dir_academica", "academicDirectorateI": "i_dir_academica",
        "rectoria": "i_rectoria", "rectorateOfficeI": "i_rectoria",
        "gerencia general": "i_gerencia_general", "generalManagementI": "i_gerencia_general",
        "secretaria general": "i_secretaria_general", "generalSecretariatI": "i_secretaria_general",
        "oficina sala de reunion": "i_oficina_reunion", "meetingRoomI": "i_oficina_reunion",
        "biblioteca": "i_biblioteca", "biblioteca central": "i_biblioteca",
        "pablo antonio cuadra": "i_biblioteca", "centralLibraryI": "i_biblioteca",
        "baños biblioteca": "i_restrooms_lib_men", "banos biblioteca": "i_restrooms_lib_men",
        "baños biblioteca hombre": "i_restrooms_lib_men", "restroomsLibraryMenI": "i_restrooms_lib_men",
        "i_restrooms_lib": "i_restrooms_lib_men",
        "baños biblioteca mujer": "i_restrooms_lib_women", "restroomsLibraryWomenI": "i_restrooms_lib_women",
        "relaciones publicas": "i_relaciones_publicas", "direccion de relaciones publicas": "i_relaciones_publicas",
        "publicRelationsI": "i_relaciones_publicas",
        "presidencia": "i_presidencia", "presidencyI": "i_presidencia",
        "rampa biblioteca": "i_ramp_lib", "rampa i": "i_ramp_street",
    }
    for alias, nid in aliases.items():
        subgraph.registerRoomAlias(alias, nid)

    return subgraph


buildingISubgraph = buildBuildingISubgraph()
