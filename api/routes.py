"""
api/routes.py
================================================================================
ENRUTADOR CENTRAL Y RAÍZ DE LA API RESTFUL (/API)
================================================================================

Propósito del Archivo:
----------------------
Punto de agregación central para las rutas del API. Define la respuesta base
del índice de la API, la especificación de versión y la documentación de
los endpoints disponibles en formato JSON.

Rutas que van en este archivo:
-----------------------------
1. GET /api:
   - Retorna un diccionario JSON informativo con la versión de la API (v1.0),
     el estado del servicio y el mapa de recursos accesibles:
     * /api/ruta (Cálculo de rutas Dijkstra)
     * /api/puntos (Puntos de interés del campus)
     * /api/gps-cercano (Nodo más próximo por Haversine)
     * /api/objetos (Catálogo filtrado por Lugar y Fecha)
     * /api/pines-mapa (Pines de objetos sobre el grafo)
     * /api/idioma/<lang> (Sincronización i18n)
     * /api/status (Healthcheck)
"""

# Aquí se implementa el controlador @api_bp.route("/") que documenta los endpoints del sistema.
