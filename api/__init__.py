"""
api/__init__.py
================================================================================
INICIALIZACIÓN DEL BLUEPRINT DE SERVICIOS WEB RESTFUL (/API)
================================================================================

Propósito del Archivo:
----------------------
Crea y expone la instancia 'api_bp' de Blueprint de Flask asociada al prefijo
de ruta '/api', proveyendo una arquitectura desacoplada para el consumo asíncrono
(fetch / AJAX) desde el frontend y potenciales aplicaciones móviles institucionales.

Contenido que va en este archivo:
--------------------------------
1. Creación del Blueprint:
   api_bp = Blueprint('api', __name__)

2. Importación y registro de los submódulos de endpoints:
   - from . import routes
   - from . import map_endpoints
   - from . import lost_found_endpoints
   - from . import common_endpoints
"""

# Aquí se define e instancia el Blueprint api_bp y se registran sus submódulos de endpoints.
