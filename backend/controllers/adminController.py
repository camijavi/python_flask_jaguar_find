"""
adminController.py
================================================================================
ADMINISTRATION & CUSTODY MANAGEMENT CONTROLLER
================================================================================
Flask Blueprint providing RESTful API endpoints for CAE administrators:
system-wide KPIs & stats, custody status workflow management (moving items
from Reported -> In Custody -> Claimed), and user account inspection.
"""

from flask import Blueprint, request, jsonify, session
from typing import Dict, Any

from backend.database import (
    getSystemStats,
    updateLostObjectState,
    getAllUsers,
    getLostObjectById,
)

adminController = Blueprint("adminController", __name__, url_prefix="/api/admin")


def _requireAdmin():
    """Validates that caller possesses an active admin session (optional enforcement)."""
    user = session.get("user")
    if not user or user.get("UserTypeId") != 4:
        return False
    return True


@adminController.route("/stats", methods=["GET"])
def getStats():
    """
    GET /api/admin/stats
    Returns aggregate metric counts for dashboard visualization:
    totalItems, reportedItems, inCustodyItems, claimedItems, totalUsers.
    """
    stats = getSystemStats()
    return jsonify({
        "success": True,
        "stats": stats,
    }), 200


@adminController.route("/items/<int:itemId>/state", methods=["PUT", "POST"])
def updateItemState(itemId: int):
    """
    PUT/POST /api/admin/items/<itemId>/state
    Updates the custody status of an item (1: Reported, 2: In Custody, 3: Claimed).
    Payload:
      - stateId: integer (1, 2, or 3) [Required]
      - resolvedByAdminId: integer (optional; falls back to active admin session user)
    """
    item = getLostObjectById(itemId)
    if not item:
        return jsonify({
            "success": False,
            "error": f"Item #{itemId} was not found."
        }), 404

    payload = request.get_json(silent=True) or request.form.to_dict() or {}
    stateIdRaw = payload.get("stateId") or payload.get("lostObjectStateId")

    if stateIdRaw is None:
        return jsonify({"success": False, "error": "'stateId' is required."}), 400

    try:
        newStateId = int(stateIdRaw)
        if newStateId not in (1, 2, 3):
            raise ValueError()
    except (ValueError, TypeError):
        return jsonify({"success": False, "error": "stateId must be an integer (1, 2, or 3)."}), 400

    # Determine resolvedByAdminId
    currentUser = session.get("user")
    resolvedBy = payload.get("resolvedByAdminId")
    if resolvedBy is not None:
        try:
            resolvedBy = int(resolvedBy)
        except ValueError:
            resolvedBy = None
    if resolvedBy is None and currentUser and currentUser.get("UserTypeId") == 4:
        resolvedBy = currentUser.get("Id")

    success = updateLostObjectState(
        reportId=itemId,
        newStateId=newStateId,
        resolvedByAdminId=resolvedBy
    )

    if not success:
        return jsonify({"success": False, "error": "Failed to update item state."}), 500

    updatedItem = getLostObjectById(itemId)
    return jsonify({
        "success": True,
        "message": f"Item #{itemId} status updated to '{updatedItem.get('StateName')}'.",
        "item": updatedItem,
    }), 200


@adminController.route("/users", methods=["GET"])
def listUsers():
    """
    GET /api/admin/users
    Returns complete registered user directory with role identifiers and active status.
    Password hashes are omitted.
    """
    users = getAllUsers()
    return jsonify({
        "success": True,
        "count": len(users),
        "users": users,
    }), 200
