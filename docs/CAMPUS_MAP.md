# Campus Map & Navigation / Módulo de Navegación y Mapa del Campus

---

<details open>
<summary><b>🇪🇸 Versión en Español</b></summary>

### 1. Propósito y Acceso 100% Público
El módulo de mapa de **JaguarFind** opera como un "Google Maps" peatonal del campus de la UAM:
* **Sin Registro:** Los visitantes y estudiantes pueden consultar el mapa, buscar destinos y calcular rutas sin crear cuentas ni iniciar sesión.
* **Cobertura en las Tres Entradas del Campus:**  
  Dado que los mapas físicos de la UAM están ubicados solo cerca de los Edificios A y B, se despliegan Códigos QR en los 3 accesos:
  1. **Entrada Principal (Sur / Parqueo Principal):** `https://.../mapa?origen=PARQUEO_PPAL`
  2. **Segundo Acceso (Noreste / Campos Deportivos):** `https://.../mapa?origen=SEGUNDO_ACCESO`
  3. **Tercer Acceso (Norte / Copérnico y FIA):** `https://.../mapa?origen=TERCER_ACCESO`

---

### 2. Catálogo Ultra-Fino de Nodos y Puntos de Interés (POIs)
1. **Aulas Piso por Piso:**
   * **Edificio B (Primer Piso):** Aulas `B-101`, `B-102`, `B-103`, `B-104`, `B-105` y `B-106` ordenadas de izquierda a derecha. Módulo Comercial 1 y Fotocopiadora Jaguar Shop al final del pasillo.
   * **Edificio B (Segundo Piso):** Aulas `B-201` a `B-210`.
   * **Edificio C (Primer Piso):** Auditorio C-101, Aulas `C-102` a `C-106`, Auditorio C-109 y Caja Central de Tesorería.
   * **Edificio C (Segundo Piso):** Laboratorios MAC C-107 y C-203, Lab Acai-Erasmus+, Laboratorios C-201 a C-205.
   * **Edificio P (Copérnico):** Estación Meteorológica, Aulas `P-101` a `P-401`, Talleres de Arquitectura y Observatorio Astronómico Copérnico (Piso 5).
2. **Servicios Higiénicos (Baños):**
   * Baños de Hombres y Mujeres en cada pasillo principal (ej. pasillo central del Edificio B).
   * Baños adaptados para personas con movilidad reducida (♿) en Edificios A, C, G y N.
3. **Puntos de Alimentación:**
   * Cafetería Central y Jaguar Corner (Edificio K), Terrazas y Kioscos 1 y 2.
   * Plaza Chilamates (Módulos Comerciales 1, 2 y 3 con mesas exteriores).
   * Comedor de Colaboradores (zona sureste).
4. **Accesibilidad Universal (Rampas ♿):**
   * Al activar "Ruta accesible", el algoritmo descarta aristas con escaleras o gradas, guiando al usuario únicamente por andenes planos y rampas.
5. **Narración por Voz (Web Speech API):**
   * Un botón *"🔊 Escuchar"* ejecuta la síntesis de voz nativa del navegador en el celular del visitante, leyendo en voz alta las indicaciones paso a paso en español o inglés.
6. **Pines de Objetos Ubicados sobre el Grafo (📍):**
   * El mapa del campus proyecta marcadores visuales sobre los nodos donde se encuentran o fueron reportados objetos extraviados (ej. pin sobre aula B-103 o Cafetería A), permitiendo identificar artículos físicamente en el plano.

### 3. Mecánica Operativa del Grafo y Algoritmo de Dijkstra

El cálculo de ruta se ejecuta mediante el siguiente procedimiento algorítmico estricto:
1. **Modelado en Grafo Ponderado:** Vértices $V$ (puertas de aulas, casetas QR, baños e intersecciones) y Aristas $E$ con peso $w(u,v) = \text{distancia métrica en metros}$ y bandera `esRutaAccesible`.
2. **Cola de Prioridad Min-Heap (`heapq`):**
   * Inicialización: $\text{dist}[\text{origen}] = 0$ y $\text{dist}[v] = \infty \quad \forall v \neq \text{origen}$.
   * Extracción del nodo con menor costo acumulado en tiempo $\mathcal{O}(\log V)$.
   * **Poda por Accesibilidad ♿:** Si se activa el modo silla de ruedas, cualquier arista con $\text{esRutaAccesible} = \text{False}$ (gradas o desniveles) se ignora automáticamente durante la exploración.
   * Relajación de aristas adyacentes: si $\text{dist}[u] + w(u,v) < \text{dist}[v]$, se actualiza $\text{dist}[v]$ y el puntero al nodo predecesor.
