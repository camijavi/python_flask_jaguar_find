"""
auth/__init__.py
================================================================================
INICIALIZACIÓN DEL BLUEPRINT DE AUTENTICACIÓN
================================================================================

Propósito del Archivo:
----------------------
Crea y expone la instancia 'auth_bp' de Blueprint de Flask asociada al prefijo
de ruta '/auth', desacoplando los controladores y vistas de login, registro
y administración de sesiones.

Contenido que va en este archivo:
--------------------------------
1. Creación del Blueprint:
   auth_bp = Blueprint('auth', __name__, template_folder='../templates')

2. Importación diferida de las rutas:
   from . import routes
   (para registrar los controladores asociados a este Blueprint sin generar importaciones circulares).
"""

# Aquí se define e instancia el Blueprint auth_bp y se importan sus rutas.
