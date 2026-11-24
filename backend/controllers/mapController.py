"""
mapController.py
================================================================================
CAMPUS MAP & PEDESTRIAN ROUTING CONTROLLER
================================================================================
Flask Blueprint providing RESTful API endpoints for the interactive UAM campus
map, Dijkstra shortest-path calculations (with wheelchair accessibility options),
building nodes directory, points of interest (placesCatalog), categories metadata,
and GPS-to-campus-node snapping.
"""

from flask import Blueprint, request, jsonify, session, Response, current_app, send_file
from typing import Dict, Any, List
import unicodedata
from io import BytesIO

from backend.graph.navigationService import globalNavigationService
from backend.graph.geoUtils import CampusGeoUtils
from backend.graph.graphRegistry import getGraphsInventory
from backend.data.campusCategories import CampusCategory, CATEGORY_METADATA
from backend.data.placesCatalog import PLACES_CATALOG
from backend.subgraphs import getBuildingSubgraph, getAllBuildingSubgraphs
from backend.services.azureSpeechService import AzureSpeechService

mapController = Blueprint("mapController", __name__, url_prefix="/api/map")

_azureSpeechService = None


def _getAzureSpeechService() -> AzureSpeechService:
    global _azureSpeechService
    if _azureSpeechService is None:
        _azureSpeechService = AzureSpeechService(
            endpoint=current_app.config["AZURE_SPEECH_ENDPOINT"],
            region=current_app.config["AZURE_SPEECH_REGION"],
            resource_id=current_app.config["AZURE_SPEECH_RESOURCE_ID"],
            managed_identity_client_id=current_app.config.get(
                "AZURE_MANAGED_IDENTITY_CLIENT_ID"
            ),
        )
    return _azureSpeechService


def _getPreferredLanguage() -> str:
    """Detects preferred language from query param, session, or default ('eng')."""
    lang = request.args.get("lang")
    if not lang and request.is_json:
        payload = request.get_json(silent=True) or {}
        lang = payload.get("lang")
    if not lang:
        lang = session.get("lang", "eng")
    return "spa" if str(lang).lower().startswith("sp") else "eng"


@mapController.route("/nodes", methods=["GET"])
def getCampusNodes():
    """
    GET /api/map/nodes
    Returns all macro campus nodes (buildings, gates, parking, courtyards)
    with localized names, coordinates (% and GPS), and connected edges.
    """
    lang = _getPreferredLanguage()
    nodesList = []

    for nodeId, node in globalNavigationService.graph.nodes.items():
        edges = [
            {
                "targetNodeId": edge.targetNodeId,
                "distanceMeters": edge.distanceMeters,
                "isAccessible": edge.isAccessible,
                "stepInstruction": edge.getInstruction(lang),
            }
            for edge in getattr(node, "outgoingEdges", [])
        ]
        nodeDict = node.toDict(lang)
        nodeDict["adjacentEdges"] = edges
        nodesList.append(nodeDict)

    return jsonify({
        "success": True,
        "count": len(nodesList),
        "language": lang,
        "nodes": nodesList,
    }), 200


@mapController.route("/nodes/<nodeId>", methods=["GET"])
def getCampusNodeDetail(nodeId: str):
    """
    GET /api/map/nodes/<nodeId>
    Returns detailed information about a specific node and all sub-places
    (classrooms, laboratories, deaneries, fountains) located inside it.
    """
    lang = _getPreferredLanguage()
    node = globalNavigationService.graph.getNode(nodeId)
    if not node:
        return jsonify({
            "success": False,
            "error": f"Campus node '{nodeId}' not found."
        }), 404

    # Collect internal sub-rooms from catalog
    subPlaces = [
        place for place in PLACES_CATALOG
        if place.get("parentBuildingId", "").lower() == nodeId.lower()
    ]

    edges = [
        {
            "targetNodeId": edge.targetNodeId,
            "distanceMeters": edge.distanceMeters,
            "isAccessible": edge.isAccessible,
            "stepInstruction": edge.getInstruction(lang),
        }
        for edge in getattr(node, "outgoingEdges", [])
    ]

    nodeDict = node.toDict(lang)
    nodeDict["adjacentEdges"] = edges

    return jsonify({
        "success": True,
        "node": nodeDict,
        "subPlacesCount": len(subPlaces),
        "subPlaces": subPlaces,
    }), 200


