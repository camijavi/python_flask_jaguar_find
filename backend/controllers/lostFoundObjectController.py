"""
lostFoundObjectController.py
================================================================================
LOST & FOUND OBJECT CONTROLLER
================================================================================
Flask Blueprint providing RESTful API endpoints for the JaguarFind module:
public lost & found item catalog, reporting discovered objects, item claim
submission with secret detail verification, custody state tracking, and
interactive map pin aggregations.
"""

from flask import Blueprint, request, jsonify, session
from typing import Dict, Any, List, Optional

from backend.database import (
    createLostObjectReport,
    getAllLostObjects,
    getLostObjectById,
    getCustodyStates,
)
from backend.graph.navigationService import globalNavigationService
from backend.graph.geoUtils import CampusGeoUtils
from backend.i18n import get_current_language, t

lostFoundObjectController = Blueprint(
    "lostFoundObjectController",
    __name__,
    url_prefix="/api/lost-found-object"
)

STATE_BADGES = {
    1: {"color": "amber", "labelKey": "lost_found.state_reported"},
    2: {"color": "blue", "labelKey": "lost_found.state_custody"},
    3: {"color": "emerald", "labelKey": "lost_found.state_claimed"},
}


def _getStateBadgeMeta(stateId: int, lang: Optional[str] = None) -> Dict[str, str]:
    meta = STATE_BADGES.get(stateId)
    if not meta:
        return {"color": "gray", "label": t("common.unknown", lang=lang)}
    return {"color": meta["color"], "label": t(meta["labelKey"], lang=lang)}


def _resolveLocationName(locationId: str, lang: Optional[str] = None) -> str:
    """Resolves a campus node ID (e.g. 'buildingB') to its localized display name."""
    loc = (locationId or "").strip()
    if not loc:
        return ""
    activeLang = lang or get_current_language()
    node = globalNavigationService.graph.getNode(loc)
    if node:
        return node.getName(activeLang)
    locLower = loc.lower()
    for nodeId, candidate in globalNavigationService.graph.nodes.items():
        if nodeId.lower() == locLower:
            return candidate.getName(activeLang)
    return loc


def _maskSecretDetail(item: Dict[str, Any], currentUserId: Optional[int], isAdmin: bool) -> Dict[str, Any]:
    """
    Hides private identification details (e.g., sticker, serial number, screen photo)
    from the public catalog unless the viewer is the administrator or the original reporter.
    """
    sanitized = dict(item)
    hasSecret = bool(sanitized.get("SecretDetail"))
    sanitized["hasSecretDetail"] = hasSecret
    sanitized["hasSignature"] = bool(sanitized.get("Signature"))
    sanitized["locationName"] = _resolveLocationName(sanitized.get("Location", ""))

    # Attach badge color and localized label metadata
    stateId = sanitized.get("LostObjectStateId", 1)
    badgeMeta = _getStateBadgeMeta(stateId)
    sanitized["badgeColor"] = badgeMeta["color"]
    sanitized["badgeLabel"] = badgeMeta["label"]

    isOwner = currentUserId is not None and sanitized.get("UserId") == currentUserId
    if not (isAdmin or isOwner):
        sanitized["SecretDetail"] = None

    return sanitized


@lostFoundObjectController.route("/items", methods=["GET"])
def listItems():
    """
    GET /api/lost-found-object/items
    Retrieves lost & found items with optional filtering by custody state,
    category, search keyword, and campus building/location node.
    """
    stateIdRaw = request.args.get("stateId")
    category = request.args.get("category")
    searchKeyword = (request.args.get("search") or request.args.get("q") or "").strip().lower()
    rawBuildingFilter = (request.args.get("building") or request.args.get("location") or "").strip()
    locationFilter = rawBuildingFilter.lower()

    stateId = None
    if stateIdRaw:
        try:
            stateId = int(stateIdRaw)
        except ValueError:
            pass

    currentUser = session.get("user")
    currentUserId = currentUser["Id"] if currentUser else None
    isAdmin = bool(currentUser and currentUser.get("UserTypeId") == 4)

    items = getAllLostObjects(stateId=stateId, category=category)

    filtered = []
    for rawItem in items:
        rawLoc = (rawItem.get("Location") or "").strip()

        # Filter by campus node / building ID (exact case-insensitive match)
        if locationFilter and locationFilter != rawLoc.lower():
            continue

        # Filter by search keyword (matches name, description, node ID, or localized building name)
        if searchKeyword:
            nameMatch = searchKeyword in rawItem.get("ItemName", "").lower()
            descMatch = searchKeyword in rawItem.get("Description", "").lower()
            locIdMatch = searchKeyword in rawLoc.lower()
            locSpaMatch = searchKeyword in _resolveLocationName(rawLoc, "spa").lower()
            locEngMatch = searchKeyword in _resolveLocationName(rawLoc, "eng").lower()
            if not (nameMatch or descMatch or locIdMatch or locSpaMatch or locEngMatch):
                continue

        sanitizedItem = _maskSecretDetail(rawItem, currentUserId=currentUserId, isAdmin=isAdmin)
        filtered.append(sanitizedItem)

    return jsonify({
        "success": True,
        "count": len(filtered),
        "building": rawBuildingFilter or None,
        "items": filtered,
    }), 200


