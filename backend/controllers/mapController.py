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
from backend.graph.buildingBoundaries import getAllBuildingBoundaries, BEACON_REGISTRY
from backend.graph.graphRegistry import getGraphsInventory
from backend.data.campusCategories import CampusCategory, CATEGORY_METADATA
from backend.data.placesCatalog import PLACES_CATALOG
from backend.subgraphs import getBuildingSubgraph, getAllBuildingSubgraphs
from backend.services.azureSpeechService import AzureSpeechService
from backend.services.placeSearchService import buildIndexedPlaces, searchPlaces
from backend.i18n import get_current_language, normalize_language, t

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
    """Detects preferred language from query param, JSON payload, session, or default."""
    lang = request.args.get("lang")
    if not lang and request.is_json:
        payload = request.get_json(silent=True) or {}
        lang = payload.get("lang")
    if not lang:
        return get_current_language()
    return normalize_language(lang)


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
            "error": t("api.map_node_not_found", lang=lang, nodeId=nodeId)
        }), 404

    # Collect all indexed internal sub-rooms (catalog + building subgraph)
    indexedPlaces = buildIndexedPlaces(lang=lang)
    subPlaces = [
        place for place in indexedPlaces
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
    lang = _getPreferredLanguage()
    indexedPlaces = buildIndexedPlaces(lang=lang)
    categoriesList = []
    for catKey, meta in CATEGORY_METADATA.items():
        matchingCount = sum(1 for p in indexedPlaces if p.get("category") == catKey)
        categoriesList.append({
            "key": catKey,
            "label": t(f"map.category_labels.{catKey}", lang=lang),
            "labelEnglish": t(f"map.category_labels.{catKey}", lang="eng"),
            "labelSpanish": t(f"map.category_labels.{catKey}", lang="spa"),
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
      - q: free-text search across name, room codes, keywords, and location notes
      - floor: integer floor filter (e.g. 1, 2)
    """
    lang = _getPreferredLanguage()
    categoryFilter = request.args.get("category")
    rawQuery = request.args.get("q") or ""
    floorFilter = request.args.get("floor")

    combinedPlaces = buildIndexedPlaces(lang=lang)
    results = searchPlaces(
        combinedPlaces,
        query=rawQuery,
        category=categoryFilter,
        floor=floorFilter,
    )

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
    lang = normalize_language(payload.get("lang")) if payload.get("lang") else _getPreferredLanguage()

    if not origin or not destination:
        return jsonify({
            "success": False,
            "error": t("api.map_origin_dest_required", lang=lang)
        }), 400

    accessibleRaw = payload.get("accessibleOnly", False)
    accessibleOnly = str(accessibleRaw).lower() in ("true", "1", "yes")

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
    activeLang = normalize_language(language) if language else _getPreferredLanguage()

    if not text:
        return jsonify({"success": False, "error": t("api.speech_text_required", lang=activeLang)}), 400
    if len(text) > 2000:
        return jsonify({"success": False, "error": t("api.speech_text_too_long", lang=activeLang)}), 400

    try:
        audioData = _getAzureSpeechService().synthesize(text, language or ("es-MX" if activeLang == "spa" else "en-US"))
        return send_file(
            BytesIO(audioData),
            mimetype="audio/wav",
            as_attachment=False,
            download_name="jaguarfind-speech.wav",
        )
    except ValueError as error:
        errKey = str(error)
        return jsonify({"success": False, "error": t(errKey, lang=activeLang, default=errKey)}), 400
    except Exception:
        current_app.logger.exception("Azure Speech synthesis failed")
        return jsonify({
            "success": False,
            "error": t("api.speech_unavailable", lang=activeLang),
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
    Matches a device GPS latitude/longitude coordinate against defined campus
    building boundaries (polygons & radius checks), multi-floor inference
    (altitude / beacon / prompt), and all campus graph nodes.
    Query Params:
      - lat: float latitude (e.g. 12.1085)
      - lng: float longitude (e.g. -86.2570)
      - accuracy: optional GPS horizontal accuracy in meters
      - altitude: optional GPS/barometric altitude in meters above sea level
      - altitudeAccuracy: optional vertical accuracy in meters
      - floor: optional integer floor hint for multi-story buildings
      - beacon / beaconId: optional indoor beacon identifier (e.g. UAM-P-F2)
      - beaconFloor: optional integer floor from indoor beacon
      - lang: 'eng' | 'spa'
    """
    latRaw = request.args.get("lat")
    lngRaw = request.args.get("lng")
    lang = _getPreferredLanguage()

    if not latRaw or not lngRaw:
        return jsonify({
            "success": False,
            "error": t("api.map_lat_lng_required", lang=lang)
        }), 400

    try:
        userLat = float(latRaw)
        userLng = float(lngRaw)
    except (ValueError, TypeError):
        return jsonify({"success": False, "error": t("api.map_invalid_coords", lang=lang)}), 400

    def _parseOptionalFloat(paramName: str):
        raw = request.args.get(paramName)
        if raw is None or raw == "":
            return None
        try:
            val = float(raw)
            if val != val:  # NaN guard
                return None
            return val
        except (ValueError, TypeError):
            return None

    def _parseOptionalInt(paramName: str):
        raw = request.args.get(paramName)
        if raw is None or raw == "":
            return None
        try:
            return int(raw)
        except (ValueError, TypeError):
            return None

    accuracyMeters = _parseOptionalFloat("accuracy")
    altitudeMeters = _parseOptionalFloat("altitude")
    altitudeAccuracyMeters = _parseOptionalFloat("altitudeAccuracy")
    floorHint = _parseOptionalInt("floor")
    beaconId = (request.args.get("beacon") or request.args.get("beaconId") or "").strip() or None
    beaconFloor = _parseOptionalInt("beaconFloor")

    lang = _getPreferredLanguage()
    result = globalNavigationService.findNearestGpsNode(
        userLat,
        userLng,
        lang=lang,
        accuracyMeters=accuracyMeters,
        floorHint=floorHint,
        altitudeMeters=altitudeMeters,
        altitudeAccuracyMeters=altitudeAccuracyMeters,
        beaconId=beaconId,
        beaconFloor=beaconFloor,
    )

    isInside = result.get("isWithinCampus", True)
    if not isInside:
        return jsonify({
            "success": False,
            "outsideCampus": True,
            "message": t("api.map_outside_campus", lang=lang),
            "language": lang,
            "userCoordinates": {
                "lat": userLat,
                "lng": userLng,
                "accuracy": accuracyMeters,
                "altitude": altitudeMeters,
                "altitudeAccuracy": altitudeAccuracyMeters,
            },
            "suggestedFallbackNode": "mainParking",
            "campusEntrances": globalNavigationService.getCampusEntranceOptions(lang=lang),
            "nearest": result,
        }), 200

    return jsonify({
        "success": True,
        "outsideCampus": False,
        "language": lang,
        "userCoordinates": {
            "lat": userLat,
            "lng": userLng,
            "accuracy": accuracyMeters,
            "altitude": altitudeMeters,
            "altitudeAccuracy": altitudeAccuracyMeters,
        },
        "nearest": result,
    }), 200


@mapController.route("/boundaries", methods=["GET"])
def getBuildingBoundariesEndpoint():
    """
    GET /api/map/boundaries
    Returns all defined campus building coordinate boundaries (polygons and radius checks)
    along with floor counts and altitude calibration metadata.
    """
    lang = _getPreferredLanguage()
    boundaries = []
    for bId, boundary in getAllBuildingBoundaries().items():
        macroNode = globalNavigationService.graph.getNode(bId)
        item = boundary.toDict()
        item["buildingName"] = macroNode.getName(lang) if macroNode else bId
        boundaries.append(item)

    return jsonify({
        "success": True,
        "count": len(boundaries),
        "beaconCount": len(BEACON_REGISTRY),
        "boundaries": boundaries,
    }), 200


@mapController.route("/buildings/<buildingId>/locations", methods=["GET"])
def getBuildingLocationsEndpoint(buildingId: str):
    """
    GET /api/map/buildings/<buildingId>/locations
    Returns ALL available location options for the specified building/zone,
    grouped by floor for manual fallback selection.
    Query Params:
      - floor: optional integer floor filter
      - lat / lng: optional user coordinates to sort locations by proximity
      - lang: 'eng' | 'spa'
    """
    lang = _getPreferredLanguage()
    if buildingId not in globalNavigationService.graph.nodes and not getBuildingSubgraph(buildingId):
        return jsonify({
            "success": False,
            "error": t("api.map_building_not_found", lang=lang, buildingId=buildingId),
        }), 404

    floorParam = request.args.get("floor")
    floorFilter = None
    if floorParam is not None and floorParam != "":
        try:
            floorFilter = int(floorParam)
        except ValueError:
            pass

    userLat = None
    userLng = None
    try:
        if request.args.get("lat") and request.args.get("lng"):
            userLat = float(request.args.get("lat"))
            userLng = float(request.args.get("lng"))
    except (ValueError, TypeError):
        pass

    payload = globalNavigationService.getBuildingLocations(
        buildingId=buildingId,
        userLat=userLat,
        userLng=userLng,
        floor=floorFilter,
        lang=lang,
    )

    return jsonify({
        "success": True,
        **payload,
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
            "error": t("api.map_subgraph_not_found", lang=lang, buildingId=buildingId)
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
    lang = normalize_language(payload.get("lang")) if payload.get("lang") else _getPreferredLanguage()

    if not origin or not destination:
        return jsonify({
            "success": False,
            "error": t("api.map_origin_dest_required", lang=lang)
        }), 400

    accessibleRaw = payload.get("accessibleOnly", False)
    accessibleOnly = str(accessibleRaw).lower() in ("true", "1", "yes")

    sg = getBuildingSubgraph(buildingId)
    if not sg:
        return jsonify({
            "success": False,
            "error": t("api.map_subgraph_not_found", lang=lang, buildingId=buildingId)
        }), 404

    result = sg.calculateIndoorRoute(
        originQuery=str(origin),
        destinationQuery=str(destination),
        accessibleOnly=accessibleOnly,
        lang=lang,
    )

    statusCode = 200 if result.get("success") else 404
    return jsonify(result), statusCode
