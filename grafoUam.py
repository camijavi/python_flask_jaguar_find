"""
grafoUam.py
================================================================================
TDA GRAFO PONDERADO DEL CAMPUS UAM Y ALGORITMO DE DIJKSTRA
================================================================================

Propósito del Archivo:
----------------------
Modela la topología peatonal completa del campus universitario de la UAM como un
Grafo Ponderado G = (V, E) en Python puro. Provee el cálculo de rutas óptimas mediante
el Algoritmo de Dijkstra con cola de prioridad binaria (heapq), filtrado de accesibilidad
en silla de ruedas (♿), generación de instrucciones paso a paso para la Web Speech API
y anclaje georreferenciado para proyectar pines de objetos ubicados sobre los nodos físicos.

Estructuras de Datos y Clases que van en este archivo:
-----------------------------------------------------
1. Clase 'Nodo':
   - id: Identificador único del nodo físico (ej. 'GATE_1', 'B_101', 'A_CAFETERIA', 'CLINICAS_FODO').
   - nombre: Nombre descriptivo en lenguaje natural (ej. 'Aula B-103 - Edificio B').
   - categoria: Tipo de instalación ('ENTRADA_QR', 'AULA', 'BANO_H', 'BANO_M', 'CLINICA', 'CAFETERIA', 'PARQUEO', 'GIMNASIO').
   - x, y: Coordenadas cartesianas en el plano vectorial SVG del campus.
   - lat, lng: Coordenadas geodésicas GPS para cálculo Haversine de cercanía.

2. Clase 'Arista':
   - origenId, destinoId: Nodos adyacentes conectados por un tramo peatonal transitable.
   - distanciaMetros: Peso métrico w(u,v) de la caminata a pie.
   - esRutaAccesible: Booleano que indica si el tramo carece de escalones o desniveles (rampa apta para silla de ruedas ♿).
   - descripcionPaso: Texto explicativo para orientación humana y síntesis de voz
     (ej. 'Avanza 15 metros recto por el pasillo del Edificio B hacia el aula B-103').

3. Clase 'GrafoUam':
   - adyacencias: Diccionario {nodoId: [Arista, ...]}.
   - nodos: Diccionario {nodoId: Nodo}.
   - agregarNodo(nodo): Registra un vértice en el grafo.
   - agregarArista(u, v, distancia, accesible, descripcion, bidireccional=True): Conecta dos nodos.

Algoritmos y Métodos Principales:
--------------------------------
- dijkstra(origenId, destinoId, soloAccesible=False):
  - Inicializa distancias en infinito y montículo binario (heapq) en O((V+E)log V).
  - Si soloAccesible es True, descarta en tiempo de exploración toda arista con esRutaAccesible == False.
  - Reconstruye la ruta óptima de nodos predecesores, distancia total acumulada y tiempo estimado a pie.

- generarInstruccionesVoz(rutaNodos):
  - Traduce la secuencia de nodos y aristas en frases secuenciales legibles
    para alimentar el sintetizador de voz nativo del navegador (Web Speech API).

- encontrarNodoMasCercanoGps(lat, lng):
  - Aplica la fórmula de Haversine para determinar el nodo de entrada o edificio
    más próximo a las coordenadas del usuario.

Nodos y Puntos Clave del Campus UAM Representados:
-------------------------------------------------
- Casetas de Entrada con Códigos QR:
  * GATE_1: Rotonda Principal (Entrada 1).
  * GATE_2: Acceso Noreste (Entrada 2).
  * GATE_3: Acceso Norte Copérnico (Entrada 3).
- Edificio A:
  * Recepción Central y Oficina de Custodia de Objetos Perdidos.
  * Cafetería Central del Edificio A.
- Edificio B (Planta Baja y Pasillo Principal):
  * Aulas B-101 a B-106 (distribuidas ordenadamente de izquierda a derecha).
  * Baño de Mujeres y Baño de Hombres del Edificio B.
- Otras Instalaciones Clave:
  * Plaza Central UAM.
  * Clínicas Odontológicas (Facultad de Odontología - FODO).
  * Facultad de Ingeniería y Arquitectura (FIA).
  * Polideportivo / Gimnasio y Canchas.
  * Rampas de acceso y pasos peatonales inclusivos ♿.
"""

# Aquí se implementan las clases Nodo, Arista, GrafoUam, el algoritmo de Dijkstra
# con cola de prioridad heapq, la fórmula de Haversine y el generador de pasos de voz.