@lostFoundObjectController.route("/items/<int:itemId>", methods=["GET"])
def getItemDetail(itemId: int):
    """
    GET /api/lost-found-object/items/<itemId>
    Returns detailed information about a specific lost & found object report.
    """
    item = getLostObjectById(itemId)
    if not item:
        return jsonify({
            "success": False,
            "error": t("lost_found.api.item_not_found")
        }), 404

    currentUser = session.get("user")
    currentUserId = currentUser["Id"] if currentUser else None
    isAdmin = bool(currentUser and currentUser.get("UserTypeId") == 4)

    sanitized = _maskSecretDetail(item, currentUserId=currentUserId, isAdmin=isAdmin)

    return jsonify({
        "success": True,
        "item": sanitized,
    }), 200


@lostFoundObjectController.route("/items", methods=["POST"])
def reportItem():
    """
    POST /api/lost-found-object/items
    Submits a new lost or found object report on campus.
    Payload:
      - itemName: string (e.g. 'Calculadora Casio fx-991LA') [Required]
      - location: string (macro campus node ID, e.g. 'buildingB') [Required]
      - description: string (public description) [Required]
      - category: string ('electronics' | 'documents' | 'personalItems' | 'clothing' | 'other')
      - secretDetail: string (private verification detail, e.g. sticker on back)
      - signature: string (base64 image or signature representation)
      - photoUrl: string (optional uploaded photo URL)
      - userId: integer (optional user link; defaults to active session user)
    """
    payload = request.get_json(silent=True) or request.form.to_dict() or {}

    itemName = (payload.get("itemName") or "").strip()
    location = (payload.get("location") or "").strip()
    description = (payload.get("description") or "").strip()
    category = (payload.get("category") or "other").strip()
    secretDetail = payload.get("secretDetail")
    signature = payload.get("signature")
    photoUrl = payload.get("photoUrl")

    if not itemName:
        return jsonify({"success": False, "error": t("lost_found.api.item_name_required")}), 400
    if not location:
        return jsonify({"success": False, "error": t("lost_found.api.location_required")}), 400
    if not description:
        return jsonify({"success": False, "error": t("lost_found.api.description_required")}), 400

    # Validate coordinates against campus perimeter (if GPS or coordinate pair is provided)
    lat = payload.get("latitude")
    lng = payload.get("longitude")
    if lat is not None and lng is not None and str(lat).strip() != "" and str(lng).strip() != "":
        try:
            latF = float(lat)
            lngF = float(lng)
            if not CampusGeoUtils.isWithinCampusPerimeter(latF, lngF, bufferMeters=30.0):
                return jsonify({
                    "success": False,
                    "error": t("lost_found.api.location_outside_campus")
                }), 400
        except (ValueError, TypeError):
            return jsonify({
                "success": False,
                "error": t("lost_found.api.invalid_gps_coords")
            }), 400
    elif "," in location:
        parts = [p.strip() for p in location.split(",")]
        if len(parts) == 2:
            try:
                latF = float(parts[0])
                lngF = float(parts[1])
                if not CampusGeoUtils.isWithinCampusPerimeter(latF, lngF, bufferMeters=30.0):
                    return jsonify({
                        "success": False,
                        "error": t("lost_found.api.location_outside_campus")
                    }), 400
            except ValueError:
                pass

    # Resolve reporter userId
    currentUser = session.get("user")
    userId = payload.get("userId")
    if userId is not None:
        try:
            userId = int(userId)
        except ValueError:
            userId = None
    if userId is None and currentUser:
        userId = currentUser.get("Id")

    try:
        newId = createLostObjectReport(
            itemName=itemName,
            location=location,
            description=description,
            category=category,
            userId=userId,
            lostObjectStateId=1,  # Initial state: Reported
            secretDetail=secretDetail.strip() if secretDetail else None,
            signature=signature.strip() if signature else None,
            photoUrl=photoUrl.strip() if photoUrl else None,
        )
    except Exception:
        return jsonify({"success": False, "error": t("lost_found.api.report_error")}), 500

    return jsonify({
        "success": True,
        "message": t("lost_found.api.report_created"),
        "id": newId,
    }), 201


