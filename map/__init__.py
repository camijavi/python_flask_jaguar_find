"""
map/__init__.py
================================================================================
INICIALIZACIÓN DEL BLUEPRINT DEL NAVEGADOR PEATONAL (JAGUARMAPS)
================================================================================

Propósito del Archivo:
----------------------
Crea y expone la instancia 'map_bp' de Blueprint de Flask para las rutas del mapa
interactivo, el cálculo de rutas peatonales, la visualización de casetas QR y la
proyección de pines georreferenciados de objetos perdidos sobre el campus de la UAM.

Contenido que va en este archivo:
--------------------------------
1. Creación del Blueprint:
   map_bp = Blueprint('map', __name__, template_folder='../templates')

2. Importación diferida de las rutas:
   from . import routes
"""

# Aquí se define e instancia el Blueprint map_bp y se importan sus rutas.