3. **Reconstrucción del Camino y Salida:** Se recupera el vector de nodos mediante retroceso de punteros, generando las coordenadas para la polilínea del lienzo SVG y las frases ordenadas para la Web Speech API.
4. **Geolocalización Inversa por Haversine:** La función compara las coordenadas GPS del smartphone contra cada nodo del campus usando trigonometría esférica para asignar el nodo de inicio sin requerir tecleo manual.

</details>

---

<details open>
<summary><b>🇺🇸 English Version</b></summary>

### 1. Scope & 100% Public Access
The map module of **JaguarFind** functions as a campus-tailored pedestrian "Google Maps":
* **No Login Required:** Visitors, parents, and students can search destinations and compute optimal paths without signing in.
* **Three Campus Gate Coverage:**  
  Because physical map totems are concentrated only near Buildings A and B, QR codes are placed at all three entrances:
  1. **Main Entrance (South / Main Parking):** `https://.../mapa?origen=PARQUEO_PPAL`
  2. **Second Entrance (Northeast / Sports Fields):** `https://.../mapa?origen=SEGUNDO_ACCESO`
  3. **Third Entrance (North / Copernicus & Engineering):** `https://.../mapa?origen=TERCER_ACCESO`

---

### 2. Ultra-Fine Campus Directory & POIs
1. **Floor-by-Floor Classrooms:**
   * **Building B (First Floor):** Classrooms `B-101`, `B-102`, `B-103`, `B-104`, `B-105`, and `B-106` ordered left to right. Commercial Module 1 and Jaguar Shop Copy Center at the hallway terminus.
   * **Building B (Second Floor):** Classrooms `B-201` to `B-210`.
   * **Building C (First Floor):** Auditorium C-101, Classrooms `C-102` to `C-106`, Auditorium C-109, and Central Cashier Office.
   * **Building C (Second Floor):** MAC Labs C-107/C-203, Erasmus+ Lab, Computer Labs C-201 to C-205.
   * **Building P (Copernicus):** Meteorology Station, Classrooms `P-101` to `P-401`, Architecture Studios, and Copernicus Astronomical Observatory (5th Floor).
2. **Restrooms:**
   * Men's and Women's restrooms along primary corridors (e.g., Building B central hallway).
   * Wheelchair-accessible restrooms (♿) in Buildings A, C, G, and N.
3. **Dining & Food Areas:**
   * Main Cafeteria & Jaguar Corner (Building K), outdoor patio seating, Kiosks 1 and 2.
   * Plaza Chilamates (Modules 1, 2, and 3 with outdoor tables).
   * Staff Dining Hall (Southeast zone).
4. **Universal Accessibility (Ramps ♿):**
   * Users can toggle "Accessible Route". The Dijkstra algorithm prunes pathways with stairs or steep steps, routing exclusively across paved ramps.
5. **Voice Directions (Web Speech API):**
   * A *"🔊 Listen"* button triggers the browser's native speech synthesis on mobile devices, reading turn-by-turn guidance aloud in English or Spanish.
6. **Located Object Pins on the Graph (📍):**
   * The campus map projects visual markers over nodes where lost items have been reported or held in custody (e.g. pin over room B-103 or Cafeteria A), allowing physical identification on the floor plan.

### 3. Operational Mechanics of Graph and Dijkstra's Algorithm

Route computation is executed via the following strict algorithmic procedure:
1. **Weighted Graph Modeling:** Vertices $V$ (classroom doors, gate QR codes, restrooms, intersections) and Edges $E$ with weight $w(u,v) = \text{metric distance in meters}$ and an `esRutaAccesible` boolean flag.
2. **Min-Heap Priority Queue (`heapq`):**
   * Initialization: $\text{dist}[\text{origin}] = 0$ and $\text{dist}[v] = \infty \quad \forall v \neq \text{origin}$.
   * Extraction of minimum accumulated cost node in $\mathcal{O}(\log V)$ time.
   * **Accessibility Pruning ♿:** When wheelchair mode is active, any edge with $\text{esRutaAccesible} = \text{False}$ (steps/stairs) is automatically ignored during exploration.
   * Relaxation of adjacent edges: if $\text{dist}[u] + w(u,v) < \text{dist}[v]$, updates $\text{dist}[v]$ and predecessor pointer.
3. **Path Reconstruction & Output:** Retrieves node vector via pointer backtracking, generating $(x,y)$ coordinates for SVG polyline drawing and ordered phrases for Web Speech API.
4. **Inverse Geolocation via Haversine:** Compares mobile GPS coordinates against every campus node using spherical trigonometry to set origin node without manual input.

</details>
