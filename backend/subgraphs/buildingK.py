"""
buildingK.py
================================================================================
BUILDING K (CAFETERÍA CENTRAL, JAGUAR SHOP & TERRAZAS) SUBGRAPH / CHILD GRAPH
================================================================================
Multi-floor indoor child graph (Floors 1 & 2) covering Cafetería Central,
Jaguar Shop, Food Court, Terrazas, Kioskos and Banpro proximity (buildings.txt).
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
        description="Edificio K: Comedor Estudiantil Central, Food Court, Jaguar Shop, Terrazas, Banpro y Kioskos del 2.º piso."
    )

    # Floor 1
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
        nodeId="k_food_court",
        name="Módulos Comerciales (Food Court) y Kiosko 1 (Edificio K)",
        category=CampusCategory.FOOD_AREA,
        xPercent=31.8, yPercent=63.0,
        latitude=12.108775, longitude=-86.256755,
        floorLevel=1, isOutdoorAccessPoint=True,
        portalKind="door", buildingId="buildingK"
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
        nodeId="k_terraces_tables",
        name="Área de Mesas y Terrazas (Edificio K - Piso 1)",
        category=CampusCategory.FOOD_AREA,
        xPercent=32.5, yPercent=64.0,
        latitude=12.108805, longitude=-86.256785,
        floorLevel=1, isOutdoorAccessPoint=False,
        buildingId="buildingK"
    ))
    subgraph.addNode(Node(
        nodeId="k_restrooms_f1",
        name="Servicios Sanitarios (Hombres y Mujeres - Edificio K)",
        category=CampusCategory.RESTROOM,
        xPercent=30.5, yPercent=64.5,
        latitude=12.108815, longitude=-86.256730,
        floorLevel=1, isOutdoorAccessPoint=False,
        buildingId="buildingK"
    ))
    subgraph.addNode(Node(
        nodeId="k_stairs_f1",
        name="Escaleras hacia Terrazas y Kioskos (Piso 1)",
        category=CampusCategory.STAIRS,
        xPercent=31.5, yPercent=62.5,
        latitude=12.108775, longitude=-86.256755,
        floorLevel=1, isOutdoorAccessPoint=False,
        portalKind="stairs", buildingId="buildingK"
    ))

    # Floor 2
    subgraph.addNode(Node(
        nodeId="k_stairs_f2",
        name="Escaleras Edificio K (Piso 2)",
        category=CampusCategory.STAIRS,
        xPercent=31.5, yPercent=62.5,
        latitude=12.108775, longitude=-86.256755,
        floorLevel=2, isOutdoorAccessPoint=False,
        portalKind="stairs", buildingId="buildingK"
    ))
    subgraph.addNode(Node(
        nodeId="k_kiosks_f2",
        name="Kiosko 1 y Kiosko 2 (Piso 2 - Edificio K)",
        category=CampusCategory.FOOD_AREA,
        xPercent=31.8, yPercent=62.5,
        latitude=12.108775, longitude=-86.256755,
        floorLevel=2, isOutdoorAccessPoint=False,
        buildingId="buildingK"
    ))
    subgraph.addNode(Node(
        nodeId="k_tables_f2",
        name="Área de Mesas y Terraza Superior (Piso 2)",
        category=CampusCategory.FOOD_AREA,
        xPercent=32.5, yPercent=63.5,
        latitude=12.108800, longitude=-86.256780,
        floorLevel=2, isOutdoorAccessPoint=False,
        buildingId="buildingK"
    ))

    subgraph.addBidirectionalCorridor("k_entrance_banpro", "k_jaguar_shop", 14.0, isAccessible=True)
    subgraph.addBidirectionalCorridor("k_jaguar_shop", "k_food_court", 7.0, isAccessible=True)
    subgraph.addBidirectionalCorridor("k_food_court", "k_terraces_tables", 6.0, isAccessible=True)
    subgraph.addBidirectionalCorridor("k_food_court", "k_restrooms_f1", 8.0, isAccessible=True)
    subgraph.addBidirectionalCorridor("k_food_court", "k_stairs_f1", 5.0, isAccessible=True)
    subgraph.addVerticalConnection("k_stairs_f1", "k_stairs_f2", distanceMeters=10.0, isAccessible=False)
    subgraph.addBidirectionalCorridor("k_stairs_f2", "k_kiosks_f2", 5.0, isAccessible=True)
    subgraph.addBidirectionalCorridor("k_kiosks_f2", "k_tables_f2", 6.0, isAccessible=True)

    aliases = {
        "banpro": "k_entrance_banpro", "banco": "k_entrance_banpro",
        "cafeteria": "k_food_court", "food court": "k_food_court", "comedor": "k_food_court",
        "jaguar shop": "k_jaguar_shop", "terrazas": "k_terraces_tables", "baños k": "k_restrooms_f1",
        "kiosko 2": "k_kiosks_f2", "terraza superior": "k_tables_f2",
    }
    for alias, nid in aliases.items():
        subgraph.registerRoomAlias(alias, nid)

    return subgraph


buildingKSubgraph = buildBuildingKSubgraph()
