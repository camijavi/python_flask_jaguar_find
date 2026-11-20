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

lostFoundObjectController = Blueprint(
    "lostFoundObjectController",
    __name__,
    url_prefix="/api/lost-found-object"
)

STATE_BADGES = {
    1: {"color": "amber", "label": "Reportado"},
    2: {"color": "blue", "label": "En Custodia (Edif. A)"},
    3: {"color": "emerald", "label": "Entregado / Reclamado"},
}


def _maskSecretDetail(item: Dict[str, Any], currentUserId: Optional[int], isAdmin: bool) -> Dict[str, Any]:
    """
    Hides private identification details (e.g., sticker, serial number, screen photo)
    from the public catalog unless the viewer is the administrator or the original reporter.
    """
    sanitized = dict(item)
    hasSecret = bool(sanitized.get("SecretDetail"))
    sanitized["hasSecretDetail"] = hasSecret
    sanitized["hasSignature"] = bool(sanitized.get("Signature"))

    # Attach badge color and label metadata
    stateId = sanitized.get("LostObjectStateId", 1)
    badgeMeta = STATE_BADGES.get(stateId, {"color": "gray", "label": "Desconocido"})
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
    category, search keyword, and campus location node.
    """
    stateIdRaw = request.args.get("stateId")
    category = request.args.get("category")
    searchKeyword = (request.args.get("search") or request.args.get("q") or "").strip().lower()
    locationFilter = (request.args.get("location") or "").strip().lower()

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
        # Filter by search keyword
        if searchKeyword:
            nameMatch = searchKeyword in rawItem.get("ItemName", "").lower()
            descMatch = searchKeyword in rawItem.get("Description", "").lower()
            locMatch = searchKeyword in rawItem.get("Location", "").lower()
            if not (nameMatch or descMatch or locMatch):
                continue

        # Filter by campus node location
        if locationFilter and locationFilter != rawItem.get("Location", "").lower():
            continue

        sanitizedItem = _maskSecretDetail(rawItem, currentUserId=currentUserId, isAdmin=isAdmin)
        filtered.append(sanitizedItem)

    return jsonify({
        "success": True,
        "count": len(filtered),
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
            "error": f"Lost object report with ID #{itemId} was not found."
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
        return jsonify({"success": False, "error": "ItemName is required."}), 400
    if not location:
        return jsonify({"success": False, "error": "Location (campus node) is required."}), 400
    if not description:
        return jsonify({"success": False, "error": "Description is required."}), 400

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
    except Exception as err:
        return jsonify({"success": False, "error": str(err)}), 500

    return jsonify({
        "success": True,
        "message": "Lost object report successfully submitted.",
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
        return jsonify({"success": False, "error": f"Item #{itemId} not found."}), 404

    if item.get("LostObjectStateId") == 3:
        return jsonify({
            "success": False,
            "error": "This item has already been claimed and delivered to its owner."
        }), 400

    payload = request.get_json(silent=True) or request.form.to_dict() or {}
    claimantName = (payload.get("claimantName") or "").strip()
    contact = (payload.get("contact") or payload.get("phoneNumber") or payload.get("email") or "").strip()
    secretAnswer = (payload.get("secretDetailVerification") or payload.get("secretAnswer") or "").strip()

    if not claimantName or not contact:
        return jsonify({
            "success": False,
            "error": "Both claimantName and contact information are required."
        }), 400

    actualSecret = (item.get("SecretDetail") or "").strip().lower()
    matchesSecret = bool(actualSecret and secretAnswer and secretAnswer.lower() in actualSecret)

    return jsonify({
        "success": True,
        "message": (
            "Your claim request has been registered. Please present your identification "
            "at Building A (Student Services CAE / Lost & Found Custody) to complete handover."
        ),
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
    """
    activeItems = getAllLostObjects()
    # Filter only Reported (1) or In Custody (2)
    activeItems = [i for i in activeItems if i.get("LostObjectStateId") in (1, 2)]

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
        })

    pins = []
    for nodeId, itemsList in groupedByNode.items():
        node = globalNavigationService.graph.getNode(nodeId)
        pins.append({
            "locationNodeId": nodeId,
            "locationName": node.name if node else nodeId,
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
        badge = STATE_BADGES.get(sId, {"color": "gray", "label": s["Name"]})
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
