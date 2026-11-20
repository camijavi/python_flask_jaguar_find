/**
 * ================================================================================
 * CONTROLADOR DE SÍNTESIS DE VOZ NATIVO (TTSHELPER.JS)
 * ================================================================================
 * 
 * Propósito del Archivo:
 * ----------------------
 * Encapsula la API nativa de voz del navegador (Web Speech API - window.speechSynthesis)
 * para proporcionar guía acústica paso a paso (Turn-by-Turn) a estudiantes, visitantes
 * y personas con discapacidad visual o movilidad reducida mientras caminan por el campus.
 * 
 * Clases, Métodos y Lógica que van en este archivo:
 * ------------------------------------------------
 * 1. Clase 'TtsHelper':
 *    - constructor(opciones):
 *      * Inicializa la referencia a window.speechSynthesis.
 *      * Configura parámetros por defecto: idioma ('es-NI' / 'es-ES' / 'en-US'),
 *        velocidad de habla (rate = 1.0) y tono (pitch = 1.0).
 * 
 * 2. Métodos Principales:
 *    - hablarTexto(texto, callbackFin):
 *      * Crea una nueva instancia de SpeechSynthesisUtterance(texto).
 *      * Selecciona la mejor voz disponible en el sistema operativo según el idioma actual.
 *      * Dispara la reproducción de audio y notifica al terminar.
 *    - reproducirSecuenciaPasos(listaPasos, callbackPaso, callbackFinal):
 *      * Itera secuencialmente sobre las instrucciones generadas por Dijkstra
 *        (ej. 'Avanza 20 metros hacia el aula B-103', 'Gira a la derecha en el pasillo').
 *      * Sincroniza la locución de audio con el resaltado visual del paso en pantalla.
 *    - pausar():
 *      * Pausa la síntesis de voz en curso (speechSynthesis.pause()).
 *    - reanudar():
 *      * Continúa la reproducción (speechSynthesis.resume()).
 *    - cancelar():
 *      * Detiene inmediatamente cualquier locución en reproducción o cola (speechSynthesis.cancel()).
 * 
 * 3. Detección de Soporte:
 *    - esSoportado():
 *      * Verifica si 'speechSynthesis' in window está disponible en el navegador del usuario.
 *      * Si no es soportado, oculta los botones de voz o muestra un aviso no intrusivo.
 */
