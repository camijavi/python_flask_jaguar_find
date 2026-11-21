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

from flask import Blueprint, request, jsonify, session
from typing import Dict, Any, List

from backend.graph.navigationService import globalNavigationService
from backend.graph.geoUtils import CampusGeoUtils
from backend.data.campusCategories import CampusCategory, CATEGORY_METADATA
from backend.data.placesCatalog import PLACES_CATALOG
from backend.subgraphs import getBuildingSubgraph, getAllBuildingSubgraphs

mapController = Blueprint("mapController", __name__, url_prefix="/api/map")


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


@mapController.route("/places", methods=["GET"])
def getPlaces():
    """
    GET /api/map/places
    Searches and filters registered campus places.
    Query Params:
      - category: filter by CampusCategory (e.g., 'drinkingFountain', 'medicalLab')
      - q: free-text search across name, keywords, and location notes
      - floor: integer floor filter (e.g. 1, 2)
    """
    categoryFilter = request.args.get("category")
    searchQuery = (request.args.get("q") or "").strip().lower()
    floorFilter = request.args.get("floor")

    results = []
    for place in PLACES_CATALOG:
        if categoryFilter and place.get("category") != categoryFilter:
            continue
        if floorFilter is not None:
            try:
                if place.get("floorLevel") != int(floorFilter):
                    continue
            except ValueError:
                pass

        if searchQuery:
            nameMatch = searchQuery in place.get("name", "").lower()
            notesMatch = searchQuery in place.get("locationNotes", "").lower()
            keywordMatch = any(searchQuery in kw.lower() for kw in place.get("keywords", []))
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
    Snaps a device GPS latitude/longitude coordinate to the nearest campus macro node.
    Validates whether the user's location is within the official UAM campus perimeter.
    Query Params:
      - lat: float latitude (e.g. 12.1077)
      - lng: float longitude (e.g. -86.2579)
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

    lang = _getPreferredLanguage()
    result = globalNavigationService.findNearestGpsNode(userLat, userLng, lang=lang)

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
        catalog.append({
            "buildingId": sg.buildingId,
            "name": sg.name,
            "code": sg.code,
            "floors": sg.floors,
            "macroNodeId": sg.macroNodeId,
            "entranceNodeIds": sg.entranceNodeIds,
            "description": sg.description,
            "totalNodes": len(sg.getAllNodes()),
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