@mapController.route("/categories", methods=["GET"])
def getCategories():
    """
    GET /api/map/categories
    Returns all campus facility categories with bilingual labels, icon keys,
    and the number of registered places in each category.
    """
    categoriesList = []
    for catKey, meta in CATEGORY_METADATA.items():
        matchingCount = sum(1 for p in PLACES_CATALOG if p.get("category") == catKey)
        categoriesList.append({
            "key": catKey,
            "labelEnglish": meta.get("labelEnglish", catKey),
            "labelSpanish": meta.get("labelSpanish", catKey),
            "icon": meta.get("icon", "pin"),
            "placesCount": matchingCount,
        })

    return jsonify({
        "success": True,
        "count": len(categoriesList),
        "categories": categoriesList,
    }), 200


def _normalizeText(text: str) -> str:
    """Case- and accent-insensitive normalization for bilingual campus search."""
    decomposed = unicodedata.normalize("NFD", str(text or "").strip().lower())
    return "".join(ch for ch in decomposed if unicodedata.category(ch) != "Mn")


@mapController.route("/places", methods=["GET"])
def getPlaces():
    """
    GET /api/map/places
    Searches and filters all registered campus places across PLACES_CATALOG
    and all 18 indoor building subgraphs (buildings.txt + coordenadas.txt).
    Query Params:
      - category: filter by CampusCategory (e.g., 'drinkingFountain', 'medicalLab')
      - q: free-text search across name, keywords, and location notes
      - floor: integer floor filter (e.g. 1, 2)
    """
    categoryFilter = request.args.get("category")
    searchQuery = _normalizeText(request.args.get("q") or "")
    floorFilter = request.args.get("floor")

    combinedPlaces = list(PLACES_CATALOG)
    seenKeys = {
        (_normalizeText(p.get("parentBuildingId", "")), _normalizeText(p.get("name", "")))
        for p in combinedPlaces
    }
    for buildingId, sg in getAllBuildingSubgraphs().items():
        for node in sg.getAllNodes():
            key = (_normalizeText(sg.macroNodeId), _normalizeText(node.name))
            if key in seenKeys:
                continue
            seenKeys.add(key)
            combinedPlaces.append({
                "placeId": node.nodeId,
                "name": node.name,
                "category": node.category,
                "parentBuildingId": sg.macroNodeId,
                "floorLevel": node.floorLevel,
                "isAccessible": node.category != CampusCategory.STAIRS,
                "latitude": node.latitude,
                "longitude": node.longitude,
                "locationNotes": f"{sg.name} — Piso {node.floorLevel}",
                "keywords": [node.nodeId, sg.code, sg.name],
            })

    results = []
    for place in combinedPlaces:
        if categoryFilter and place.get("category") != categoryFilter:
            continue
        if floorFilter is not None:
            try:
                if place.get("floorLevel") != int(floorFilter):
                    continue
            except ValueError:
                pass

        if searchQuery:
            nameMatch = searchQuery in _normalizeText(place.get("name", ""))
            notesMatch = searchQuery in _normalizeText(place.get("locationNotes", ""))
            keywordMatch = any(searchQuery in _normalizeText(kw) for kw in place.get("keywords", []))
            if not (nameMatch or notesMatch or keywordMatch):
                continue

        results.append(place)

    return jsonify({
        "success": True,
        "count": len(results),
        "places": results,
    }), 200


@mapController.route("/route", methods=["POST", "GET"])
def calculateRoute():
    """
    POST/GET /api/map/route
    Calculates the shortest walkable pedestrian path between two points.
    Supports smart resolution for macro nodes (e.g. 'buildingA') or internal
    classrooms/POIs (e.g. 'B103', 'Laboratorio Simuladores', 'Bebedero').
    
    Parameters (JSON or Query Params):
      - origin: origin place ID, node ID, or search keyword
      - destination: target place ID, node ID, or search keyword
      - accessibleOnly: boolean (True forces route through ramps, avoiding stairs)
      - lang: 'eng' | 'spa'
    """
    if request.method == "POST":
        payload = request.get_json(silent=True) or request.form.to_dict() or {}
    else:
        payload = request.args.to_dict()

    origin = payload.get("origin") or payload.get("originQuery") or payload.get("source")
    destination = payload.get("destination") or payload.get("destinationQuery") or payload.get("target")

    if not origin or not destination:
        return jsonify({
            "success": False,
            "error": "Both 'origin' and 'destination' parameters are required."
        }), 400

    accessibleRaw = payload.get("accessibleOnly", False)
    accessibleOnly = str(accessibleRaw).lower() in ("true", "1", "yes")
    lang = payload.get("lang") or _getPreferredLanguage()

    routeResult = globalNavigationService.calculateRoute(
        originQuery=str(origin),
        destinationQuery=str(destination),
        accessibleOnly=accessibleOnly,
        lang=lang,
    )

    statusCode = 200 if routeResult.get("success") else 404
    return jsonify(routeResult), statusCode