@lostFoundObjectController.route("/items/<int:itemId>/claim", methods=["POST"])
def claimItem(itemId: int):
    """
    POST /api/lost-found-object/items/<itemId>/claim
    Submits a claim request for a lost item with claimant details and proof of ownership.
    """
    item = getLostObjectById(itemId)
    if not item:
        return jsonify({"success": False, "error": t("lost_found.api.item_not_found")}), 404

    if item.get("LostObjectStateId") == 3:
        return jsonify({
            "success": False,
            "error": t("lost_found.api.claim_already_claimed")
        }), 400

    payload = request.get_json(silent=True) or request.form.to_dict() or {}
    claimantName = (payload.get("claimantName") or "").strip()
    contact = (payload.get("contact") or payload.get("phoneNumber") or payload.get("email") or "").strip()
    secretAnswer = (payload.get("secretDetailVerification") or payload.get("secretAnswer") or "").strip()

    if not claimantName or not contact:
        return jsonify({
            "success": False,
            "error": t("lost_found.api.claim_missing_fields")
        }), 400

    actualSecret = (item.get("SecretDetail") or "").strip().lower()
    matchesSecret = bool(actualSecret and secretAnswer and secretAnswer.lower() in actualSecret)

    return jsonify({
        "success": True,
        "message": t("lost_found.api.claim_registered", itemId=itemId),
        "itemId": itemId,
        "claimStatus": "pending_admin_review",
        "secretVerificationMatch": matchesSecret,
    }), 200


@lostFoundObjectController.route("/map-pins", methods=["GET"])
def getMapPins():
    """
    GET /api/lost-found-object/map-pins
    Aggregates active lost and in-custody items by campus node to display
    interactive badge markers on the campus map.
    Only available to authenticated campus users.
    """
    currentUser = session.get("user")
    if not currentUser:
        return jsonify({
            "success": True,
            "totalPins": 0,
            "totalActiveItems": 0,
            "pins": [],
            "requiresAuth": True
        }), 200

    activeItems = getAllLostObjects()
    # Filter only Reported (1) or In Custody (2)
    activeItems = [i for i in activeItems if i.get("LostObjectStateId") in (1, 2)]

    lang = get_current_language()
    groupedByNode: Dict[str, List[Dict[str, Any]]] = {}
    for item in activeItems:
        loc = (item.get("Location") or "unknown").strip()
        groupedByNode.setdefault(loc, []).append({
            "id": item["Id"],
            "itemName": item["ItemName"],
            "category": item["Category"],
            "lostObjectStateId": item["LostObjectStateId"],
            "stateName": item["StateName"],
            "dateTimeReported": item["DateTimeReported"],
            "hasPhoto": bool(item.get("PhotoUrl")),
        })

    pins = []
    for nodeId, itemsList in groupedByNode.items():
        node = globalNavigationService.graph.getNode(nodeId)
        pins.append({
            "locationNodeId": nodeId,
            "locationName": node.getName(lang) if node else _resolveLocationName(nodeId, lang),
            "xPercent": node.xPercent if node else None,
            "yPercent": node.yPercent if node else None,
            "latitude": node.latitude if node else None,
            "longitude": node.longitude if node else None,
            "itemsCount": len(itemsList),
            "items": itemsList,
        })

    return jsonify({
        "success": True,
        "totalPins": len(pins),
        "totalActiveItems": len(activeItems),
        "pins": pins,
    }), 200


@lostFoundObjectController.route("/states", methods=["GET"])
def getStates():
    """
    GET /api/lost-found-object/states
    Returns all custody state definitions with colors and labels.
    """
    states = getCustodyStates()
    results = []
    for s in states:
        sId = s["Id"]
        badge = _getStateBadgeMeta(sId)
        results.append({
            "id": sId,
            "name": s["Name"],
            "badgeColor": badge["color"],
            "badgeLabel": badge["label"],
        })

    return jsonify({
        "success": True,
        "states": results,
    }), 200
