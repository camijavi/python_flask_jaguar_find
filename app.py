"""
app.py
================================================================================
FLASK APPLICATION ENTRY POINT & WSGI SERVER
================================================================================
Exposes the main application instance configured from backend.app.createApp().
Can be launched directly via `python app.py` or through WSGI servers like Gunicorn.
"""

from backend.app import createApp, app

if __name__ == "__main__":
    print(" Starting JaguarFind & JaguarMaps Development Server...")
    print(" Interactive Map: http://localhost:5000/api/map/nodes")
    print(" Lost & Found:   http://localhost:5000/api/lost-found-object/items")
    print(" Auth:           http://localhost:5000/api/auth/me")
    print(" Admin:          http://localhost:5000/api/admin/stats")
    app.run(host="0.0.0.0", port=5000, debug=True)
