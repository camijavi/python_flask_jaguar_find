# JaguarFind — Documentation Portal / Centro de Documentación
**Universidad Americana (UAM) • Structured Programming / Programación Estructurada**

---

Bienvenido al centro de documentación oficial del proyecto **JaguarFind**. 
Para mantener la máxima simplicidad y orden, cada archivo posee su título en **Inglés** y contiene su información completa tanto en **Español** como en **Inglés** mediante bloques desplegables interactivos.

Welcome to the official **JaguarFind** documentation portal. 
Each file has its title in **English** and contains the full information in both **Spanish** and **English** using interactive toggleable blocks.

---

### Project Documentation Files / Archivos de Documentación

1. **[GENERAL_JAGUARFIND.md](file:///Users/camijavi/Projects/python/python_flask_jaguar_find/docs/GENERAL_JAGUARFIND.md)**
 * **ES:** Visión general, contexto institucional UAM (semestres, eventos, visitantes, clínicas y facultades), planteamiento de los dos problemas, modelo matemático del Grafo y justificación de Dijkstra.
 * **EN:** System overview, UAM institutional dynamics (semesters, visitor profiles, clinics, and faculties), the two core problems, and mathematical graph modeling.

2. **[CAMPUS_MAP.md](file:///Users/camijavi/Projects/python/python_flask_jaguar_find/docs/CAMPUS_MAP.md)**
 * **ES:** Módulo de navegación peatonal (Google Maps UAM), acceso público sin registro, Códigos QR en las 3 entradas al campus, aulas piso por piso (B-101 a B-106 de izquierda a derecha), baños en pasillo, rampas accesibles y síntesis de voz con Web Speech API nativa.
 * **EN:** Campus wayfinding subsystem, public access, QR codes at all 3 campus gates, floor-by-floor classrooms (B-101 to B-106), corridor restrooms, accessible ramps , and native browser Web Speech API.

3. **[LOST_AND_FOUND.md](file:///Users/camijavi/Projects/python/python_flask_jaguar_find/docs/LOST_AND_FOUND.md)**
 * **ES:** Módulo de objetos perdidos, autenticación institucional con correo `@uamv.edu.ni`, roles (**Estudiante** con soporte para doble titulación, **Colaborador** con cédula, **Administrador** con panel de delegación y creación de usuarios), ciclo de 3 estados, regla antifraude y SQLite3.
 * **EN:** Lost & Found management, institutional authentication (`@uamv.edu.ni`), user roles (Student with double degree support, Collaborator, Admin with delegation panel), 3-state custody lifecycle, anti-fraud secret rule, and SQLite3 schema.

4. **[TEAM_PLANNING.md](file:///Users/camijavi/Projects/python/python_flask_jaguar_find/docs/TEAM_PLANNING.md)**
 * **ES:** Organización del equipo (Camila, Francis, James y Elias), paquetes de trabajo, matriz RACI y cronograma de desarrollo día a día de 12 días en formato tabular y diagrama de flujo.
 * **EN:** Team role allocation, WBS work packages, RACI matrix, and 12-day day-by-day development roadmap.

5. **[GRAPH_MAPPING_RULES.md](file:///Users/camijavi/Projects/python/python_flask_jaguar_find/docs/GRAPH_MAPPING_RULES.md)**
 * **ES:** Reglas y criterios oficiales de modelado topológico: abstracción de perímetro en áreas restringidas (Gateway Pattern para Edificio N Odontología y laboratorios), política de 1 sola puerta en aulas vs. accesos múltiples en auditorios, modelo híbrido (GPS exterior vs. plano cartesiano/pisos interior) y argumentos de defensa ante el jurado.
 * **EN:** Official topological modeling rules: perimeter abstraction in restricted zones (Gateway Pattern for Building N Dental Clinics & labs), single-door vs. multi-door policy, hybrid navigation model (outdoor GPS vs. indoor Cartesian canvas/floors), and defense talking points.

6. **[GRAPH_STRUCTURES.md](file:///Users/camijavi/Projects/python/python_flask_jaguar_find/docs/GRAPH_STRUCTURES.md)**
 * **ES:** Documentación completa de las 20 estructuras de grafos dirigidos, ponderados y no completos unificadas sobre `graph_combined.py` (1 Macro + 1 Red Peatonal + 18 Subgrafos de Edificios), inventario exacto de nodos/aristas, resumen de mejoras y gráfico visual completo (`campus_graphs_diagram.svg`).
 * **EN:** Complete documentation of all 20 weighted, directed, non-complete graph structures unified on `graph_combined.py` (1 Macro + 1 Pedestrian Walkway + 18 Building Subgraphs), exact vertex/edge inventory, summary of improvements, and full vector visual graphic (`campus_graphs_diagram.svg`).

---

### Modular Codebase Architecture / Estructura Modular del Proyecto

La aplicación Flask se encuentra subdividida en paquetes independientes y modulares:

* **Entrypoint & Config:** [`app.py`](file:///Users/camijavi/Projects/python/python_flask_jaguar_find/app.py) • [`config.py`](file:///Users/camijavi/Projects/python/python_flask_jaguar_find/config.py) • [`database.py`](file:///Users/camijavi/Projects/python/python_flask_jaguar_find/database.py)
* **Pure Python Graph ADT:** [`graphUam.py`](file:///Users/camijavi/Projects/python/python_flask_jaguar_find/graphUam.py) (Dijkstra $O((V+E)\log V)$ con `heapq` y Haversine)
* **Auth Subsystem:** [`auth/routes.py`](file:///Users/camijavi/Projects/python/python_flask_jaguar_find/auth/routes.py) • [`auth/services.py`](file:///Users/camijavi/Projects/python/python_flask_jaguar_find/auth/services.py) • [`auth/models.py`](file:///Users/camijavi/Projects/python/python_flask_jaguar_find/auth/models.py)
* **Campus Wayfinding:** [`map/routes.py`](file:///Users/camijavi/Projects/python/python_flask_jaguar_find/map/routes.py) • [`map/services.py`](file:///Users/camijavi/Projects/python/python_flask_jaguar_find/map/services.py)
* **Lost & Found:** [`lost_found/routes.py`](file:///Users/camijavi/Projects/python/python_flask_jaguar_find/lost_found/routes.py) • [`lost_found/services.py`](file:///Users/camijavi/Projects/python/python_flask_jaguar_find/lost_found/services.py) • [`lost_found/models.py`](file:///Users/camijavi/Projects/python/python_flask_jaguar_find/lost_found/models.py)
* **REST API Endpoints:** [`api/routes.py`](file:///Users/camijavi/Projects/python/python_flask_jaguar_find/api/routes.py) • [`api/map_endpoints.py`](file:///Users/camijavi/Projects/python/python_flask_jaguar_find/api/map_endpoints.py) • [`api/lost_found_endpoints.py`](file:///Users/camijavi/Projects/python/python_flask_jaguar_find/api/lost_found_endpoints.py) • [`api/common_endpoints.py`](file:///Users/camijavi/Projects/python/python_flask_jaguar_find/api/common_endpoints.py)
* **Internationalization:** [`languages/spa.json`](file:///Users/camijavi/Projects/python/python_flask_jaguar_find/languages/spa.json) • [`languages/eng.json`](file:///Users/camijavi/Projects/python/python_flask_jaguar_find/languages/eng.json)
* **Frontend Templates:** [`templates/base.html`](file:///Users/camijavi/Projects/python/python_flask_jaguar_find/templates/base.html) • [`templates/map/index.html`](file:///Users/camijavi/Projects/python/python_flask_jaguar_find/templates/map/index.html) • [`templates/auth/`](file:///Users/camijavi/Projects/python/python_flask_jaguar_find/templates/auth/) • [`templates/lost_found/`](file:///Users/camijavi/Projects/python/python_flask_jaguar_find/templates/lost_found/)
* **Static Assets:** [`static/js/mapaInteractivo.js`](file:///Users/camijavi/Projects/python/python_flask_jaguar_find/static/js/mapaInteractivo.js) • [`static/js/ttsHelper.js`](file:///Users/camijavi/Projects/python/python_flask_jaguar_find/static/js/ttsHelper.js) • [`static/css/styles.css`](file:///Users/camijavi/Projects/python/python_flask_jaguar_find/static/css/styles.css)
