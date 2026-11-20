# Reglas de Modelado y Topología del Grafo / Campus Graph Modeling Rules
**JaguarFind & JaguarMaps — Universidad Americana (UAM)**  
*Especificación de Criterios de Ingeniería, Seguridad Física, Granularidad y Topología*

---

<details open>
<summary><b> Versión en Español (Reglas Oficiales del Sistema)</b></summary>

## 1. Propósito del Documento
Este documento establece las **reglas normativas y criterios de ingeniería** que rigen la construcción, granularidad y mantenimiento del **Grafo Ponderado, Dirigido y No Completo** del campus de la UAM. Estas reglas resuelven dilemas de precisión, accesibilidad, bioseguridad y rendimiento computacional para el motor de navegación peatonal (Dijkstra) y el plano interactivo.

---

## 2. Decálogo de Reglas de Modelado

### Regla 1: Abstracción de Perímetro en Áreas Restringidas (*The Gateway Pattern*)
* **Criterio:** Queda **estrictamente descartado** el levantamiento cartográfico y la creación de nodos internos dentro de zonas de acceso restringido, clínicas asistenciales, quirófanos, áreas estériles o cuartos técnicos de alta seguridad.
* **Espacios Aplicables:**
  * **Edificio N (Clínicas Odontológicas):** Quirófanos 1-2, esterilización, radiología, tomografía y cubículos clínicos.
  * **Edificio H:** Laboratorios de simulación médica y áreas biológicas.
  * **Edificio C / O:** Cuartos de servidores (*datacenters*), armarios de telecomunicaciones (IDF/MDF) y subestaciones eléctricas.
* **Mecanismo de Resolución (*Gateway*):**
  1. El grafo únicamente modela hasta el **Punto de Control Público / Recepción** (ej. `EDIF_N_RECEPTION`).
  2. Cuando el usuario busca términos sensibles (*"quirófano dental"*, *"esterilización"*, *"rayos x"*), el `DestinationResolver` enruta al nodo público de recepción.
  3. Al llegar a la recepción, el sistema emite una notificación de perímetro:  
     > *"Has llegado a la Recepción del Edificio N (Clínicas Odontológicas). El ingreso a cubículos clínicos y quirófanos requiere uniforme estéril y autorización docente."*
* **Justificación de Ingeniería:** Cumplimiento de normas de bioseguridad, protección de la privacidad de los pacientes atendidos en la UAM y prevención del ingreso de visitantes no autorizados a áreas críticas.

---

### Regla 2: Granularidad de Accesos por Tipo de Espacio (*Regla de Puertas*)
* **Criterio A (Aulas y Salones Estándar - 1 Sola Puerta):**
  * Para las aulas convencionales (ej. `B-101` a `B-106`, `C-102` a `C-106`, `M-201`, etc.), **se mapea una única puerta física** (la puerta frontal / principal más próxima al pasillo o rampa).
  * *Justificación:* La distancia entre puertas delantera y trasera en un aula estándar es de $6\text{ a }8\text{ metros}$, magnitud irrelevante frente al margen de error natural del GPS ($3\text{ a }5\text{ metros}$) y a caminatas de campus de cientos de metros. Evita duplicar innecesariamente la cardinalidad de vértices ($|V|$) y elimina ambigüedades en la búsqueda de Dijkstra.
* **Criterio B (Macro-Espacios y Auditorios - Múltiples Accesos Diferenciados):**
  * Para recintos de alta concurrencia con accesos separados por más de $25\text{ metros}$ o situados en fachadas opuestas, **se mapean accesos independientes**:
    * **Auditorio Central (Edificio G):** `EDIF_G_DOOR_MAIN` (Lobby central) y `EDIF_G_DOOR_SIDE` (Parqueo este).
    * **Jaguar Center / Polideportivo:** `JAGUAR_CTR_NORTH` (Canchas) y `JAGUAR_CTR_SOUTH` (Estacionamiento).
    * **Cafetería Central (Edificio K):** Acceso Plaza Chilamates y Acceso Edificio A.
