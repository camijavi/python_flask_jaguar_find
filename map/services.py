"""
map/services.py
================================================================================
SERVICIOS DE NEGOCIO PARA CARTOGRAFÍA, RUTAS Y PINES GEORREFERENCIADOS
================================================================================

Propósito del Archivo:
----------------------
Encapsula la lógica auxiliar para la manipulación del grafo del campus, la agrupación
de puntos de interés (POIs), la integración de los objetos perdidos como pines en el mapa
y la estructuración de respuestas cartográficas legibles tanto para la interfaz SVG
como para el sintetizador de voz.

Funciones y Servicios que van en este archivo:
---------------------------------------------
1. obtenerPuntosAgrupadosPorCategoria():
   - Consulta los nodos registrados en 'grafoUam.py'.
   - Agrupa los destinos por categorías institucionales:
     * Casetas de Entrada (QR)
     * Aulas Edificio B (B-101 a B-106)
     * Baños (Hombres / Mujeres)
     * Clínicas Odontológicas (FODO)
     * Edificio A (Custodia y Administración)
     * Cafeterías y Áreas de Comida
     * Deportes y Gimnasio
   - Retorna la estructura para poblar los elementos <select> de origen y destino en el frontend.

2. obtenerPinesDeObjetosParaMapa():
   - Consulta a la base de datos los artículos en estado 'REPORTADO' o 'VERIFICADO'.
   - Asocia cada artículo con las coordenadas SVG (x, y) del nodo donde fue reportado o custodiado.
   - Retorna una lista de pines georreferenciados (📍) con metadatos sanitizados (título, categoría,
     lugar, fecha) aislando totalmente cualquier detalle confidencial antifraude.

3. calcularRutaPeatonal(origenId, destinoId, accesible=False):
   - Invoca el algoritmo de Dijkstra en la instancia de GrafoUam.
   - Retorna un diccionario con:
     * nodos: Coordenadas secuenciales (x, y) para dibujar la polilínea vectorial SVG animada.
     * distanciaMetros: Distancia total a pie.
     * tiempoEstimadoSegundos: Tiempo de caminata a velocidad peatonal media.
     * pasosVoz: Lista de instrucciones descriptivas en texto para la Web Speech API.
"""

# Aquí se implementan las funciones obtenerPuntosAgrupadosPorCategoria(),
# obtenerPinesDeObjetosParaMapa() y calcularRutaPeatonal().