@mapController.route("/speech/synthesize", methods=["POST"])
def synthesizeSpeech():
    """Synthesize one text instruction using Azure Neural Speech with Entra ID."""
    payload = request.get_json(silent=True) or {}
    text = str(payload.get("text") or "").strip()
    language = str(payload.get("language") or "").strip()

    if not text:
        return jsonify({"success": False, "error": "Text is required."}), 400

    try:
        audioData = _getAzureSpeechService().synthesize(text, language)
        return send_file(
            BytesIO(audioData),
            mimetype="audio/wav",
            as_attachment=False,
            download_name="jaguarfind-speech.wav",
        )
    except ValueError as error:
        return jsonify({"success": False, "error": str(error)}), 400
    except Exception:
        current_app.logger.exception("Azure Speech synthesis failed")
        return jsonify({
            "success": False,
            "error": "Azure Speech synthesis is unavailable.",
        }), 503


@mapController.route("/perimeter", methods=["GET"])
def getCampusPerimeter():
    """
    GET /api/map/perimeter
    Returns the official UAM campus polygon perimeter coordinates and validation status.
    """
    perimeter = CampusGeoUtils.getCampusPerimeter()
    return jsonify({
        "success": True,
        "count": len(perimeter),
        "perimeter": perimeter,
    }), 200


@mapController.route("/nearest-gps", methods=["GET"])
def findNearestGpsNode():
    """
    GET /api/map/nearest-gps
    Matches a device GPS latitude/longitude coordinate against all field-measured
    campus nodes (18 building subgraphs + pedestrian walkways + macro buildings).
    Query Params:
      - lat: float latitude (e.g. 12.1085)
      - lng: float longitude (e.g. -86.2570)
      - accuracy: optional GPS accuracy in meters
      - floor: optional integer floor hint for multi-story buildings
      - lang: 'eng' | 'spa'
    """
    latRaw = request.args.get("lat")
    lngRaw = request.args.get("lng")

    if not latRaw or not lngRaw:
        return jsonify({
            "success": False,
            "error": "Both 'lat' and 'lng' query parameters are required."
        }), 400

    try:
        userLat = float(latRaw)
        userLng = float(lngRaw)
    except (ValueError, TypeError):
        return jsonify({"success": False, "error": "Invalid floating point lat/lng coordinates."}), 400

    accuracyMeters = None
    accRaw = request.args.get("accuracy")
    if accRaw is not None and accRaw != "":
        try:
            accuracyMeters = float(accRaw)
        except ValueError:
            pass

    floorHint = None
    floorRaw = request.args.get("floor")
    if floorRaw is not None and floorRaw != "":
        try:
            floorHint = int(floorRaw)
        except ValueError:
            pass

    lang = _getPreferredLanguage()
    result = globalNavigationService.findNearestGpsNode(
        userLat,
        userLng,
        lang=lang,
        accuracyMeters=accuracyMeters,
        floorHint=floorHint,
    )

    isInside = result.get("isWithinCampus", True)
    if not isInside:
        return jsonify({
            "success": False,
            "outsideCampus": True,
            "message": "Te encuentras fuera del campus de la UAM." if lang == "spa" else "You are outside the UAM campus.",
            "language": lang,
            "userCoordinates": {"lat": userLat, "lng": userLng},
            "suggestedFallbackNode": "mainParking",
            "nearest": result,
        }), 200

    return jsonify({
        "success": True,
        "outsideCampus": False,
        "language": lang,
        "userCoordinates": {"lat": userLat, "lng": userLng},
        "nearest": result,
    }), 200


@mapController.route("/calibration", methods=["GET"])
def getMapCalibration():
    """
    GET /api/map/calibration
    Returns calibrated affine GPS <-> SVG projection parameters and true compass
    bearing of the official UAM campus map (for live 2.5D compass rotation).
    """
    return jsonify({
        "success": True,
        "calibration": CampusGeoUtils.getCalibrationMetadata(),
    }), 200


@mapController.route("/walkways", methods=["GET"])
def getPedestrianWalkwaysGraph():
    """
    GET /api/map/walkways
    Returns formal graph metrics and nodes of the weighted, directed, non-complete
    pedestrian walkway network synchronized with the frontend map.
    """
    lang = _getPreferredLanguage()
    wg = globalNavigationService.walkwayGraph
    nodesList = [n.toDict(lang) for n in wg.getAllNodes()]
    directedEdgeCount = sum(len(n.outgoingEdges) for n in wg.getAllNodes())
    maxComplete = len(nodesList) * max(0, len(nodesList) - 1)
    density = round(directedEdgeCount / maxComplete, 5) if maxComplete > 0 else 0.0

    return jsonify({
        "success": True,
        "graphType": "Weighted, Directed, Non-Complete Graph G = (V, E, W)",
        "vertexCount": len(nodesList),
        "directedEdgeCount": directedEdgeCount,
        "density": density,
        "calibration": CampusGeoUtils.getCalibrationMetadata(),
        "nodes": nodesList,
    }), 200