* **Criterio C (Accesibilidad Inclusiva ♿):**
  * Si un edificio posee un acceso con escaleras y otro con rampa a nivel, ambos deben modelarse como aristas dirigidas diferenciadas, asignando `isAccessible = True` exclusivamente a la rampa.

---

### Regla 3: Modelo Híbrido Macro vs. Micro-Navegación (*GPS vs. Plano Cartesiano*)
* **Criterio A (Macro-Navegación Exterior - GPS Real):**
  * Se asigna latitud y longitud geodésica real (WGS84) a **todos los accesos de edificios, casetas QR, canchas, plazas y bifurcaciones de andenes peatonales exteriores**.
  * Permite autolocalización con `watchPosition()`, cálculo de distancia euclidiana/Haversine y detección de desvío de ruta (*rerouting* dinámico).
* **Criterio B (Micro-Navegación Interior - Plano Cartesiano + Pisos):**
  * Dentro de los edificios, **no se confía en la señal satelital GPS** debido a la atenuación de techos de concreto (*multipath jitter*) y a la incapacidad del GPS móvil para discriminar el eje vertical $Z$ (pisos).
  * La navegación interior se modela mediante:
    1. Coordenadas cartesianas relativas ($x\%, y\%$ en el lienzo SVG).
    2. Nivel de piso (`floorLevel`: 1, 2, 3, etc.).
    3. Instrucciones descriptivas de pasillo para la Web Speech API (*"Sube por las escaleras al Piso 2 y camina 12 metros al fondo a la derecha"*).

---

### Regla 4: Propiedades Formales del Grafo ($G = (V, E, W)$)
1. **Grafo Ponderado ($W: E \to \mathbb{R}^+$):**
   * Cada arista almacena un peso no negativo $w > 0$ correspondiente a la **distancia caminada real en metros** sobre el pavimento o acera (prohibido usar distancia aérea euclidiana entre nodos que no tengan camino físico).
2. **Grafo Dirigido ($E \subseteq V \times V$):**
   * Toda conexión peatonal ordinaria se implementa mediante **dos aristas dirigidas opuestas**: $(u \to v)$ y $(v \to u)$ con el mismo peso métrico.
   * Permite incorporar restricciones direccionales reales (ej. torniquetes unidireccionales de entrada o salidas de emergencia exclusivas).
3. **Grafo No Completo ($|E| \ll |V|(|V|-1)$):**
   * La topología es dispersa. Solo existen aristas entre nodos físicos físicamente contiguos y transitables.

---

### Regla 5: Estándar de Código, Nomenclatura y `camelCase`
* Todo el código fuente del motor de grafos debe escribirse en **idioma inglés** y bajo convención estricta **`camelCase`** para métodos, variables y atributos:
  * Identificadores de nodo: `nodeId` (ej. `"EDIF_A"`, `"PARQUEO_PPAL"`).
  * Propiedades de arista: `sourceNodeId`, `targetNodeId`, `distanceMeters`, `isAccessible`, `stepInstruction`.
  * Propiedades de nodo: `category`, `xPercent`, `yPercent`, `latitude`, `longitude`, `accessLevel`, `accessNotice`.
  * Métodos de enrutamiento: `findShortestPath()`, `resolveDestination()`, `findNearestNodeByGps()`.

---

## 3. Resumen de Argumentación para la Defensa ante el Jurado

| Decisión Tomada | Justificación Técnica ante Preguntas del Jurado |
| :--- | :--- |
| **¿Por qué no mapearon los cubículos dentales del Edificio N?** | *"Implementamos el **Gateway Pattern**: por bioseguridad, privacidad de pacientes y control de acceso hospitalario, los mapas peatonales guían al usuario hasta el punto de recepción y registro público, evitando intrusiones en zonas clínicas estériles."* |
| **¿Por qué una sola puerta en aulas normales?** | *"A escala de campus, 6 metros entre puertas delantera y trasera caen dentro del margen de error natural del GPS (3-5 m). Modelar dos puertas duplicaría los vértices sin beneficio perceptible para el estudiante."* |
| **¿Por qué no usar GPS dentro de los salones del segundo piso?** | *"El GPS civil carece de resolución vertical para pisos ($Z$) y sufre atenuación por concreto (*indoor multipath*). Usamos un modelo híbrido: GPS en exteriores y coordenadas cartesianas relativas con instrucciones de pasillo en interiores."* |

