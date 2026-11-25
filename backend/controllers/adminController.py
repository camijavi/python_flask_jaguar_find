"""
adminController.py
================================================================================
ADMINISTRATION & CUSTODY MANAGEMENT CONTROLLER
================================================================================
Flask Blueprint providing RESTful API endpoints for CAE administrators:
system-wide KPIs & stats, custody status workflow management (moving items
from Reported -> In Custody -> Claimed), user directory inspection, password
resets, user creation, role assignment, and account status toggling.
"""

from flask import Blueprint, request, jsonify, session
from typing import Dict, Any, Optional
import sqlite3
import re

from backend.database import (
    MAX_CEDULA_LENGTH,
    MIN_CEDULA_LENGTH,
    getSystemStats,
    updateLostObjectState,
    getAllUsers,
    getLostObjectById,
    getUserById,
    createUser,
    updateUserPassword,
    updateUserStatus,
    updateUserRole,
    getUserByUsername,
    getUserByIdentifier,
)
from backend.auth_guard import admin_required
from backend.i18n import t

adminController = Blueprint("adminController", __name__, url_prefix="/api/admin")

STATE_I18N_KEYS = {
    1: "lost_found.state_reported",
    2: "lost_found.state_custody",
    3: "lost_found.state_claimed",
}

ROLE_I18N_KEYS = {
    1: "auth.role_student",
    2: "auth.role_collaborator",
    3: "auth.role_visitor_short",
    4: "auth.role_admin",
}


def _requireAdmin():
    """Validates that caller possesses an active admin session."""
    user = session.get("user")
    if not user or user.get("UserTypeId") != 4:
        return False
    return True


@adminController.route("/stats", methods=["GET"])
@admin_required
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
@admin_required
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
            "error": t("admin.api.item_not_found")
        }), 404

    payload = request.get_json(silent=True) or request.form.to_dict() or {}
    stateIdRaw = payload.get("stateId") or payload.get("lostObjectStateId")

    if stateIdRaw is None:
        return jsonify({"success": False, "error": t("admin.api.invalid_state")}), 400

    try:
        newStateId = int(stateIdRaw)
        if newStateId not in (1, 2, 3):
            raise ValueError()
    except (ValueError, TypeError):
        return jsonify({"success": False, "error": t("admin.api.invalid_state")}), 400

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
        return jsonify({"success": False, "error": t("admin.api.state_update_failed")}), 500

    updatedItem = getLostObjectById(itemId)
    localizedState = t(STATE_I18N_KEYS.get(newStateId, "common.unknown"))
    return jsonify({
        "success": True,
        "message": t("admin.api.item_state_updated", itemId=itemId, state=localizedState),
        "item": updatedItem,
    }), 200


@adminController.route("/users", methods=["GET"])
@admin_required
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


