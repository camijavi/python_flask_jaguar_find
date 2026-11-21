"""
app.py
================================================================================
FLASK APPLICATION FACTORY FOR JAGUARFIND & JAGUARMAPS
================================================================================
Initializes the Flask WSGI application, registers modular controller blueprints,
sets up Jinja2 multi-folder template loading, injects the global i18n engine,
configures error handling, and provides web page and language switching routes.
"""

import os
from pathlib import Path
from flask import Flask, jsonify, request, session, render_template, redirect, url_for
from jinja2 import ChoiceLoader, FileSystemLoader

from backend.config import Config
from backend.database import initDb
from backend.controllers import registerControllers
from backend.i18n import init_i18n, I18nManager, t, get_current_language


def createApp(configClass=Config) -> Flask:
    """Creates and configures an instance of the Flask application."""
    frontendDir = Path(__file__).resolve().parent.parent / "frontend"
    staticDir = frontendDir / "static"

    app = Flask(
        __name__,
        static_folder=str(staticDir),
        static_url_path="/static",
    )
    app.config.from_object(configClass)

    # Configure Jinja2 to discover templates across frontend/, screens/, and components/
    app.jinja_loader = ChoiceLoader([
        FileSystemLoader(str(frontendDir)),
        FileSystemLoader(str(frontendDir / "screens")),
        FileSystemLoader(str(frontendDir / "screens" / "map")),
        FileSystemLoader(str(frontendDir / "components")),
        FileSystemLoader(str(frontendDir / "components" / "map")),
        FileSystemLoader(str(frontendDir / "components" / "common")),
    ])

    # Initialize i18n support for Jinja2 (injects t, current_language, etc.)
    init_i18n(app)

    # Ensure database schema and lookup tables are initialized
    initDb()

    # Register all controller blueprints (/api/auth, /api/map, /api/lost-found-object, /api/admin)
    registerControllers(app)

    # Context processor to pass dictionary of translations to templates for client-side JS
    @app.context_processor
    def injectClientI18n():
        currLang = get_current_language()
        i18nMgr = I18nManager.getInstance()
        langDict = i18nMgr.translations.get(currLang, {})
        return {
            "current_lang": currLang,
            "i18n_dict": langDict,
        }

    # ==========================================================================
    # WEB UI ROUTES
    # ==========================================================================

    @app.route("/", methods=["GET"])
    @app.route("/map", methods=["GET"])
    @app.route("/mapa", methods=["GET"])
    def renderMapScreen():
        """Renders the main interactive JaguarMaps navigation interface."""
        return render_template("mapScreen.html")

    @app.route("/auth")
    def renderLogInScreen():
        """Pantalla de entrada: sign up or signIn."""
        return render_template("screens/auth/logInScreen.html")

    @app.route("/auth/options")
    def renderUserOptions():
        """Selección de rol (Estudiante / Colaborador / Visitante)."""
        return render_template("screens/auth/userOptions.html")

    @app.route("/auth/signup")
    def renderSigUp():
        """Formulario de registro, filtrado por el rol elegido."""
        rol = request.args.get("rol", "estudiante")
        if rol not in ("estudiante", "colaborador", "visitante"):
            rol = "estudiante"
        return render_template("screens/auth/signUpScreen.html", rol=rol)

    @app.route("/auth/signin")
    def renderSignIn():
        """Formulario de inicio de sesión."""
        return render_template("screens/auth/signInScreen.html")


    @app.route("/set-language/<lang>", methods=["GET", "POST"])
    def setLanguage(lang: str):
        """Web route to switch language and redirect user back to previous page."""
        cleanLang = "spa" if str(lang).lower().startswith("sp") else "eng"
        session["idioma"] = cleanLang
        session["lang"] = cleanLang
        referrer = request.referrer or url_for("renderMapScreen")
        return redirect(referrer)

    @app.route("/api/i18n/set-language/<lang>", methods=["GET", "POST"])
    def apiSetLanguage(lang: str):
        """API route to dynamically update language in user session."""
        cleanLang = "spa" if str(lang).lower().startswith("sp") else "eng"
        session["idioma"] = cleanLang
        session["lang"] = cleanLang
        return jsonify({
            "success": True,
            "language": cleanLang,
            "message": f"Language switched to {cleanLang}."
        }), 200

    @app.route("/api/i18n/translations/<lang>", methods=["GET"])
    def apiGetTranslations(lang: str):
        """Returns translation dictionary for client-side JavaScript rendering."""
        cleanLang = "spa" if str(lang).lower().startswith("sp") else "eng"
        i18nMgr = I18nManager.getInstance()
        return jsonify({
            "success": True,
            "language": cleanLang,
            "translations": i18nMgr.translations.get(cleanLang, {})
        }), 200

    # ==========================================================================
    # HEALTH CHECK & ERROR HANDLERS
    # ==========================================================================

    @app.route("/api/health", methods=["GET"])
    def healthCheck():
        """Health check probe endpoint for uptime monitoring."""
        return jsonify({
            "status": "healthy",
            "system": "JaguarFind & JaguarMaps UAM",
            "version": "2.0.0",
            "current_language": get_current_language(),
            "endpoints": [
                "/api/auth",
                "/api/map",
                "/api/lost-found-object",
                "/api/admin",
            ],
        }), 200

    @app.errorhandler(404)
    def notFound(error):
        if request.path.startswith("/api/"):
            return jsonify({
                "success": False,
                "error": "Requested API endpoint not found.",
                "path": request.path,
            }), 404
        return render_template("mapScreen.html"), 404

    @app.errorhandler(500)
    def internalServerError(error):
        return jsonify({
            "success": False,
            "error": "An internal server error occurred.",
        }), 500

    return app


app = createApp()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
