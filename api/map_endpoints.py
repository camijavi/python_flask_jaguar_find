"""
api/map_endpoints.py
================================================================================
ENDPOINTS RESTFUL PARA CARTOGRAFÍA, RUTAS DIJKSTRA Y GEOLOCALIZACIÓN
================================================================================

Propósito del Archivo:
----------------------
Expone los servicios web JSON consumidos de forma asíncrona por el frontend
interactivo del mapa (mapaInteractivo.js) y el sintetizador de voz (ttsHelper.js).

Endpoints que van en este archivo:
---------------------------------
1. POST /api/ruta:
   - Entrada JSON:
     {
       "origen": "GATE_1",
       "destino": "B_103",
       "accesible": true  // Opcional: filtro para personas con movilidad reducida / silla de ruedas ♿
     }
   - Proceso:
     Ejecuta el algoritmo de Dijkstra sobre la instancia del TDA GrafoUam.
   - Salida JSON:
     {
       "exito": true,
       "distanciaMetros": 185.5,
       "tiempoSegundos": 140,
       "nodos": [{"id": "GATE_1", "x": 80, "y": 240}, ...],
       "pasosVoz": [
         "Inicia en la Caseta 1 Rotonda Principal.",
         "Avanza 75 metros hacia la recepción del Edificio A.",
         "Gira a la izquierda hacia el Edificio B.",
         "Has llegado a tu destino: Aula B-103."
       ]
     }

2. GET /api/puntos:
   - Retorna la lista completa de nodos físicos del campus organizados por categorías:
     * Casetas de Entrada QR (GATE_1, GATE_2, GATE_3).
     * Aulas Edificio B (B-101 a B-106 de izquierda a derecha).
     * Servicios sanitarios (Baño Hombres, Baño Mujeres).
     * Clínicas Odontológicas (FODO).
     * Cafeterías, Gimnasio y Áreas comunes.
   - Cada nodo incluye identificador, nombre descriptivo y coordenadas SVG (x, y).

3. POST /api/gps-cercano:
   - Entrada JSON:
     {
       "lat": 12.12456,
       "lng": -86.26845
     }
   - Proceso:
     Calcula mediante la fórmula trigonométrica de Haversine la distancia esférica
     entre la posición GPS del usuario y todos los vértices del grafo.
   - Salida JSON:
     Retorna el nodo más cercano para sugerir automáticamente el punto de partida.
"""

# Aquí se implementan los controladores POST /api/ruta, GET /api/puntos y POST /api/gps-cercano.
