"""
buildingF.py
================================================================================
BUILDING F (FCAE, FMDCC & POSGRADOS) SUBGRAPH / CHILD GRAPH
================================================================================
Single-floor indoor child graph built from official UAM field GPS measurements
(coordenadas.txt) and room directory (buildings.txt).
Weighted, Directed, Non-Complete Graph G = (V, E, W).
================================================================================
"""

from backend.graph.directedGraph import Node
from backend.data.campusCategories import CampusCategory
from .buildingSubgraph import BuildingSubgraph, makeIndoorDistanceCalculator

_calcDist = makeIndoorDistanceCalculator(2.5)


def buildBuildingFSubgraph() -> BuildingSubgraph:
    subgraph = BuildingSubgraph(
        buildingId="buildingF",
        name="Edificio F (FCAE, FMDCC & Posgrados)",
        code="F",
        floors=[1],
        macroNodeId="buildingF",
        entranceNodeIds=["f_ramp_teachers_map", "f_ramp_fcae", "f_ramp_to_i"],
        description="Edificio F: Facultad de Ciencias Administrativas y Económicas (FCAE), Marketing y Diseño (FMDCC), Posgrados y Salón de Profesores."
    )

    subgraph.addNode(Node(
        nodeId="f_ramp_teachers_map",
        name="Rampa al Salón de Profesores y Mapa UAM (Edificio F)",
        category=CampusCategory.ACCESSIBLE_RAMP,
        xPercent=49.5, yPercent=65.5,
        latitude=12.108908, longitude=-86.257390,
        floorLevel=1, isOutdoorAccessPoint=True,
        portalKind="ramp", buildingId="buildingF"
    ))
    subgraph.addNode(Node(
        nodeId="f_fcae_fmdcc",
        name="Facultad de Ciencias Administrativas (FCAE) y Marketing, Diseño y Comunicación (FMDCC)",
        category=CampusCategory.FACULTY,
        xPercent=50.3, yPercent=66.4,
        latitude=12.108938, longitude=-86.257431,
        floorLevel=1, isOutdoorAccessPoint=False,
        buildingId="buildingF"
    ))
    subgraph.addNode(Node(
        nodeId="f_posgrados",
        name="Dirección de Posgrados y Educación Continua",
        category=CampusCategory.ADMINISTRATIVE,
        xPercent=50.0, yPercent=66.8,
        latitude=12.108939, longitude=-86.257347,
        floorLevel=1, isOutdoorAccessPoint=False,
        buildingId="buildingF"
    ))
    subgraph.addNode(Node(
        nodeId="f_ramp_to_i",
        name="Rampa y Escaleras hacia Edificio I",
        category=CampusCategory.ACCESSIBLE_RAMP,
        xPercent=51.5, yPercent=67.0,
        latitude=12.108939, longitude=-86.257347,
        floorLevel=1, isOutdoorAccessPoint=True,
        portalKind="ramp", buildingId="buildingF"
    ))
    subgraph.addNode(Node(
        nodeId="f_fcae_south_hall",
        name="Pasillo Sur FCAE / FMDCC",
        category=CampusCategory.FACULTY,
        xPercent=51.0, yPercent=69.5,
        latitude=12.109078, longitude=-86.257563,
        floorLevel=1, isOutdoorAccessPoint=False,
        buildingId="buildingF"
    ))
    subgraph.addNode(Node(
        nodeId="f_ramp_fcae",
        name="Rampa Accesible FCAE",
        category=CampusCategory.ACCESSIBLE_RAMP,
        xPercent=52.5, yPercent=69.5,
        latitude=12.109053, longitude=-86.257713,
        floorLevel=1, isOutdoorAccessPoint=True,
        portalKind="ramp", buildingId="buildingF"
    ))
    subgraph.addNode(Node(
        nodeId="f_vida_estudiantil_link",
        name="Paso hacia Dirección de Vida Estudiantil",
        category=CampusCategory.ADMINISTRATIVE,
        xPercent=49.0, yPercent=69.5,
        latitude=12.109070, longitude=-86.257354,
        floorLevel=1, isOutdoorAccessPoint=True,
        portalKind="corridor", buildingId="buildingF"
    ))

    edges = [
        ("f_ramp_teachers_map", "f_fcae_fmdcc"),
        ("f_ramp_teachers_map", "f_posgrados"),
        ("f_fcae_fmdcc", "f_posgrados"),
        ("f_posgrados", "f_ramp_to_i"),
        ("f_fcae_fmdcc", "f_fcae_south_hall"),
        ("f_fcae_south_hall", "f_ramp_fcae"),
        ("f_fcae_south_hall", "f_vida_estudiantil_link"),
    ]
    for u, v in edges:
        nU, nV = subgraph.getNode(u), subgraph.getNode(v)
        subgraph.addBidirectionalCorridor(u, v, _calcDist(nU.latitude, nU.longitude, nV.latitude, nV.longitude), isAccessible=True)

    aliases = {
        "facultyBusinessF": "f_fcae_fmdcc", "fcae": "f_fcae_fmdcc", "administracion": "f_fcae_fmdcc", "economia": "f_fcae_fmdcc",
        "facultyMarketingF": "f_fcae_fmdcc", "fmdcc": "f_fcae_fmdcc", "marketing": "f_fcae_fmdcc", "diseno": "f_fcae_fmdcc",
        "postgraduateDirectorateF": "f_posgrados", "posgrados": "f_posgrados", "educacion continua": "f_posgrados",
        "salon de profesores": "f_ramp_teachers_map", "rampa fcae": "f_ramp_fcae",
    }
    for alias, nid in aliases.items():
        subgraph.registerRoomAlias(alias, nid)

    return subgraph


buildingFSubgraph = buildBuildingFSubgraph()
