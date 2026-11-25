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

from flask import Blueprint, request, jsonify, session, redirect
from werkzeug.security import check_password_hash

from backend.auth_guard import getSessionUser, sanitizeUser
from backend.i18n import t
from backend.database import (
    MAX_CEDULA_LENGTH,
    MIN_CEDULA_LENGTH,
    createUser,
    getUserById,
    getUserByIdentifier,
    getUserByUsername,
)

authController = Blueprint("authController", __name__, url_prefix="/api/auth")

INSTITUTIONAL_DOMAIN = "@uamv.edu.ni"
MIN_PASSWORD_LENGTH = 6
USER_TYPE_LABELS = {1: "student", 2: "collaborator", 3: "visitor", 4: "admin"}

CEDULA_REGEX = re.compile(r"^\d{3}-?\d{6}-?\d{4}[A-Za-z]$")
EMAIL_REGEX = re.compile(r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$")


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
            "error": t("auth.errors.identifier_required")
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
            message = t("auth.errors.admin_invalid_credentials")
        else:
            message = t("auth.errors.account_not_found_identifier", identifier=identifier)
        return jsonify({"success": False, "error": message}), 401

    if not user.get("IsActive", 1):
        return jsonify({
            "success": False,
            "error": t("auth.errors.account_inactive")
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
                "error": t("auth.errors.password_required")
            }), 401
        if not passwordHash or not check_password_hash(passwordHash, password):
            if typeId == 4:
                message = t("auth.errors.admin_invalid_credentials")
            else:
                message = t("auth.errors.invalid_password")
            return jsonify({"success": False, "error": message}), 401

    cleanUser = _sanitizeUser(user)
    session["user"] = cleanUser

    return jsonify({
        "success": True,
        "message": t("auth.messages.welcome_back", name=cleanUser.get("FullName") or cleanUser.get("Email") or ""),
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
        return jsonify({"success": False, "error": t("auth.errors.invalid_user_type")}), 400

    if userTypeId == 4:
        return jsonify({
            "success": False,
            "error": t("auth.errors.admin_cannot_self_register")
        }), 403
    if userTypeId not in (1, 2, 3):
        return jsonify({"success": False, "error": t("auth.errors.invalid_user_type")}), 400

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

    if not fullName or len(fullName) < 2:
        return jsonify({"success": False, "field": "nombre", "error": t("auth.errors.full_name_required")}), 400

    # Role specific validations
    if userTypeId == 1:
        if not cif or not re.fullmatch(r"\d{8}", cif):
            return jsonify({"success": False, "field": "cif", "error": t("auth.errors.cif_required_digits")}), 400
    if userTypeId == 2:
        if not govermentId:
            return jsonify({"success": False, "field": "cedula", "error": t("auth.errors.cedula_required")}), 400
        if not MIN_CEDULA_LENGTH <= len(govermentId) <= MAX_CEDULA_LENGTH or not CEDULA_REGEX.fullmatch(govermentId):
            return jsonify({"success": False, "field": "cedula", "error": t("auth.errors.cedula_invalid_format")}), 400
        cleanGov = govermentId.replace("-", "").upper()
        govermentId = f"{cleanGov[:3]}-{cleanGov[3:9]}-{cleanGov[9:13]}{cleanGov[13]}"

    if userTypeId == 3:
        if not govermentId:
            return jsonify({"success": False, "field": "cedula", "error": t("auth.errors.cedula_required")}), 400
        if not MIN_CEDULA_LENGTH <= len(govermentId) <= MAX_CEDULA_LENGTH or not CEDULA_REGEX.fullmatch(govermentId):
            return jsonify({"success": False, "field": "cedula", "error": t("auth.errors.cedula_invalid_format")}), 400
        cleanGov = govermentId.replace("-", "").upper()
        govermentId = f"{cleanGov[:3]}-{cleanGov[3:9]}-{cleanGov[9:13]}{cleanGov[13]}"

        if not phoneNumber:
            return jsonify({"success": False, "field": "telefono", "error": t("auth.errors.phone_required")}), 400
        if re.search(r"[a-zA-Z]", phoneNumber):
            return jsonify({"success": False, "field": "telefono", "error": t("auth.errors.phone_no_letters")}), 400
        cleanPhone = re.sub(r"\D", "", phoneNumber)
        if not cleanPhone or len(cleanPhone) < 7:
            return jsonify({"success": False, "field": "telefono", "error": t("auth.errors.phone_min_digits")}), 400
        phoneNumber = cleanPhone

        if not email:
            return jsonify({"success": False, "field": "correoPersonal", "error": t("auth.errors.email_required")}), 400
        if not EMAIL_REGEX.fullmatch(email):
            return jsonify({"success": False, "field": "correoPersonal", "error": t("auth.errors.email_invalid")}), 400

    if userTypeId in (1, 2):
        if not email or not email.endswith(INSTITUTIONAL_DOMAIN):
            return jsonify({"success": False, "field": "correo", "error": t("auth.errors.institutional_email_required")}), 400
        if not password or len(password) < MIN_PASSWORD_LENGTH:
            return jsonify({"success": False, "field": "password", "error": t("auth.errors.password_min")}), 400
    else:
        password = None  # visitors are passwordless

    # Check for duplicate userName
    if userName and getUserByUsername(userName):
        return jsonify({"success": False, "error": t("auth.errors.username_taken", userName=userName)}), 409

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
            return jsonify({"success": False, "field": "cif", "error": t("auth.errors.duplicate_cif")}), 409
        if "govermentid" in errStr:
            return jsonify({"success": False, "field": "cedula", "error": t("auth.errors.duplicate_cedula")}), 409
        if "email" in errStr:
            fieldKey = "correoPersonal" if userTypeId == 3 else "correo"
            return jsonify({"success": False, "field": fieldKey, "error": t("auth.errors.duplicate_email")}), 409
        if "username" in errStr:
            return jsonify({"success": False, "error": t("auth.errors.duplicate_username")}), 409
        return jsonify({"success": False, "error": t("auth.errors.constraint_violation")}), 400
    except Exception as err:
        return jsonify({"success": False, "error": t("auth.errors.registration_failed", detail=str(err))}), 500

    createdUser = getUserById(newUserId)
    if not createdUser:
        return jsonify({"success": False, "error": t("auth.errors.user_retrieval_failed")}), 500

    cleanUser = _sanitizeUser(createdUser)
    session["user"] = cleanUser

    return jsonify({
        "success": True,
        "message": t("auth.messages.account_created"),
        "userId": newUserId,
        "user": cleanUser,
        "redirect": _homeUrlFor(cleanUser),
    }), 201


@authController.route("/logout", methods=["GET", "POST"])
def logout():
    """
    GET/POST /api/auth/logout
    Terminates active session and returns to Module 1 (Interactive Campus Map).
    """
    session.pop("user", None)
    if request.is_json or request.headers.get("Accept") == "application/json":
        return jsonify({
            "success": True,
            "message": t("auth.messages.signed_out"),
            "redirect": "/"
        }), 200
    return redirect("/")


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
