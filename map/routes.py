"""
map/routes.py
================================================================================
ENRUTADOR Y CONTROLADORES DE NAVEGACIÓN PEATONAL Y CÓDIGOS QR
================================================================================

Propósito del Archivo:
----------------------
Define los controladores de vistas públicas para el módulo de mapas (JaguarMaps).
No exige autenticación previa, permitiendo que cualquier visitante, padre de familia,
paciente de clínicas odontológicas o estudiante consulte el plano, genere rutas
óptimas o acceda de forma inmediata al escanear los códigos QR físicos colocados en
las 3 entradas del campus.

Rutas y Lógica que van en este archivo:
--------------------------------------
1. GET / y GET /mapa:
   - Renderiza la plantilla principal 'map/index.html'.
   - Pasa al frontend la lista de puntos de interés (POIs), categorías y casetas de entrada.
   - Pasa la lista de pines de objetos activos (REPORTADO y VERIFICADO) para que el plano
     SVG dibuje los marcadores georreferenciados (📍) sobre los nodos físicos.
   - Habilita la interfaz accesible con selector de rutas inclusivas en silla de ruedas ♿
     y el botón de guía por voz (Web Speech API).

2. GET /qr/<puntoId>:
   - Endpoint de escaneo de Código QR físico en las casetas de entrada:
     * /qr/GATE_1: Caseta 1 (Rotonda Principal).
     * /qr/GATE_2: Caseta 2 (Acceso Noreste).
     * /qr/GATE_3: Caseta 3 (Acceso Norte Copérnico).
   - Valida que 'puntoId' exista como nodo válido en el grafo del campus.
   - Redirige al mapa principal (/mapa?origen=GATE_X), precargando automáticamente
     dicha caseta como el punto de partida del usuario para resolver el problema de desorientación.
"""

# Aquí se implementan los controladores @map_bp.route("/") y @map_bp.route("/qr/<puntoId>"),
# interactuando con services.py de map y el Grafo UAM.