@mapController.route("/graphs-summary", methods=["GET"])
def getGraphsSummary():
    """
    GET /api/map/graphs-summary
    Returns the live inventory and formal graph-theory metrics of every
    weighted, directed, non-complete graph powered by `graphCombined.py`.
    """
    return jsonify({
        "success": True,
        **getGraphsInventory(),
    }), 200


# =============================================================================
# INDOOR BUILDING SUBGRAPHS (CHILD GRAPHS) ENDPOINTS
# =============================================================================

@mapController.route("/subgraphs", methods=["GET"])
def getSubgraphsCatalog():
    """
    GET /api/map/subgraphs
    Returns the catalog of all campus buildings with detailed indoor child graphs.
    """
    lang = _getPreferredLanguage()
    subgraphs = getAllBuildingSubgraphs()
    catalog = []
    for bId, sg in subgraphs.items():
        metrics = sg.graph.getGraphSummary()
        catalog.append({
            "buildingId": sg.buildingId,
            "name": sg.name,
            "code": sg.code,
            "floors": sg.floors,
            "macroNodeId": sg.macroNodeId,
            "entranceNodeIds": sg.entranceNodeIds,
            "description": sg.description,
            "totalNodes": len(sg.getAllNodes()),
            "totalDirectedEdges": metrics["directedEdgeCount"],
            "density": metrics["density"],
            "isComplete": metrics["isComplete"],
        })
    return jsonify({
        "success": True,
        "count": len(catalog),
        "buildings": catalog,
    }), 200


@mapController.route("/buildings/<buildingId>/subgraph", methods=["GET"])
def getBuildingSubgraphDetail(buildingId: str):
    """
    GET /api/map/buildings/<buildingId>/subgraph
    Returns the full indoor child graph (nodes, edges, floors) for the specified building.
    Query Params:
      - floor: optional integer filter for a specific floor (e.g. 1, 2, 3)
      - lang: 'eng' | 'spa'
    """
    lang = _getPreferredLanguage()
    sg = getBuildingSubgraph(buildingId)
    if not sg:
        return jsonify({
            "success": False,
            "error": f"Child graph for building '{buildingId}' not found."
        }), 404

    floorParam = request.args.get("floor")
    data = sg.toDict(lang=lang)

    if floorParam is not None:
        try:
            targetFloor = int(floorParam)
            data["filteredFloor"] = targetFloor
            data["nodes"] = [n for n in data["nodes"] if n.get("floorLevel") == targetFloor]
            data["nodesCount"] = len(data["nodes"])
        except ValueError:
            pass

    return jsonify({
        "success": True,
        "subgraph": data,
    }), 200


@mapController.route("/buildings/<buildingId>/route", methods=["GET", "POST"])
def calculateIndoorRoute(buildingId: str):
    """
    GET/POST /api/map/buildings/<buildingId>/route
    Calculates turn-by-turn indoor routing between two rooms/nodes inside the building.
    Parameters (JSON or Query Params):
      - origin: starting room code or node ID (e.g. 'P101', 'p_room_101')
      - destination: target room code or node ID (e.g. 'P208', 'p_restrooms_f3')
      - accessibleOnly: boolean (True enforces ramps/elevators, avoiding stairs)
      - lang: 'eng' | 'spa'
    """
    if request.method == "POST":
        payload = request.get_json(silent=True) or request.form.to_dict() or {}
    else:
        payload = request.args.to_dict()

    origin = payload.get("origin") or payload.get("source")
    destination = payload.get("destination") or payload.get("target")

    if not origin or not destination:
        return jsonify({
            "success": False,
            "error": "Both 'origin' and 'destination' parameters are required."
        }), 400

    accessibleRaw = payload.get("accessibleOnly", False)
    accessibleOnly = str(accessibleRaw).lower() in ("true", "1", "yes")
    lang = payload.get("lang") or _getPreferredLanguage()

    sg = getBuildingSubgraph(buildingId)
    if not sg:
        return jsonify({
            "success": False,
            "error": f"Child graph for building '{buildingId}' not found."
        }), 404

    result = sg.calculateIndoorRoute(
        originQuery=str(origin),
        destinationQuery=str(destination),
        accessibleOnly=accessibleOnly,
        lang=lang,
    )

    statusCode = 200 if result.get("success") else 404
    return jsonify(result), statusCode
