"""
backend.controllers package
================================================================================
EXPORTS ALL CONTROLLER BLUEPRINTS AND REGISTRATION HELPER
================================================================================
Exposes:
- authController: /api/auth
- mapController: /api/map
- lostFoundObjectController: /api/lost-found-object
- adminController: /api/admin
"""

from .authController import authController
from .mapController import mapController
from .lostFoundObjectController import lostFoundObjectController
from .adminController import adminController

ALL_CONTROLLERS = [
    authController,
    mapController,
    lostFoundObjectController,
    adminController,
]


def registerControllers(app) -> None:
    """Convenience helper to register all controller blueprints onto a Flask app instance."""
    for controller in ALL_CONTROLLERS:
        app.register_blueprint(controller)


__all__ = [
    "authController",
    "mapController",
    "lostFoundObjectController",
    "adminController",
    "ALL_CONTROLLERS",
    "registerControllers",
]
