"""
authController.py
================================================================================
AUTHENTICATION & USER IDENTITY CONTROLLER
================================================================================
Flask Blueprint providing RESTful API endpoints for user authentication,
role-specific credential verification (Student CIF, Collaborator GovId,
Visitor GovId + Phone, Admin Email + Password), signup, session management,
and user profile resolution.
"""

import re
import sqlite3
from typing import Any, Dict, Optional

from flask import Blueprint, request, jsonify, session
from werkzeug.security import check_password_hash

from backend.auth_guard import L, getSessionUser, sanitizeUser
from backend.database import (
    createUser,
    getUserById,
    getUserByIdentifier,
    getUserByUsername,
)

authController = Blueprint("authController", __name__, url_prefix="/api/auth")

INSTITUTIONAL_DOMAIN = "@uamv.edu.ni"
MIN_PASSWORD_LENGTH = 6
USER_TYPE_LABELS = {1: "student", 2: "collaborator", 3: "visitor", 4: "admin"}


def _sanitizeUser(user: Dict[str, Any]) -> Dict[str, Any]:
    """Removes sensitive security fields (e.g., PasswordHash) before client return."""
    return sanitizeUser(user)


def _homeUrlFor(user: Dict[str, Any]) -> str:
    """Where the client should land after authenticating."""
    return "/admin/dashboard" if user.get("UserTypeId") == 4 else "/lost-found-object/catalogo"


@authController.route("/login", methods=["POST"])
def login():
    """
    POST /api/auth/login
    Authenticates a user. The identifier depends on the role chosen in the UI:
    - Student (1):      CIF (8 digits)          [+ password, when the account has one]
    - Collaborator (2): GovermentId (cédula)    [+ password, when the account has one]
    - Visitor (3):      GovermentId (cédula)    passwordless
    - Admin (4):        Email or UserName       + password (always)
    """
    payload = request.get_json(silent=True) or request.form.to_dict() or {}

    identifier = (
        payload.get("identifier")
        or payload.get("cif")
        or payload.get("govermentId")
        or payload.get("email")
        or payload.get("userName")
        or payload.get("username")
    )
    password = payload.get("password") or ""
    userTypeId = payload.get("userTypeId")

    if userTypeId is not None:
        try:
            userTypeId = int(userTypeId)
        except (ValueError, TypeError):
            userTypeId = None

    if not identifier or not str(identifier).strip():
        return jsonify({
            "success": False,
            "error": L("Ingresa tu identificación (CIF, cédula o correo).",
                       "An identifier (CIF, Government ID, Email, or UserName) is required.")
        }), 400

    identifier = str(identifier).strip()

    # Resolve the account (role-specific lookup first, then universal handles)
    user: Optional[Dict[str, Any]] = None
    if userTypeId in (1, 2, 3, 4):
        user = getUserByIdentifier(identifier, userTypeId=userTypeId)
        if not user and userTypeId == 4:
            candidate = getUserByUsername(identifier)
            if candidate and candidate.get("UserTypeId") == 4:
                user = candidate
    if not user and userTypeId is None:
        user = getUserByIdentifier(identifier) or getUserByUsername(identifier)

    if not user:
        if userTypeId == 4:
            message = L("Correo o contraseña de administrador incorrectos.",
                        "Invalid email or password for administrator.")
        else:
            message = L("No encontramos una cuenta con ese dato para este rol.",
                        f"No active user found with identifier: '{identifier}'.")
        return jsonify({"success": False, "error": message}), 401

    if not user.get("IsActive", 1):
        return jsonify({
            "success": False,
            "error": L("Esta cuenta fue dada de baja. Contacta a la administración del campus.",
                       "This account has been deactivated. Please contact campus administration.")
        }), 403

    # Password policy: admins always, students/collaborators when a password was set, visitors never
    typeId = user.get("UserTypeId")
    passwordHash = user.get("PasswordHash")
    needsPassword = typeId == 4 or (typeId in (1, 2) and bool(passwordHash))

    if needsPassword:
        if not password:
            return jsonify({
                "success": False,
                "passwordRequired": True,
                "error": L("Esta cuenta requiere contraseña.", "This account requires a password.")
            }), 401
        if not passwordHash or not check_password_hash(passwordHash, password):
            if typeId == 4:
                message = L("Correo o contraseña de administrador incorrectos.",
                            "Invalid email or password for administrator.")
            else:
                message = L("Contraseña incorrecta.", "Incorrect password.")
            return jsonify({"success": False, "error": message}), 401

    cleanUser = _sanitizeUser(user)
    session["user"] = cleanUser

    return jsonify({
        "success": True,
        "message": L(f"¡Bienvenido/a, {cleanUser.get('FullName', 'Usuario')}!",
                     f"Welcome back, {cleanUser.get('FullName', 'User')}!"),
        "user": cleanUser,
        "redirect": _homeUrlFor(cleanUser),
    }), 200


