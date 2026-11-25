"""
buildingN.py
================================================================================
BUILDING N (CLÍNICAS ODONTOLÓGICAS & FODO) SUBGRAPH — GATEWAY PATTERN
================================================================================
Follows official Rule 1 (GRAPH_MAPPING_RULES.md — Gateway Pattern):
All 26 Floor 1 clinical, surgical, sterilization, radiology & administrative
suites and all 8 Floor 2 FODO labs listed in buildings.txt route strictly to
Public Reception / Control Points (`n_reception` on Floor 1 and
`n_fodo_f2_reception` on Floor 2) with an automatic biosecurity accessNotice,
while modeling public exterior connectors (restrooms by Chilamates, access from
Building D, and stairs/walkways toward Building P from coordenadas.txt).
Weighted, Directed, Non-Complete Graph G = (V, E, W).
================================================================================
"""

from backend.graph.directedGraph import Node
from backend.data.campusCategories import CampusCategory
from .buildingSubgraph import BuildingSubgraph, makeIndoorDistanceCalculator

_calcDist = makeIndoorDistanceCalculator(3.0)


def buildBuildingNSubgraph() -> BuildingSubgraph:
    bioNotice = (
        "Recepción de Clínicas Odontológicas (Edificio N). El ingreso a cubículos clínicos, "
        "quirófanos, esterilización y radiología requiere uniforme estéril y autorización docente."
    )
    subgraph = BuildingSubgraph(
        buildingId="buildingN",
        name="Edificio N (Clínicas Odontológicas & FODO)",
        code="N",
        floors=[1, 2],
        macroNodeId="buildingN",
        entranceNodeIds=["n_reception", "n_restrooms_men", "n_access_from_d"],
        description="Edificio N: Recepción de Clínicas Odontológicas (Quirófanos 1-2, Clínicas A/B/E y Post-Grado C-D, Radiología 1-3, Tomografía, Esterilización, Lab Fabricación Digital, Oficina IDEA), Sanitarios H/M y Facultad de Odontología (FODO Piso 2)."
    )

    # =========================================================================
    # FLOOR 1 (Public Gateway Points) — Ordered per buildings.txt & coordenadas.txt
    # =========================================================================
    subgraph.addNode(Node(
        nodeId="n_reception",
        name="Recepción de Clínicas Odontológicas y Archivo - Caja (Edificio N)",
        category=CampusCategory.DENTAL_LAB,
        xPercent=36.0, yPercent=33.5,
        latitude=12.107871, longitude=-86.256967,
        floorLevel=1, isOutdoorAccessPoint=True,
        accessLevel="restricted",
        accessNotice=bioNotice,
        portalKind="door", buildingId="buildingN"
    ))
    subgraph.addNode(Node(
        nodeId="n_restrooms_men",
        name="Servicios Sanitarios Hombres (Edificio N - junto a Plaza Chilamates)",
        category=CampusCategory.RESTROOM,
        xPercent=30.4, yPercent=30.5,
        latitude=12.107741, longitude=-86.256842,
        floorLevel=1, isOutdoorAccessPoint=True,
        portalKind="door", buildingId="buildingN"
    ))
    subgraph.addNode(Node(
        nodeId="n_restrooms_women",
        name="Servicios Sanitarios Mujeres (Edificio N - junto a Plaza Chilamates)",
        category=CampusCategory.RESTROOM,
        xPercent=30.6, yPercent=30.5,
        latitude=12.107741, longitude=-86.256842,
        floorLevel=1, isOutdoorAccessPoint=False,
        buildingId="buildingN"
    ))
    subgraph.addNode(Node(
        nodeId="n_access_from_d",
        name="Acceso hacia Clínicas Odontológicas (desde Lab Odontología Digital D)",
        category=CampusCategory.DENTAL_LAB,
        xPercent=35.0, yPercent=34.0,
        latitude=12.108000, longitude=-86.256842,
        floorLevel=1, isOutdoorAccessPoint=True,
        portalKind="door", buildingId="buildingN"
    ))
    subgraph.addNode(Node(
        nodeId="n_stairs_to_p",
        name="Acceso Norte Edificio N hacia Parqueo y Edificio P",
        category=CampusCategory.STAIRS,
        xPercent=35.0, yPercent=26.2,
        latitude=12.107742, longitude=-86.257105,
        floorLevel=1, isOutdoorAccessPoint=True,
        portalKind="stairs", buildingId="buildingN"
    ))
    subgraph.addNode(Node(
        nodeId="n_stairs_f1",
        name="Escaleras hacia Facultad de Odontología (FODO - Piso 1)",
        category=CampusCategory.STAIRS,
        xPercent=36.2, yPercent=32.0,
        latitude=12.107871, longitude=-86.256967,
        floorLevel=1, isOutdoorAccessPoint=False,
        portalKind="stairs", buildingId="buildingN"
    ))

    # =========================================================================
    # FLOOR 2 (FODO Gateway)
    # =========================================================================
    subgraph.addNode(Node(
        nodeId="n_fodo_f2_reception",
        name="Facultad de Odontología (FODO) — Recepción Piso 2",
        category=CampusCategory.FACULTY,
        xPercent=36.5, yPercent=31.0,
        latitude=12.107871, longitude=-86.256967,
        floorLevel=2, isOutdoorAccessPoint=False,
        accessLevel="restricted",
        accessNotice=bioNotice,
        buildingId="buildingN"
    ))
    subgraph.addNode(Node(
        nodeId="n_stairs_f2",
        name="Escaleras Edificio N (Piso 2)",
        category=CampusCategory.STAIRS,
        xPercent=36.2, yPercent=32.0,
        latitude=12.107871, longitude=-86.256967,
        floorLevel=2, isOutdoorAccessPoint=False,
        portalKind="stairs", buildingId="buildingN"
    ))

    edges = [
        ("n_access_from_d", "n_reception"),
        ("n_reception", "n_restrooms_men"),
        ("n_restrooms_men", "n_restrooms_women"),
        ("n_restrooms_men", "n_stairs_to_p"),
        ("n_reception", "n_stairs_f1"),
    ]
    for u, v in edges:
        nU, nV = subgraph.getNode(u), subgraph.getNode(v)
        subgraph.addBidirectionalCorridor(u, v, _calcDist(nU.latitude, nU.longitude, nV.latitude, nV.longitude), isAccessible=True)

    subgraph.addVerticalConnection("n_stairs_f1", "n_stairs_f2", distanceMeters=11.0, isAccessible=False)
    subgraph.addBidirectionalCorridor("n_stairs_f2", "n_fodo_f2_reception", 5.0, isAccessible=True)

    # Gateway Pattern Aliases: EVERY Building N room from buildings.txt routes cleanly to Reception
    aliases = {
        # Floor 1 Gateway (26 items in buildings.txt)
        "quirofano": "n_reception", "quirofano 1": "n_reception", "quirofano 2": "n_reception",
        "recepcion": "n_reception", "recepcion n": "n_reception", "dentistryReceptionN": "n_reception",
        "clinicas odontologicas": "n_reception", "clinica odontologica": "n_reception",
        "archivo caja": "n_reception", "archivo - caja": "n_reception", "archivo": "n_reception",
        "clinica medica a": "n_reception", "clinica medica b": "n_reception", "clinica medica e": "n_reception",
        "oficina archivo y expedientes": "n_reception", "archivo y expedientes": "n_reception",
        "coordinacion de clinicas": "n_reception",
        "radiologia": "n_reception", "radiologia 1": "n_reception", "radiologia 2": "n_reception", "radiologia 3": "n_reception",
        "proveeduria": "n_reception",
        "interpretacion radiografica": "n_reception",
        "tomografia": "n_reception",
        "lavado de instrumentos": "n_reception",
        "preparacion y empaque": "n_reception",
        "esterilizacion": "n_reception",
        "clinicas post grado": "n_reception", "clinicas post grado c-d": "n_reception", "clinicas post grado cd": "n_reception",
        "fabricacion digital": "n_reception", "laboratorio de fabricacion digital": "n_reception",
        "bodega archivo": "n_reception", "bodega archivo anexo sur": "n_reception",
        "oficina idea": "n_reception", "idea": "n_reception",
        "oficina de supervision clinicas odontologicas": "n_reception", "supervision clinicas odontologicas": "n_reception",
        "baños n": "n_restrooms_men", "banos n": "n_restrooms_men", "banos chilamate": "n_restrooms_men",
        "n_restrooms_chilamate": "n_restrooms_men", "restroomsMenN1": "n_restrooms_men",
        "restroomsWomenN1": "n_restrooms_women",
        # Floor 2 FODO Gateway (8 items in buildings.txt)
        "fodo": "n_fodo_f2_reception", "facultyDentistryN": "n_fodo_f2_reception",
        "facultad de odontologia": "n_fodo_f2_reception",
        "tecnicos odontologicos": "n_fodo_f2_reception",
        "lab simuladores": "n_fodo_f2_reception", "lab simuladores odontologia": "n_fodo_f2_reception",
        "lab de grado": "n_fodo_f2_reception",
        "proveeduria fodo": "n_fodo_f2_reception",
        "lab post-grado": "n_fodo_f2_reception", "lab post grado": "n_fodo_f2_reception",
        "radiologia no1 - no 2": "n_fodo_f2_reception", "radiologia no1": "n_fodo_f2_reception", "radiologia no2": "n_fodo_f2_reception",
        "revelado digital": "n_fodo_f2_reception",
    }
    for alias, nid in aliases.items():
        subgraph.registerRoomAlias(alias, nid)

    return subgraph


buildingNSubgraph = buildBuildingNSubgraph()