</details>

---

<details open>
<summary><b>English Version (Official System Architectural Rules)</b></summary>

## 1. Document Scope
This document sets forth the **formal architectural and engineering rules** governing the construction, granularity, and maintenance of the **Weighted, Directed, and Non-Complete Graph** for the UAM Campus.

---

## 2. Core Graph Modeling Rules

### Rule 1: Perimeter Abstraction for Restricted Areas (*The Gateway Pattern*)
* **Rule:** Internal rooms within restricted clinical, medical, surgical, or high-security utility areas **must not be mapped as individual internal nodes**.
* **Target Areas:**
  * **Building N (Dental Clinics):** Operating rooms 1-2, sterilization room, clinical cubicles, dental X-ray/CT rooms.
  * **Building H:** Medical simulation labs and anatomical biology suites.
  * **Buildings C & O:** Central server rooms (*datacenters*), telecommunication closets (MDF/IDF), and electrical substations.
* **Resolution Strategy (*Gateway Pattern*):**
  1. The graph maps strictly up to the **Public Front Desk / Reception Node** (e.g., `EDIF_N_RECEPTION`).
  2. Clinical search queries (*"dental operating room"*, *"sterilization"*) resolve directly to the reception node.
  3. Upon arrival, an automated access perimeter notice is presented to the user.

### Rule 2: Access Point Granularity (*Single vs. Multi-Door Policy*)
* **Standard Classrooms (Single Access Door):**
  * Routine classrooms (`B-101` to `B-106`, `C-102` to `C-106`, etc.) register **only one primary physical door** (the main entry closest to the central hallway or ramp).
  * Distances of $6\text{ to }8\text{ meters}$ between front and rear doors are negligible compared to standard campus walks ($100\text{ to }400\text{ m}$) and GPS variance ($3\text{ to }5\text{ m}$).
* **Large Venues & Auditoriums (Distinct Multi-Access Nodes):**
  * High-capacity facilities separated by $> 25\text{ meters}$ register distinct access points (e.g., `AUD_CENTRAL_MAIN` vs. `AUD_CENTRAL_PARKING`).
* **Universal Accessibility (♿ Wheelchair Policy):**
  * Walkways featuring stairs vs. grade-level ramps are split into separate directed edges with `isAccessible = True` designated exclusively on ramps.

### Rule 3: Hybrid Navigation Model (*Outdoor GPS vs. Indoor Cartesian Coordinates*)
* **Macro-Navigation (Outdoor Campus):**
  * Driven by real-world geodetic coordinates (WGS84 `latitude`, `longitude`) along pedestrian paths, gateways, and building portals.
* **Micro-Navigation (Indoor Facilities & Multi-Story Buildings):**
  * Driven by relative Cartesian coordinates ($x\%, y\%$ on SVG canvas), discrete vertical levels (`floorLevel`), and step-by-step corridor speech instructions, mitigating satellite attenuation and vertical drift.

### Rule 4: Formal Graph Theory Specifications ($G = (V, E, W)$)
* **Weighted ($W: E \to \mathbb{R}^+$):** Weights denote real physical walking distance in meters.
* **Directed ($E \subseteq V \times V$):** Bidirectional walkways are modeled as pairs of antiparallel directed edges: $(u \to v)$ and $(v \to u)$.
* **Non-Complete ($|E| \ll |V|^2$):** Sparse adjacency structure representing solely authentic, walkable ground pathways.

### Rule 5: Coding Standards & `camelCase`
* All classes, algorithms, database models, and API payloads must be coded in **English** using **`camelCase`** conventions.

</details>
