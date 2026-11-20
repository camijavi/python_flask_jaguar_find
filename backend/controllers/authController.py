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

from flask import Blueprint, request, jsonify, session
from typing import Dict, Any, Optional
import sqlite3

from backend.database import (
    createUser,
    getUserById,
    getUserByIdentifier,
    getUserByUsername,
    authenticateAdmin,
)

authController = Blueprint("authController", __name__, url_prefix="/api/auth")


def _sanitizeUser(user: Dict[str, Any]) -> Dict[str, Any]:
    """Removes sensitive security fields (e.g., PasswordHash) before client return."""
    clean = dict(user)
    clean.pop("PasswordHash", None)
    return clean


@authController.route("/login", methods=["POST"])
def login():
    """
    POST /api/auth/login
    Authenticates user based on role or universal handle:
    - Student: CIF (8 digits) or userName
    - Collaborator: GovermentId or userName
    - Visitor: GovermentId or userName
    - Admin: Email + Password (or userName + Password)
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
    password = payload.get("password")
    userTypeId = payload.get("userTypeId")

    if userTypeId is not None:
        try:
            userTypeId = int(userTypeId)
        except (ValueError, TypeError):
            userTypeId = None

    if not identifier:
        return jsonify({
            "success": False,
            "error": "An identifier (CIF, Government ID, Email, or UserName) is required."
        }), 400

    identifier = str(identifier).strip()
    user = None

    # 1. Admin Authentication (requires email/username + password)
    if password or userTypeId == 4 or "@" in identifier:
        # Try direct email + password
        user = authenticateAdmin(identifier, password)
        # Fallback: check if username was provided instead of email
        if not user and password:
            uByUname = getUserByUsername(identifier)
            if uByUname and uByUname.get("UserTypeId") == 4 and uByUname.get("Email"):
                user = authenticateAdmin(uByUname["Email"], password)

        if not user:
            return jsonify({
                "success": False,
                "error": "Invalid email or password for administrator."
            }), 401

    # 2. Universal / Role-based Authentication for Campus Users (Students, Collaborators, Visitors)
    else:
        # Check by specific role if userTypeId provided
        if userTypeId in (1, 2, 3):
            user = getUserByIdentifier(identifier, userTypeId=userTypeId)

        # Fallback to general lookup across CIF, GovermentId, Email, and UserName
        if not user:
            user = getUserByIdentifier(identifier)

        if not user:
            user = getUserByUsername(identifier)

        if not user:
            return jsonify({
                "success": False,
                "error": f"No active user found with identifier: '{identifier}'."
            }), 401

    if not user.get("IsActive", 1):
        return jsonify({
            "success": False,
            "error": "This account has been deactivated. Please contact campus administration."
        }), 403

    cleanUser = _sanitizeUser(user)
    session["user"] = cleanUser

    return jsonify({
        "success": True,
        "message": f"Welcome back, {cleanUser.get('FullName', 'User')}!",
        "user": cleanUser
    }), 200


@authController.route("/signup", methods=["POST"])
def signup():
    """
    POST /api/auth/signup
    Registers a new campus user adhering to conditional identity rules:
    - Student (1): requires CIF
    - Collaborator (2): requires GovermentId
    - Visitor (3): requires GovermentId and PhoneNumber
    - Admin (4): requires Email and Password
    """
    payload = request.get_json(silent=True) or request.form.to_dict() or {}

    userTypeIdRaw = payload.get("userTypeId", 1)
    try:
        userTypeId = int(userTypeIdRaw)
    except (ValueError, TypeError):
        return jsonify({"success": False, "error": "Invalid userTypeId format."}), 400

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
    password = payload.get("password")

    if not fullName:
        return jsonify({"success": False, "error": "FullName is required."}), 400

    # Role specific validations
    if userTypeId == 1 and not cif:
        return jsonify({"success": False, "error": "CIF (Student ID) is required for students."}), 400
    if userTypeId == 2 and not govermentId:
        return jsonify({"success": False, "error": "Government ID (Cédula/Passport) is required for collaborators."}), 400
    if userTypeId == 3:
        if not govermentId or not phoneNumber:
            return jsonify({
                "success": False,
                "error": "Both Government ID and PhoneNumber are required for visitors."
            }), 400
    if userTypeId == 4:
        if not email or not password:
            return jsonify({"success": False, "error": "Email and Password are required for administrators."}), 400

    # Check for duplicate userName
    if userName:
        existingUname = getUserByUsername(userName)
        if existingUname:
            return jsonify({"success": False, "error": f"UserName '{userName}' is already in use."}), 409

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
            return jsonify({"success": False, "error": "A user with this CIF already exists."}), 409
        if "govermentid" in errStr:
            return jsonify({"success": False, "error": "A user with this Government ID already exists."}), 409
        if "email" in errStr:
            return jsonify({"success": False, "error": "A user with this Email already exists."}), 409
        if "username" in errStr:
            return jsonify({"success": False, "error": "This UserName is already taken."}), 409
        return jsonify({"success": False, "error": "Database constraint violation occurred."}), 400
    except Exception as err:
        return jsonify({"success": False, "error": str(err)}), 500

    createdUser = getUserById(newUserId)
    if not createdUser:
        return jsonify({"success": False, "error": "Failed to retrieve created user."}), 500

    cleanUser = _sanitizeUser(createdUser)
    session["user"] = cleanUser

    return jsonify({
        "success": True,
        "message": "User registration completed successfully.",
        "userId": newUserId,
        "user": cleanUser
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
