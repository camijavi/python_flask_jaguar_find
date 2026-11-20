"""
app.py
================================================================================
FLASK APPLICATION FACTORY FOR JAGUARFIND & JAGUARMAPS
================================================================================
Initializes the Flask WSGI application, registers modular controller blueprints,
sets up error handling, and verifies database readiness.
"""

from flask import Flask, jsonify, request, session
from backend.config import Config
from backend.database import initDb
from backend.controllers import registerControllers


def createApp(configClass=Config) -> Flask:
    """Creates and configures an instance of the Flask application."""
    app = Flask(
        __name__,
        template_folder="../frontend/screens",
        static_folder="../frontend/static",
    )
    app.config.from_object(configClass)

    # Ensure database schema and lookup tables are initialized
    initDb()

    # Register all controller blueprints (/api/auth, /api/map, /api/lost-found-object, /api/admin)
    registerControllers(app)

    # Global Error Handlers for API endpoints
    @app.errorhandler(404)
    def notFound(error):
        if request.path.startswith("/api/"):
            return jsonify({
                "success": False,
                "error": "Requested API endpoint not found.",
                "path": request.path,
            }), 404
        return jsonify({"success": False, "error": "Resource not found."}), 404

    @app.errorhandler(500)
    def internalServerError(error):
        return jsonify({
            "success": False,
            "error": "An internal server error occurred.",
        }), 500

    @app.route("/api/health", methods=["GET"])
    def healthCheck():
        """Health check probe endpoint for uptime monitoring."""
        return jsonify({
            "status": "healthy",
            "system": "JaguarFind & JaguarMaps UAM",
            "version": "2.0.0",
            "endpoints": [
                "/api/auth",
                "/api/map",
                "/api/lost-found-object",
                "/api/admin",
            ],
        }), 200

    return app


app = createApp()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
