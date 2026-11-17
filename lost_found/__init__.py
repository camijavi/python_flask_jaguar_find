"""
lost_found/__init__.py
================================================================================
INICIALIZACIÓN DEL BLUEPRINT DE GESTIÓN DE OBJETOS PERDIDOS Y CUSTODIA
================================================================================

Propósito del Archivo:
----------------------
Crea y expone la instancia 'lost_found_bp' de Blueprint de Flask asociada al prefijo
de ruta '/lost-found', gestionando el catálogo público, el formulario de reporte de
pertenencias, el panel de custodia del Edificio A y la administración de usuarios y roles.

Contenido que va en este archivo:
--------------------------------
1. Creación del Blueprint:
   lost_found_bp = Blueprint('lost_found', __name__, template_folder='../templates')

2. Importación diferida de las rutas:
   from . import routes
"""

# Aquí se define e instancia el Blueprint lost_found_bp y se importan sus rutas.
