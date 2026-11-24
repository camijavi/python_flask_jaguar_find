"""
sportsComplex.py
================================================================================
JAGUAR CENTER COMPLEX & SPORTS FIELDS SUBGRAPHS
================================================================================
Detailed pedestrian child graphs built from official UAM field GPS measurements
(coordenadas.txt) and directory (buildings.txt):
  1. jaguarCenterSubgraph: Jaguar Gym, Fisioterapia, Oficina de Deportes,
     Salón de Usos Múltiples DVE, Psicología Deportiva, Artes Marciales, Mapa UAM.
  2. sportsZoneSubgraph: Kiosko Jaguarcito, Baños Hombres/Mujeres, Bodega de
     Deportes, Cancha de Fútbol, Estadio Jaguar.
Weighted, Directed, Non-Complete Graphs G = (V, E, W).
================================================================================
"""

from backend.graph.directedGraph import Node
from backend.data.campusCategories import CampusCategory
from .buildingSubgraph import BuildingSubgraph, calcIndoorDistance as _calcDist


def buildJaguarCenterSubgraph() -> BuildingSubgraph:
    subgraph = BuildingSubgraph(
        buildingId="jaguarCenter",
        name="Complejo Deportivo Jaguar Center",
        code="JC",
        floors=[1],
        macroNodeId="jaguarCenter",
        entranceNodeIds=["jc_main_entry", "jc_gym", "jc_mapa_uam"],
        description="Complejo Jaguar Center: Jaguar Gym, Clínica de Fisioterapia, Oficina de Deportes, Artes Marciales, Usos Múltiples y Psicología Deportiva."
    )

    subgraph.addNode(Node(
        nodeId="jc_main_entry",
        name="Entrada Jaguar Center (junto a Edificio L)",
        category=CampusCategory.SPORTS,
        xPercent=79.5, yPercent=72.0,
        latitude=12.109111, longitude=-86.258514,
        floorLevel=1, isOutdoorAccessPoint=True,
        portalKind="door", buildingId="jaguarCenter"
    ))
    subgraph.addNode(Node(
        nodeId="jc_physiotherapy",
        name="Clínica de Fisioterapia",
        category=CampusCategory.MEDICAL_LAB,
        xPercent=81.5, yPercent=79.8,
        latitude=12.109303, longitude=-86.258511,
        floorLevel=1, isOutdoorAccessPoint=True,
        portalKind="door", buildingId="physiotherapy"
    ))
    subgraph.addNode(Node(
        nodeId="jc_gym",
        name="Jaguar Gym y Bebedero",
        category=CampusCategory.SPORTS,
        xPercent=80.8, yPercent=83.0,
        latitude=12.109309, longitude=-86.258508,
        floorLevel=1, isOutdoorAccessPoint=True,
        portalKind="door", buildingId="jaguarGym"
    ))
    subgraph.addNode(Node(
        nodeId="jc_sports_office",
        name="Oficina de Deportes",
        category=CampusCategory.SPORTS,
        xPercent=86.5, yPercent=80.5,
        latitude=12.109252, longitude=-86.258709,
        floorLevel=1, isOutdoorAccessPoint=False,
        buildingId="jaguarCenter"
    ))
    subgraph.addNode(Node(
        nodeId="jc_martial_arts",
        name="Salón de Artes Marciales",
        category=CampusCategory.SPORTS,
        xPercent=90.0, yPercent=82.0,
        latitude=12.109284, longitude=-86.258871,
        floorLevel=1, isOutdoorAccessPoint=False,
        buildingId="jaguarCenter"
    ))
    subgraph.addNode(Node(
        nodeId="jc_sports_psych",
        name="Oficina de Psicología Deportiva",
        category=CampusCategory.ADMINISTRATIVE,
        xPercent=90.0, yPercent=84.0,
        latitude=12.109280, longitude=-86.258880,
        floorLevel=1, isOutdoorAccessPoint=False,
        buildingId="jaguarCenter"
    ))
    subgraph.addNode(Node(
        nodeId="jc_multipurpose",
        name="Salón de Usos Múltiples (DVE)",
        category=CampusCategory.SPORTS,
        xPercent=90.0, yPercent=86.0,
        latitude=12.109279, longitude=-86.258881,
        floorLevel=1, isOutdoorAccessPoint=False,
        buildingId="jaguarCenter"
    ))
    subgraph.addNode(Node(
        nodeId="jc_mapa_uam",
        name="Mapa UAM (Complejo Jaguar Center)",
        category=CampusCategory.ADMINISTRATIVE,
        xPercent=90.2, yPercent=88.0,
        latitude=12.109332, longitude=-86.258882,
        floorLevel=1, isOutdoorAccessPoint=True,
        portalKind="door", buildingId="jaguarCenter"
    ))

    edges = [
        ("jc_main_entry", "jc_physiotherapy"),
        ("jc_physiotherapy", "jc_gym"),
        ("jc_physiotherapy", "jc_sports_office"),
        ("jc_gym", "jc_sports_office"),
        ("jc_sports_office", "jc_martial_arts"),
        ("jc_martial_arts", "jc_sports_psych"),
        ("jc_sports_psych", "jc_multipurpose"),
        ("jc_multipurpose", "jc_mapa_uam"),
    ]
    for u, v in edges:
        nU, nV = subgraph.getNode(u), subgraph.getNode(v)
        subgraph.addBidirectionalCorridor(u, v, _calcDist(nU.latitude, nU.longitude, nV.latitude, nV.longitude), isAccessible=True)

    aliases = {
        "jaguar gym": "jc_gym", "gimnasio": "jc_gym", "gym": "jc_gym",
        "fisioterapia": "jc_physiotherapy", "clinica fisioterapia": "jc_physiotherapy",
        "oficina de deportes": "jc_sports_office",
        "artes marciales": "jc_martial_arts", "salon de artes marciales": "jc_martial_arts",
        "psicologia deportiva": "jc_sports_psych",
        "usos multiples": "jc_multipurpose", "salon de usos multiples": "jc_multipurpose",
    }
    for alias, nid in aliases.items():
        subgraph.registerRoomAlias(alias, nid)

    return subgraph


