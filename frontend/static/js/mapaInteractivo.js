/**
 * ================================================================================
 * LÓGICA DE INTERACCIÓN CARTOGRÁFICA Y PINES VECTORIALES (MAPAINTERACTIVO.JS)
 * ================================================================================
 * 
 * Propósito del Archivo:
 * ----------------------
 * Orquesta la interactividad del lienzo vectorial SVG en la página principal (/mapa).
 * Gestiona la selección de nodos de origen/destino, el consumo asíncrono de la API
 * de Dijkstra (/api/ruta), el dibujo animado de polilíneas peatonales, la integración
 * con la Web Speech API (ttsHelper.js) y el renderizado interactivo de pines
 * de pertenencias extraviadas sobre el plano de la UAM.
 * 
 * Funciones y Módulos que van en este archivo:
 * --------------------------------------------
 * 1. Inicialización y Event Listeners:
 *    - Captura elementos del DOM: selects de origen/destino, toggle de accesibilidad,
 *      contenedor SVG del mapa, lista de instrucciones y panel de métricas.
 *    - Pendiente para una futura integración QR: leer un parámetro de ubicación validado
 *      (ej. ?origen=GATE_1) para establecer el origen al abrir un enlace de señalización.
 * 
 * 2. Consumo de la API de Rutas (Dijkstra):
 *    - trazarRuta():
 *      * Realiza una petición POST asíncrona a '/api/ruta' enviando {origen, destino, accesible}.
 *      * Recibe coordenadas (x, y) de la secuencia de nodos óptimos, distancia y pasos de voz.
 *      * Llama a dibujarPolilineaSvg(nodos) y actualiza las métricas de distancia y tiempo.
 *      * Prepara la lista de instrucciones paso a paso para el asistente de voz.
 * 
 * 3. Renderizado Gráfico Vectorial en el SVG:
 *    - dibujarPolilineaSvg(nodos):
 *      * Genera un elemento <polyline> o <path> con las coordenadas de la ruta.
 *      * Aplica la clase 'ruta-animada' para producir el trazado fluido continuo.
 *    - centrarVistaEnNodo(nodoId):
 *      * Ajusta el viewBox del SVG para enfocar el origen o el destino seleccionado.
 * 
 * 4. Capa de Pines Georreferenciados de Objetos Perdidos:
 *    - cargarPinesDeObjetos():
 *      * Realiza petición GET a '/api/pines-mapa' para obtener los artículos bajo custodia activa.
 *      * Inserta elementos <g class="pin-objeto"> en las coordenadas (x, y) de los nodos correspondientes.
 *      * Asocia eventos 'click' para abrir una tarjeta emergente (popover) con el título del artículo,
 *        lugar, fecha y botón para tramitar el reclamo en el Edificio A.
 * 
 * 5. Geolocalización por GPS (Haversine):
 *    - usarUbicacionActual():
 *      * Solicita permiso al navegador (navigator.geolocation.getCurrentPosition).
 *      * Envía latitud y longitud a '/api/gps-cercano' para detectar la caseta de entrada o edificio
 *        más próximo al usuario y seleccionarlo automáticamente como punto de partida.
 * 
 * 6. Integración con el Sintetizador de Voz (ttsHelper.js):
 *    - Botón de audio para reproducir las instrucciones paso a paso usando la Web Speech API nativa.
 */
