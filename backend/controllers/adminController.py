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

from backend.database import (
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
from backend.auth_guard import L, admin_required

adminController = Blueprint("adminController", __name__, url_prefix="/api/admin")


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
        "message": f"Estado del objeto #{itemId} actualizado a '{updatedItem.get('StateName')}'.",
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
        return jsonify({"success": False, "error": "userTypeId must be an integer (1-4)."}), 400

    fullName = (payload.get("fullName") or payload.get("nombre") or "").strip()
    userName = (payload.get("userName") or "").strip() or None
    cif = (payload.get("cif") or "").strip() or None
    govermentId = (payload.get("govermentId") or payload.get("cedula") or "").strip() or None
    phoneNumber = (payload.get("phoneNumber") or payload.get("telefono") or "").strip() or None
    email = (payload.get("email") or payload.get("correo") or "").strip() or None
    password = payload.get("password") or None

    if not fullName:
        return jsonify({"success": False, "error": "El nombre completo es obligatorio."}), 400

    if userTypeId == 1 and not cif:
        return jsonify({"success": False, "error": "El CIF de 8 dígitos es obligatorio para estudiantes."}), 400
    if userTypeId in (2, 3) and not govermentId:
        return jsonify({"success": False, "error": "La cédula de identidad es obligatoria."}), 400
    if userTypeId == 3 and not phoneNumber:
        return jsonify({"success": False, "error": "El número de teléfono es obligatorio para visitantes."}), 400
    if userTypeId == 4 and (not email or not password):
        return jsonify({"success": False, "error": "Correo institucional y contraseña requeridos para administradores."}), 400

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
    except sqlite3.IntegrityError as err:
        return jsonify({"success": False, "error": f"Conflicto de unicidad en base de datos: {str(err)}"}), 409
    except Exception as err:
        return jsonify({"success": False, "error": str(err)}), 500

    newUser = getUserById(newUserId)
    return jsonify({
        "success": True,
        "message": "Usuario creado exitosamente.",
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
        return jsonify({"success": False, "error": f"Usuario con ID #{userId} no encontrado."}), 404

    payload = request.get_json(silent=True) or request.form.to_dict() or {}
    newPassword = (payload.get("password") or payload.get("newPassword") or "").strip()

    if not newPassword or len(newPassword) < 6:
        return jsonify({"success": False, "error": "La nueva contraseña debe tener al menos 6 caracteres."}), 400

    success = updateUserPassword(userId, newPassword)
    if not success:
        return jsonify({"success": False, "error": "No se pudo actualizar la contraseña."}), 500

    return jsonify({
        "success": True,
        "message": f"Contraseña del usuario #{userId} ({user.get('FullName')}) actualizada exitosamente.",
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
        return jsonify({"success": False, "error": f"Usuario #{userId} no encontrado."}), 404

    payload = request.get_json(silent=True) or request.form.to_dict() or {}
    if "isActive" in payload:
        newStatus = bool(payload["isActive"])
    else:
        newStatus = not bool(user.get("IsActive", 1))

    # Protect main admin from deactivating themselves
    currentAdmin = session.get("user")
    if currentAdmin and currentAdmin.get("Id") == userId and not newStatus:
        return jsonify({"success": False, "error": "No puedes desactivar tu propia cuenta administradora activa."}), 400

    success = updateUserStatus(userId, newStatus)
    if not success:
        return jsonify({"success": False, "error": "No se pudo actualizar el estado del usuario."}), 500

    statusText = "activada" if newStatus else "dada de baja"
    return jsonify({
        "success": True,
        "isActive": newStatus,
        "message": f"Cuenta de {user.get('FullName')} ha sido {statusText}.",
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
        return jsonify({"success": False, "error": f"Usuario #{userId} no encontrado."}), 404

    payload = request.get_json(silent=True) or request.form.to_dict() or {}
    try:
        newUserTypeId = int(payload.get("userTypeId"))
        if newUserTypeId not in (1, 2, 3, 4):
            raise ValueError()
    except (ValueError, TypeError):
        return jsonify({"success": False, "error": "userTypeId debe ser un entero entre 1 y 4."}), 400

    cif = payload.get("cif")
    govermentId = payload.get("govermentId") or payload.get("cedula")
    phoneNumber = payload.get("phoneNumber") or payload.get("telefono")

    try:
        success = updateUserRole(userId, newUserTypeId, cif=cif, govermentId=govermentId, phoneNumber=phoneNumber)
    except sqlite3.IntegrityError as err:
        return jsonify({"success": False, "error": f"Restricción de identidad de rol no cumplida: {str(err)}"}), 400

    if not success:
        return jsonify({"success": False, "error": "No se pudo actualizar el rol del usuario."}), 500

    updatedUser = getUserById(userId)
    return jsonify({
        "success": True,
        "message": f"Rol de {user.get('FullName')} actualizado a '{updatedUser.get('UserTypeName')}'.",
        "user": updatedUser,
    }), 200