@authController.route("/signup", methods=["POST"])
def signup():
    """
    POST /api/auth/signup
    Public self-registration for campus users adhering to conditional identity rules:
    - Student (1):      FullName + CIF (8 digits) + institutional email + password (>= 6)
    - Collaborator (2): FullName + GovermentId + institutional email + password (>= 6)
    - Visitor (3):      FullName + GovermentId + PhoneNumber (passwordless)
    Administrators (4) are never self-registered: they are created from /admin/usuarios.
    """
    payload = request.get_json(silent=True) or request.form.to_dict() or {}

    userTypeIdRaw = payload.get("userTypeId", 1)
    try:
        userTypeId = int(userTypeIdRaw)
    except (ValueError, TypeError):
        return jsonify({"success": False, "error": L("Rol inválido.", "Invalid userTypeId format.")}), 400

    if userTypeId == 4:
        return jsonify({
            "success": False,
            "error": L("Las cuentas de administrador no se pueden autorregistrar.",
                       "Administrator accounts cannot be self-registered.")
        }), 403
    if userTypeId not in (1, 2, 3):
        return jsonify({"success": False, "error": L("Rol inválido.", "Invalid userTypeId.")}), 400

    fullName = (payload.get("fullName") or "").strip()
    userName = payload.get("userName") or payload.get("username")
    userName = userName.strip() if userName else None
    cif = payload.get("cif")
    cif = str(cif).strip() if cif else None
    govermentId = payload.get("govermentId")
    govermentId = str(govermentId).strip() if govermentId else None
    phoneNumber = payload.get("phoneNumber")
    phoneNumber = str(phoneNumber).strip() if phoneNumber else None
    email = payload.get("email")
    email = str(email).strip().lower() if email else None
    password = payload.get("password") or None

    if not fullName:
        return jsonify({"success": False, "error": L("El nombre completo es obligatorio.", "FullName is required.")}), 400

    # Role specific validations
    if userTypeId == 1:
        if not cif or not re.fullmatch(r"\d{8}", cif):
            return jsonify({"success": False, "error": L("El CIF debe tener exactamente 8 dígitos.",
                                                         "CIF must be exactly 8 digits.")}), 400
    if userTypeId == 2 and not govermentId:
        return jsonify({"success": False, "error": L("La cédula es obligatoria para colaboradores.",
                                                     "Government ID is required for collaborators.")}), 400
    if userTypeId == 3 and (not govermentId or not phoneNumber):
        return jsonify({"success": False, "error": L("Los visitantes deben indicar cédula y teléfono.",
                                                     "Both Government ID and PhoneNumber are required for visitors.")}), 400

    if userTypeId in (1, 2):
        if not email or not email.endswith(INSTITUTIONAL_DOMAIN):
            return jsonify({"success": False, "error": L(f"Usa tu correo institucional ({INSTITUTIONAL_DOMAIN}).",
                                                         f"Use your institutional email ({INSTITUTIONAL_DOMAIN}).")}), 400
        if not password or len(password) < MIN_PASSWORD_LENGTH:
            return jsonify({"success": False, "error": L(f"La contraseña debe tener al menos {MIN_PASSWORD_LENGTH} caracteres.",
                                                         f"Password must be at least {MIN_PASSWORD_LENGTH} characters.")}), 400
    else:
        password = None  # visitors are passwordless

    # Check for duplicate userName
    if userName and getUserByUsername(userName):
        return jsonify({"success": False, "error": L(f"El usuario '{userName}' ya está en uso.",
                                                     f"UserName '{userName}' is already in use.")}), 409

    try:
        newUserId = createUser(
            userTypeId=userTypeId,
            fullName=fullName,
            userName=userName,
            cif=cif,
            govermentId=govermentId,
            phoneNumber=phoneNumber,
            email=email,
            password=password
        )
    except sqlite3.IntegrityError as err:
        errStr = str(err).lower()
        if "cif" in errStr:
            msg = L("Ya existe un usuario con ese CIF.", "A user with this CIF already exists.")
            return jsonify({"success": False, "error": msg}), 409
        if "govermentid" in errStr:
            msg = L("Ya existe un usuario con esa cédula.", "A user with this Government ID already exists.")
            return jsonify({"success": False, "error": msg}), 409
        if "email" in errStr:
            msg = L("Ya existe un usuario con ese correo.", "A user with this Email already exists.")
            return jsonify({"success": False, "error": msg}), 409
        if "username" in errStr:
            msg = L("Ese nombre de usuario ya está tomado.", "This UserName is already taken.")
            return jsonify({"success": False, "error": msg}), 409
        return jsonify({"success": False, "error": L("Los datos no cumplen las reglas del rol.",
                                                     "Database constraint violation occurred.")}), 400
    except Exception as err:
        return jsonify({"success": False, "error": str(err)}), 500

    createdUser = getUserById(newUserId)
    if not createdUser:
        return jsonify({"success": False, "error": "Failed to retrieve created user."}), 500

    cleanUser = _sanitizeUser(createdUser)
    session["user"] = cleanUser

    return jsonify({
        "success": True,
        "message": L("Registro completado.", "User registration completed successfully."),
        "userId": newUserId,
        "user": cleanUser,
        "redirect": _homeUrlFor(cleanUser),
    }), 201


@authController.route("/logout", methods=["POST"])
def logout():
    """
    POST /api/auth/logout
    Terminates the active user session.
    """
    session.pop("user", None)
    return jsonify({
        "success": True,
        "message": "Logged out successfully."
    }), 200


@authController.route("/me", methods=["GET"])
def getCurrentUser():
    """
    GET /api/auth/me
    Returns current authenticated session user profile or unauthenticated status.
    """
    currentUser = session.get("user")
    if not currentUser:
        return jsonify({
            "success": True,
            "authenticated": False,
            "user": None
        }), 200

    # Refresh data from database to ensure up-to-date role and status
    dbUser = getUserById(currentUser["Id"])
    if dbUser and dbUser.get("IsActive", 1):
        cleanUser = _sanitizeUser(dbUser)
        session["user"] = cleanUser
        return jsonify({
            "success": True,
            "authenticated": True,
            "user": cleanUser
        }), 200

    session.pop("user", None)
    return jsonify({
        "success": True,
        "authenticated": False,
        "user": None
    }), 200