@adminController.route("/users", methods=["POST"])
@admin_required
def createNewUser():
    """
    POST /api/admin/users
    Administrative endpoint to register a new user account with assigned role.
    """
    payload = request.get_json(silent=True) or request.form.to_dict() or {}

    try:
        userTypeId = int(payload.get("userTypeId", 1))
    except (ValueError, TypeError):
        return jsonify({"success": False, "error": t("admin.api.invalid_user_type")}), 400

    fullName = (payload.get("fullName") or payload.get("nombre") or "").strip()
    userName = (payload.get("userName") or "").strip() or None
    cif = (payload.get("cif") or "").strip() or None
    govermentId = (payload.get("govermentId") or payload.get("cedula") or "").strip() or None
    phoneNumber = (payload.get("phoneNumber") or payload.get("telefono") or "").strip() or None
    email = (payload.get("email") or payload.get("correo") or "").strip() or None
    password = payload.get("password") or None

    if not fullName:
        return jsonify({"success": False, "error": t("admin.api.full_name_required")}), 400

    if userTypeId == 1 and not cif:
        return jsonify({"success": False, "error": t("admin.api.cif_required")}), 400
    if userTypeId == 2:
        if not govermentId:
            return jsonify({"success": False, "error": t("admin.api.cedula_required")}), 400
        if not MIN_CEDULA_LENGTH <= len(govermentId) <= MAX_CEDULA_LENGTH or not re.fullmatch(r"^\d{3}-?\d{6}-?\d{4}[A-Za-z]$", govermentId):
            return jsonify({"success": False, "error": t("admin.api.cedula_invalid")}), 400
        cleanGov = govermentId.replace("-", "").upper()
        govermentId = f"{cleanGov[:3]}-{cleanGov[3:9]}-{cleanGov[9:13]}{cleanGov[13]}"
    if userTypeId == 3:
        if not govermentId:
            return jsonify({"success": False, "error": t("admin.api.cedula_required")}), 400
        if not MIN_CEDULA_LENGTH <= len(govermentId) <= MAX_CEDULA_LENGTH or not re.fullmatch(r"^\d{3}-?\d{6}-?\d{4}[A-Za-z]$", govermentId):
            return jsonify({"success": False, "error": t("admin.api.cedula_invalid")}), 400
        cleanGov = govermentId.replace("-", "").upper()
        govermentId = f"{cleanGov[:3]}-{cleanGov[3:9]}-{cleanGov[9:13]}{cleanGov[13]}"

        if not phoneNumber:
            return jsonify({"success": False, "error": t("admin.api.phone_required")}), 400
        if re.search(r"[a-zA-Z]", phoneNumber):
            return jsonify({"success": False, "error": t("admin.api.phone_no_letters")}), 400
        cleanPhone = re.sub(r"\D", "", phoneNumber)
        if not cleanPhone or len(cleanPhone) < 7:
            return jsonify({"success": False, "error": t("admin.api.phone_min_digits")}), 400
        phoneNumber = cleanPhone

        if not email:
            return jsonify({"success": False, "error": t("admin.api.email_required")}), 400
        if not re.fullmatch(r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$", email):
            return jsonify({"success": False, "error": t("admin.api.email_invalid")}), 400
    if userTypeId == 4 and (not email or not password):
        return jsonify({"success": False, "error": t("admin.api.admin_credentials_required")}), 400

    try:
        newUserId = createUser(
            userTypeId=userTypeId,
            fullName=fullName,
            userName=userName,
            cif=cif,
            govermentId=govermentId,
            phoneNumber=phoneNumber,
            email=email,
            password=password,
        )
    except sqlite3.IntegrityError:
        return jsonify({"success": False, "error": t("admin.api.duplicate_user")}), 409
    except Exception:
        return jsonify({"success": False, "error": t("api.internal_error")}), 500

    newUser = getUserById(newUserId)
    return jsonify({
        "success": True,
        "message": t("admin.api.user_created"),
        "user": newUser,
    }), 201


@adminController.route("/users/<int:userId>/password", methods=["POST", "PUT"])
@admin_required
def resetUserPassword(userId: int):
    """
    POST/PUT /api/admin/users/<userId>/password
    Resets the password for a specific user account.
    Payload:
      - password: string (minimum 6 characters) [Required]
    """
    user = getUserById(userId)
    if not user:
        return jsonify({"success": False, "error": t("admin.api.user_not_found")}), 404

    payload = request.get_json(silent=True) or request.form.to_dict() or {}
    newPassword = (payload.get("password") or payload.get("newPassword") or "").strip()

    if not newPassword or len(newPassword) < 6:
        return jsonify({"success": False, "error": t("admin.api.password_min")}), 400

    success = updateUserPassword(userId, newPassword)
    if not success:
        return jsonify({"success": False, "error": t("admin.api.password_update_failed")}), 500

    return jsonify({
        "success": True,
        "message": t("admin.api.user_password_updated_for", userId=userId, name=user.get("FullName") or ""),
    }), 200


@adminController.route("/users/<int:userId>/status", methods=["POST", "PUT"])
@admin_required
def toggleUserActiveStatus(userId: int):
    """
    POST/PUT /api/admin/users/<userId>/status
    Toggles or sets the active status of an account (dar de baja / activar).
    Payload:
      - isActive: boolean or 0/1 [Optional; toggles if omitted]
    """
    user = getUserById(userId)
    if not user:
        return jsonify({"success": False, "error": t("admin.api.user_not_found")}), 404

    payload = request.get_json(silent=True) or request.form.to_dict() or {}
    if "isActive" in payload:
        newStatus = bool(payload["isActive"])
    else:
        newStatus = not bool(user.get("IsActive", 1))

    # Protect main admin from deactivating themselves
    currentAdmin = session.get("user")
    if currentAdmin and currentAdmin.get("Id") == userId and not newStatus:
        return jsonify({"success": False, "error": t("admin.api.cannot_deactivate_self")}), 400

    success = updateUserStatus(userId, newStatus)
    if not success:
        return jsonify({"success": False, "error": t("admin.api.status_update_failed")}), 500

    msgKey = "admin.api.user_activated_for" if newStatus else "admin.api.user_deactivated_for"
    return jsonify({
        "success": True,
        "isActive": newStatus,
        "message": t(msgKey, name=user.get("FullName") or ""),
    }), 200


@adminController.route("/users/<int:userId>/role", methods=["POST", "PUT"])
@admin_required
def changeUserRole(userId: int):
    """
    POST/PUT /api/admin/users/<userId>/role
    Reassigns a user's role (1: Student, 2: Collaborator, 3: Visitor, 4: Admin).
    Payload:
      - userTypeId: integer (1-4) [Required]
    """
    user = getUserById(userId)
    if not user:
        return jsonify({"success": False, "error": t("admin.api.user_not_found")}), 404

    payload = request.get_json(silent=True) or request.form.to_dict() or {}
    try:
        newUserTypeId = int(payload.get("userTypeId"))
        if newUserTypeId not in (1, 2, 3, 4):
            raise ValueError()
    except (ValueError, TypeError):
        return jsonify({"success": False, "error": t("admin.api.invalid_role")}), 400

    cif = payload.get("cif")
    govermentId = payload.get("govermentId") or payload.get("cedula")
    phoneNumber = payload.get("phoneNumber") or payload.get("telefono")

    try:
        success = updateUserRole(userId, newUserTypeId, cif=cif, govermentId=govermentId, phoneNumber=phoneNumber)
    except sqlite3.IntegrityError:
        return jsonify({"success": False, "error": t("admin.api.role_constraint_violation")}), 400

    if not success:
        return jsonify({"success": False, "error": t("admin.api.role_update_failed")}), 500

    updatedUser = getUserById(userId)
    localizedRole = t(ROLE_I18N_KEYS.get(newUserTypeId, "common.unknown"))
    return jsonify({
        "success": True,
        "message": t("admin.api.role_updated_for", name=user.get("FullName") or "", role=localizedRole),
        "user": updatedUser,
    }), 200
