"""
buildingK.py
================================================================================
BUILDING K (CAFETERÍA CENTRAL, JAGUAR SHOP & TERRAZAS) SUBGRAPH / CHILD GRAPH
================================================================================
Multi-floor indoor child graph (Floors 1 & 2) built strictly from official UAM
room directory (buildings.txt) and field GPS measurements (coordenadas.txt).
Weighted, Directed, Non-Complete Graph G = (V, E, W).
================================================================================
"""

from backend.graph.directedGraph import Node
from backend.data.campusCategories import CampusCategory
from .buildingSubgraph import BuildingSubgraph


def buildBuildingKSubgraph() -> BuildingSubgraph:
    subgraph = BuildingSubgraph(
        buildingId="buildingK",
        name="Edificio K (Cafetería Central, Jaguar Shop & Terrazas)",
        code="K",
        floors=[1, 2],
        macroNodeId="buildingK",
        entranceNodeIds=["k_entrance_banpro", "k_food_court"],
        description="Edificio K: Baños Hombres/Mujeres, Área de Mesas, Terrazas, Jaguar Shop, Módulos Comerciales (Food Court), Kiosko 1 (P1), Kioskos 1 y 2 y Área de Mesas (P2)."
    )

    # =========================================================================
    # FLOOR 1 (PRIMER PISO) — Exact order from buildings.txt
    # =========================================================================
    subgraph.addNode(Node(
        nodeId="k_restrooms_men_f1",
        name="Baños Hombres (Edificio K)",
        category=CampusCategory.RESTROOM,
        xPercent=30.4, yPercent=64.5,
        latitude=12.108815, longitude=-86.256730,
        floorLevel=1, isOutdoorAccessPoint=False,
        buildingId="buildingK"
    ))
    subgraph.addNode(Node(
        nodeId="k_restrooms_women_f1",
        name="Baños Mujeres (Edificio K)",
        category=CampusCategory.RESTROOM,
        xPercent=30.6, yPercent=64.5,
        latitude=12.108815, longitude=-86.256730,
        floorLevel=1, isOutdoorAccessPoint=False,
        buildingId="buildingK"
    ))
    subgraph.addNode(Node(
        nodeId="k_tables_f1",
        name="Área de Mesas (Edificio K - Piso 1)",
        category=CampusCategory.FOOD_AREA,
        xPercent=32.2, yPercent=63.8,
        latitude=12.108805, longitude=-86.256785,
        floorLevel=1, isOutdoorAccessPoint=False,
        buildingId="buildingK"
    ))
    subgraph.addNode(Node(
        nodeId="k_terraces_tables",
        name="Terrazas (Edificio K)",
        category=CampusCategory.FOOD_AREA,
        xPercent=32.5, yPercent=64.0,
        latitude=12.108805, longitude=-86.256785,
        floorLevel=1, isOutdoorAccessPoint=False,
        buildingId="buildingK"
    ))
    subgraph.addNode(Node(
        nodeId="k_jaguar_shop",
        name="Jaguar Shop (Edificio K)",
        category=CampusCategory.ADMINISTRATIVE,
        xPercent=31.0, yPercent=61.5,
        latitude=12.108750, longitude=-86.256735,
        floorLevel=1, isOutdoorAccessPoint=False,
        buildingId="buildingK"
    ))
    subgraph.addNode(Node(
        nodeId="k_food_court",
        name="Módulos Comerciales (Food Court)",
        category=CampusCategory.FOOD_AREA,
        xPercent=31.8, yPercent=63.0,
        latitude=12.108775, longitude=-86.256755,
        floorLevel=1, isOutdoorAccessPoint=True,
        portalKind="door", buildingId="buildingK"
    ))
    subgraph.addNode(Node(
        nodeId="k_kiosk1_f1",
        name="Kiosko 1 (Edificio K - Piso 1)",
        category=CampusCategory.FOOD_AREA,
        xPercent=32.0, yPercent=63.1,
        latitude=12.108775, longitude=-86.256755,
        floorLevel=1, isOutdoorAccessPoint=False,
        buildingId="buildingK"
    ))
    # Supplementary access & vertical circulation
    subgraph.addNode(Node(
        nodeId="k_entrance_banpro",
        name="Acceso Edificio K (junto a Banpro)",
        category=CampusCategory.FOOD_AREA,
        xPercent=25.2, yPercent=61.0,
        latitude=12.108585, longitude=-86.256576,
        floorLevel=1, isOutdoorAccessPoint=True,
        portalKind="door", buildingId="buildingK"
    ))
    subgraph.addNode(Node(
        nodeId="k_stairs_f1",
        name="Escaleras hacia Piso 2 (Edificio K - Piso 1)",
        category=CampusCategory.STAIRS,
        xPercent=31.5, yPercent=62.5,
        latitude=12.108775, longitude=-86.256755,
        floorLevel=1, isOutdoorAccessPoint=False,
        portalKind="stairs", buildingId="buildingK"
    ))

    # =========================================================================
    # FLOOR 2 (SEGUNDO PISO) — Exact order from buildings.txt
    # =========================================================================
    subgraph.addNode(Node(
        nodeId="k_kiosk1_f2",
        name="Kiosko 1 (Edificio K - Piso 2)",
        category=CampusCategory.FOOD_AREA,
        xPercent=31.6, yPercent=62.5,
        latitude=12.108775, longitude=-86.256755,
        floorLevel=2, isOutdoorAccessPoint=False,
        buildingId="buildingK"
    ))
    subgraph.addNode(Node(
        nodeId="k_kiosk2_f2",
        name="Kiosko 2 (Edificio K - Piso 2)",
        category=CampusCategory.FOOD_AREA,
        xPercent=32.0, yPercent=62.5,
        latitude=12.108775, longitude=-86.256755,
        floorLevel=2, isOutdoorAccessPoint=False,
        buildingId="buildingK"
    ))
    subgraph.addNode(Node(
        nodeId="k_tables_f2",
        name="Área de Mesas (Edificio K - Piso 2)",
        category=CampusCategory.FOOD_AREA,
        xPercent=32.5, yPercent=63.5,
        latitude=12.108800, longitude=-86.256780,
        floorLevel=2, isOutdoorAccessPoint=False,
        buildingId="buildingK"
    ))
    subgraph.addNode(Node(
        nodeId="k_stairs_f2",
        name="Escaleras Edificio K (Piso 2)",
        category=CampusCategory.STAIRS,
        xPercent=31.5, yPercent=62.5,
        latitude=12.108775, longitude=-86.256755,
        floorLevel=2, isOutdoorAccessPoint=False,
        portalKind="stairs", buildingId="buildingK"
    ))

    subgraph.addBidirectionalCorridor("k_entrance_banpro", "k_jaguar_shop", 14.0, isAccessible=True)
    subgraph.addBidirectionalCorridor("k_jaguar_shop", "k_food_court", 7.0, isAccessible=True)
    subgraph.addBidirectionalCorridor("k_food_court", "k_kiosk1_f1", 3.0, isAccessible=True)
    subgraph.addBidirectionalCorridor("k_food_court", "k_tables_f1", 5.0, isAccessible=True)
    subgraph.addBidirectionalCorridor("k_tables_f1", "k_terraces_tables", 3.0, isAccessible=True)
    subgraph.addBidirectionalCorridor("k_food_court", "k_restrooms_men_f1", 8.0, isAccessible=True)
    subgraph.addBidirectionalCorridor("k_restrooms_men_f1", "k_restrooms_women_f1", 2.0, isAccessible=True)
    subgraph.addBidirectionalCorridor("k_food_court", "k_stairs_f1", 5.0, isAccessible=True)
    subgraph.addVerticalConnection("k_stairs_f1", "k_stairs_f2", distanceMeters=10.0, isAccessible=False)
    subgraph.addBidirectionalCorridor("k_stairs_f2", "k_kiosk1_f2", 4.0, isAccessible=True)
    subgraph.addBidirectionalCorridor("k_kiosk1_f2", "k_kiosk2_f2", 4.0, isAccessible=True)
    subgraph.addBidirectionalCorridor("k_kiosk2_f2", "k_tables_f2", 6.0, isAccessible=True)

    aliases = {
        "banpro": "k_entrance_banpro", "banco": "k_entrance_banpro",
        "cafeteria": "k_food_court", "food court": "k_food_court", "comedor": "k_food_court",
        "centralCafeteriaK": "k_food_court", "modulos comerciales": "k_food_court",
        "kiosko 1": "k_kiosk1_f1", "kiosk1K1": "k_kiosk1_f1",
        "jaguar shop": "k_jaguar_shop", "jaguarShopK": "k_jaguar_shop",
        "terrazas": "k_terraces_tables", "foodKiosksK": "k_terraces_tables",
        "area de mesas k": "k_tables_f1", "tablesAreaK1": "k_tables_f1",
        "baños k": "k_restrooms_men_f1", "banos k": "k_restrooms_men_f1",
        "k_restrooms_f1": "k_restrooms_men_f1", "restroomsMenK1": "k_restrooms_men_f1",
        "restroomsWomenK1": "k_restrooms_women_f1",
        "kiosko 1 piso 2": "k_kiosk1_f2", "kiosk1K2": "k_kiosk1_f2",
        "kiosko 2": "k_kiosk2_f2", "k_kiosks_f2": "k_kiosk2_f2", "kiosk2K2": "k_kiosk2_f2",
        "terraza superior": "k_tables_f2", "tablesAreaK2": "k_tables_f2",
    }
    for alias, nid in aliases.items():
        subgraph.registerRoomAlias(alias, nid)

    return subgraph


buildingKSubgraph = buildBuildingKSubgraph()
