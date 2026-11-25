"""
sportsComplex.py
================================================================================
JAGUAR CENTER COMPLEX & SPORTS FIELDS SUBGRAPHS
================================================================================
Detailed pedestrian child graphs built strictly from official UAM room directory
(buildings.txt) and field GPS measurements (coordenadas.txt):
  1. jaguarCenterSubgraph (Complejo deportivo Jaguar Center + Bodega general y
     contenedores): Salón de Artes Marciales, Salón de Usos Múltiples - DVE,
     Cancha Multi-Usos, Cancha de Volleyball Arena, Kiosko Jaguar Sport,
     Clínica Fisioterapia, Gimnasio JAGUAR GYM, Oficina Psicología Deportiva,
     Bodega General, Oficinas Deportivas 1-3, Comedor de Colaboradores.
  2. sportsZoneSubgraph (Campos deportivos): Estadio de Baseball (Jaguar Stadium),
     Cancha de Fútbol, Baños Hombres, Baños Mujeres, Kiosko Jaguarcito,
     Oficinas de Deportes, Bodega de Deportes.
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
        description="Complejo Jaguar Center: Salón de Artes Marciales, Salón de Usos Múltiples - DVE, Cancha Multi-Usos, Cancha de Volleyball Arena, Kiosko Jaguar Sport, Clínica Fisioterapia, Gimnasio JAGUAR GYM, Psicología Deportiva, Bodega General y Comedor de Colaboradores."
    )

    # =========================================================================
    # FLOOR 1 — Exact order from buildings.txt (Complejo deportivo Jaguar Center)
    # =========================================================================
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
        nodeId="jc_multipurpose",
        name="Salón de Usos Múltiples - DVE",
        category=CampusCategory.SPORTS,
        xPercent=90.0, yPercent=86.0,
        latitude=12.109279, longitude=-86.258881,
        floorLevel=1, isOutdoorAccessPoint=False,
        buildingId="jaguarCenter"
    ))
    subgraph.addNode(Node(
        nodeId="jc_multipurpose_court",
        name="Cancha Multi-Usos (Jaguar Center)",
        category=CampusCategory.SPORTS,
        xPercent=85.5, yPercent=76.5,
        latitude=12.109195, longitude=-86.258695,
        floorLevel=1, isOutdoorAccessPoint=False,
        buildingId="jaguarCenter"
    ))
    subgraph.addNode(Node(
        nodeId="jc_beach_volleyball",
        name="Cancha de Volleyball Arena (Jaguar Center)",
        category=CampusCategory.SPORTS,
        xPercent=87.0, yPercent=78.0,
        latitude=12.109225, longitude=-86.258740,
        floorLevel=1, isOutdoorAccessPoint=False,
        buildingId="jaguarCenter"
    ))
    subgraph.addNode(Node(
        nodeId="jc_kiosk_sport",
        name="Kiosko Jaguar Sport",
        category=CampusCategory.FOOD_AREA,
        xPercent=86.0, yPercent=79.5,
        latitude=12.109245, longitude=-86.258720,
        floorLevel=1, isOutdoorAccessPoint=False,
        buildingId="jaguarCenter"
    ))
    subgraph.addNode(Node(
        nodeId="jc_physiotherapy",
        name="Clínica Fisioterapia",
        category=CampusCategory.MEDICAL_LAB,
        xPercent=81.5, yPercent=79.8,
        latitude=12.109303, longitude=-86.258511,
        floorLevel=1, isOutdoorAccessPoint=True,
        portalKind="door", buildingId="physiotherapy"
    ))
    subgraph.addNode(Node(
        nodeId="jc_gym",
        name="Gimnasio JAGUAR GYM y Bebedero",
        category=CampusCategory.SPORTS,
        xPercent=80.8, yPercent=83.0,
        latitude=12.109309, longitude=-86.258508,
        floorLevel=1, isOutdoorAccessPoint=True,
        portalKind="door", buildingId="jaguarGym"
    ))
    subgraph.addNode(Node(
        nodeId="jc_sports_psych",
        name="Oficina Psicología Deportiva",
        category=CampusCategory.ADMINISTRATIVE,
        xPercent=90.0, yPercent=84.0,
        latitude=12.109280, longitude=-86.258880,
        floorLevel=1, isOutdoorAccessPoint=False,
        buildingId="jaguarCenter"
    ))
    # Bodega general y contenedores (buildings.txt lines 370-373) & access points
    subgraph.addNode(Node(
        nodeId="jc_bodega_general",
        name="Bodega General y Contenedores",
        category=CampusCategory.ADMINISTRATIVE,
        xPercent=90.5, yPercent=85.5,
        latitude=12.109312, longitude=-86.258888,
        floorLevel=1, isOutdoorAccessPoint=False,
        buildingId="jaguarCenter"
    ))
    subgraph.addNode(Node(
        nodeId="jc_sports_office",
        name="Oficinas Deportivas 1-3 (Oficina de Deportes)",
        category=CampusCategory.SPORTS,
        xPercent=86.5, yPercent=80.5,
        latitude=12.109252, longitude=-86.258709,
        floorLevel=1, isOutdoorAccessPoint=False,
        buildingId="jaguarCenter"
    ))
    subgraph.addNode(Node(
        nodeId="jc_comedor_colaboradores",
        name="Comedor de Colaboradores",
        category=CampusCategory.FOOD_AREA,
        xPercent=90.6, yPercent=87.0,
        latitude=12.109312, longitude=-86.258888,
        floorLevel=1, isOutdoorAccessPoint=False,
        buildingId="jaguarCenter"
    ))
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
        ("jc_main_entry", "jc_multipurpose_court"),
        ("jc_multipurpose_court", "jc_beach_volleyball"),
        ("jc_beach_volleyball", "jc_kiosk_sport"),
        ("jc_kiosk_sport", "jc_sports_office"),
        ("jc_physiotherapy", "jc_gym"),
        ("jc_physiotherapy", "jc_sports_office"),
        ("jc_gym", "jc_sports_office"),
        ("jc_sports_office", "jc_martial_arts"),
        ("jc_martial_arts", "jc_sports_psych"),
        ("jc_sports_psych", "jc_multipurpose"),
        ("jc_multipurpose", "jc_bodega_general"),
        ("jc_bodega_general", "jc_comedor_colaboradores"),
        ("jc_comedor_colaboradores", "jc_mapa_uam"),
    ]
    for u, v in edges:
        nU, nV = subgraph.getNode(u), subgraph.getNode(v)
        subgraph.addBidirectionalCorridor(u, v, _calcDist(nU.latitude, nU.longitude, nV.latitude, nV.longitude), isAccessible=True)

    aliases = {
        "artes marciales": "jc_martial_arts", "salon de artes marciales": "jc_martial_arts", "martialArtsHallJC": "jc_martial_arts",
        "usos multiples": "jc_multipurpose", "salon de usos multiples": "jc_multipurpose", "multipurposeHallJC": "jc_multipurpose",
        "cancha multi usos": "jc_multipurpose_court", "cancha multi-usos": "jc_multipurpose_court", "cancha multiusos": "jc_multipurpose_court",
        "multipurposeCourtJC": "jc_multipurpose_court",
        "volleyball arena": "jc_beach_volleyball", "cancha de volleyball arena": "jc_beach_volleyball", "beachVolleyballJC": "jc_beach_volleyball",
        "kiosko jaguar sport": "jc_kiosk_sport", "jaguar sport": "jc_kiosk_sport", "kioskJaguarSportJC": "jc_kiosk_sport",
        "fisioterapia": "jc_physiotherapy", "clinica fisioterapia": "jc_physiotherapy", "physiotherapyClinic": "jc_physiotherapy",
        "jaguar gym": "jc_gym", "gimnasio": "jc_gym", "gym": "jc_gym", "jaguarGym": "jc_gym",
        "psicologia deportiva": "jc_sports_psych", "oficina psicologia deportiva": "jc_sports_psych", "sportsPsychJC": "jc_sports_psych",
        "bodega general": "jc_bodega_general", "bodega general y contenedores": "jc_bodega_general", "generalWarehouseJC": "jc_bodega_general",
        "oficina de deportes": "jc_sports_office", "oficinas deportivas": "jc_sports_office", "oficinas deportivas 1-3": "jc_sports_office",
        "sportsOfficesJC": "jc_sports_office",
        "comedor de colaboradores": "jc_comedor_colaboradores", "staffDiningJC": "jc_comedor_colaboradores",
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
        description="Campos Deportivos: Estadio de Baseball (Jaguar Stadium), Cancha de Fútbol, Baños Hombres y Mujeres, Kiosko Jaguarcito, Oficinas de Deportes y Bodega de Deportes."
    )

    # =========================================================================
    # FLOOR 1 — Exact order from buildings.txt (Campos deportivos)
    # =========================================================================
    subgraph.addNode(Node(
        nodeId="sp_baseball_stadium",
        name="Estadio de Baseball (Jaguar Stadium)",
        category=CampusCategory.SPORTS,
        xPercent=76.5, yPercent=34.0,
        latitude=12.107238, longitude=-86.258449,
        floorLevel=1, isOutdoorAccessPoint=True,
        portalKind="door", buildingId="sportsZone"
    ))
    subgraph.addNode(Node(
        nodeId="sp_soccer_field",
        name="Cancha de Fútbol",
        category=CampusCategory.SPORTS,
        xPercent=77.5, yPercent=50.0,
        latitude=12.108450, longitude=-86.258461,
        floorLevel=1, isOutdoorAccessPoint=True,
        portalKind="door", buildingId="sportsZone"
    ))
    subgraph.addNode(Node(
        nodeId="sp_restrooms_men",
        name="Baños Hombres (Campos Deportivos)",
        category=CampusCategory.RESTROOM,
        xPercent=61.5, yPercent=40.5,
        latitude=12.108105, longitude=-86.257954,
        floorLevel=1, isOutdoorAccessPoint=True,
        buildingId="sportsZone"
    ))
    subgraph.addNode(Node(
        nodeId="sp_restrooms_women",
        name="Baños Mujeres (Campos Deportivos)",
        category=CampusCategory.RESTROOM,
        xPercent=60.5, yPercent=40.5,
        latitude=12.108083, longitude=-86.257861,
        floorLevel=1, isOutdoorAccessPoint=True,
        buildingId="sportsZone"
    ))
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
        nodeId="sp_sports_office",
        name="Oficinas de Deportes",
        category=CampusCategory.SPORTS,
        xPercent=71.0, yPercent=42.5,
        latitude=12.109252, longitude=-86.258709,
        floorLevel=1, isOutdoorAccessPoint=False,
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

    edges = [
        ("sp_kiosk_jaguarcito", "sp_restrooms_women"),
        ("sp_kiosk_jaguarcito", "sp_restrooms_men"),
        ("sp_restrooms_men", "sp_sports_warehouse"),
        ("sp_sports_warehouse", "sp_soccer_left"),
        ("sp_soccer_left", "sp_soccer_field"),
        ("sp_soccer_left", "sp_baseball_stadium"),
        ("sp_soccer_field", "sp_sports_office"),
    ]
    for u, v in edges:
        nU, nV = subgraph.getNode(u), subgraph.getNode(v)
        subgraph.addBidirectionalCorridor(u, v, _calcDist(nU.latitude, nU.longitude, nV.latitude, nV.longitude), isAccessible=True)

    aliases = {
        "estadio": "sp_baseball_stadium", "jaguar stadium": "sp_baseball_stadium",
        "estadio de beisbol": "sp_baseball_stadium", "estadio de baseball": "sp_baseball_stadium",
        "baseball": "sp_baseball_stadium", "baseballStadium": "sp_baseball_stadium",
        "cancha de futbol": "sp_soccer_field", "campo de futbol": "sp_soccer_field",
        "jaguar campo futbol": "sp_soccer_field", "futbol": "sp_soccer_field", "soccerField": "sp_soccer_field",
        "restroomsMenSZ": "sp_restrooms_men", "restroomsWomenSZ": "sp_restrooms_women",
        "jaguarcito": "sp_kiosk_jaguarcito", "kiosko jaguarcito": "sp_kiosk_jaguarcito", "kioskJaguarcitoSZ": "sp_kiosk_jaguarcito",
        "oficinas de deportes": "sp_sports_office", "sportsOfficesSZ": "sp_sports_office",
        "bodega de deportes": "sp_sports_warehouse", "sportsWarehouseSZ": "sp_sports_warehouse",
    }
    for alias, nid in aliases.items():
        subgraph.registerRoomAlias(alias, nid)

    return subgraph


jaguarCenterSubgraph = buildJaguarCenterSubgraph()
sportsZoneSubgraph = buildSportsZoneSubgraph()