def buildSportsZoneSubgraph() -> BuildingSubgraph:
    subgraph = BuildingSubgraph(
        buildingId="sportsZone",
        name="Campos Deportivos (Estadio Jaguar & Cancha de Fútbol)",
        code="SP",
        floors=[1],
        macroNodeId="sportsZone",
        entranceNodeIds=["sp_kiosk_jaguarcito", "sp_soccer_left", "sp_baseball_stadium", "sp_soccer_field"],
        description="Campos Deportivos: Kiosko Jaguarcito, Baños Hombres y Mujeres, Bodega de Deportes, Cancha de Fútbol y Estadio de Béisbol Jaguar."
    )

    subgraph.addNode(Node(
        nodeId="sp_kiosk_jaguarcito",
        name="Kiosko Jaguarcito",
        category=CampusCategory.FOOD_AREA,
        xPercent=61.0, yPercent=39.8,
        latitude=12.108100, longitude=-86.257939,
        floorLevel=1, isOutdoorAccessPoint=True,
        portalKind="door", buildingId="sportsZone"
    ))
    subgraph.addNode(Node(
        nodeId="sp_restrooms_women",
        name="Servicios Sanitarios Mujeres (Campos Deportivos)",
        category=CampusCategory.RESTROOM,
        xPercent=60.5, yPercent=40.5,
        latitude=12.108083, longitude=-86.257861,
        floorLevel=1, isOutdoorAccessPoint=True,
        buildingId="sportsZone"
    ))
    subgraph.addNode(Node(
        nodeId="sp_restrooms_men",
        name="Servicios Sanitarios Hombres (Campos Deportivos)",
        category=CampusCategory.RESTROOM,
        xPercent=61.5, yPercent=40.5,
        latitude=12.108105, longitude=-86.257954,
        floorLevel=1, isOutdoorAccessPoint=True,
        buildingId="sportsZone"
    ))
    subgraph.addNode(Node(
        nodeId="sp_sports_warehouse",
        name="Bodega de Deportes",
        category=CampusCategory.SPORTS,
        xPercent=70.5, yPercent=41.5,
        latitude=12.108164, longitude=-86.258313,
        floorLevel=1, isOutdoorAccessPoint=True,
        buildingId="sportsZone"
    ))
    subgraph.addNode(Node(
        nodeId="sp_soccer_left",
        name="Cancha de Fútbol (Entrada Izquierda)",
        category=CampusCategory.SPORTS,
        xPercent=76.5, yPercent=43.2,
        latitude=12.108181, longitude=-86.258504,
        floorLevel=1, isOutdoorAccessPoint=True,
        portalKind="door", buildingId="sportsZone"
    ))
    subgraph.addNode(Node(
        nodeId="sp_soccer_field",
        name="Campo de Fútbol Jaguar",
        category=CampusCategory.SPORTS,
        xPercent=77.5, yPercent=50.0,
        latitude=12.108450, longitude=-86.258461,
        floorLevel=1, isOutdoorAccessPoint=True,
        portalKind="door", buildingId="sportsZone"
    ))
    subgraph.addNode(Node(
        nodeId="sp_baseball_stadium",
        name="Estadio de Béisbol (Jaguar Stadium)",
        category=CampusCategory.SPORTS,
        xPercent=76.5, yPercent=34.0,
        latitude=12.107238, longitude=-86.258449,
        floorLevel=1, isOutdoorAccessPoint=True,
        portalKind="door", buildingId="sportsZone"
    ))

    edges = [
        ("sp_kiosk_jaguarcito", "sp_restrooms_women"),
        ("sp_kiosk_jaguarcito", "sp_restrooms_men"),
        ("sp_restrooms_men", "sp_sports_warehouse"),
        ("sp_sports_warehouse", "sp_soccer_left"),
        ("sp_soccer_left", "sp_soccer_field"),
        ("sp_soccer_left", "sp_baseball_stadium"),
    ]
    for u, v in edges:
        nU, nV = subgraph.getNode(u), subgraph.getNode(v)
        subgraph.addBidirectionalCorridor(u, v, _calcDist(nU.latitude, nU.longitude, nV.latitude, nV.longitude), isAccessible=True)

    aliases = {
        "jaguarcito": "sp_kiosk_jaguarcito", "kiosko jaguarcito": "sp_kiosk_jaguarcito",
        "bodega de deportes": "sp_sports_warehouse",
        "cancha de futbol": "sp_soccer_field", "campo de futbol": "sp_soccer_field",
        "jaguar campo futbol": "sp_soccer_field", "futbol": "sp_soccer_field",
        "estadio": "sp_baseball_stadium", "jaguar stadium": "sp_baseball_stadium",
        "estadio de beisbol": "sp_baseball_stadium", "baseball": "sp_baseball_stadium",
    }
    for alias, nid in aliases.items():
        subgraph.registerRoomAlias(alias, nid)

    return subgraph


jaguarCenterSubgraph = buildJaguarCenterSubgraph()
sportsZoneSubgraph = buildSportsZoneSubgraph()
