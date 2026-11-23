"""
auth_guard.py
================================================================================
SESSION AUTHENTICATION GUARDS, LOCALIZATION HELPERS & USER SANITIZATION
================================================================================
Provides route decorators and utilities to protect private endpoints:
- L(es, en): Context-aware bilingual string resolver using session language
- sanitizeUser(user): Strips security-sensitive fields (PasswordHash)
- getSessionUser(): Returns active user dict from session
- login_required: Enforces active session, redirecting visitors to /auth
- admin_required: Enforces CAE Admin (UserTypeId == 4) privileges
"""

from functools import wraps
from typing import Any, Callable, Dict, Optional
from flask import session, request, redirect, url_for, jsonify
from backend.i18n import get_current_language


def L(esText: str, enText: str) -> str:
    """Returns bilingual text according to current user session language."""
    lang = get_current_language()
    return enText if str(lang).lower().startswith("en") else esText


def sanitizeUser(user: Optional[Dict[str, Any]]) -> Dict[str, Any]:
    """Strips sensitive columns (PasswordHash) before returning to client."""
    if not user:
        return {}
    clean = dict(user)
    clean.pop("PasswordHash", None)
    return clean


def getSessionUser() -> Optional[Dict[str, Any]]:
    """Returns the current sanitized user dict from Flask session."""
    return session.get("user")


def login_required(view_func: Callable) -> Callable:
    """
    Decorator for views requiring an active authenticated user session.
    Redirects unauthenticated visitors to /auth (or returns 401 for API calls).
    """
    @wraps(view_func)
    def decorated_view(*args, **kwargs):
        user = session.get("user")
        if not user:
            if request.path.startswith("/api/") or request.is_json:
                return jsonify({
                    "success": False,
                    "error": L("Se requiere iniciar sesión.", "Authentication required.")
                }), 401
            return redirect("/auth?next=" + request.path)
        return view_func(*args, **kwargs)
    return decorated_view


def admin_required(view_func: Callable) -> Callable:
    """
    Decorator for views requiring administrator privileges (UserTypeId == 4).
    Redirects unauthorized users to /auth or /admin/adminsignin (or 403 for API calls).
    """
    @wraps(view_func)
    def decorated_view(*args, **kwargs):
        user = session.get("user")
        if not user or user.get("UserTypeId") != 4:
            if request.path.startswith("/api/") or request.is_json:
                return jsonify({
                    "success": False,
                    "error": L("Se requieren privilegios de administrador.", "Administrator privileges required.")
                }), 403
            return redirect("/admin/adminsignin?next=" + request.path)
        return view_func(*args, **kwargs)
    return decorated_view
