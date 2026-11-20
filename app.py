"""
app.py
================================================================================
PUNTO DE ENTRADA Y FÁBRICA DE APLICACIÓN FLASK (APPLICATION FACTORY)
================================================================================

Propósito del Archivo:
----------------------
Es el archivo principal que inicializa el servidor web WSGI, configura la instancia
de la aplicación Flask ('app') e integra todos los módulos desacoplados del sistema
mediante el patrón arquitectónico de Blueprints.

Componentes y Lógica que van en este archivo:
--------------------------------------------
1. Instanciación de Flask y Carga de Configuración:
   - Crear la instancia de Flask(__name__).
   - Cargar parámetros desde 'config.py' (app.config.from_object(Config)).

2. Registro de Blueprints Modulares:
   - auth_bp (/auth): Módulo de login institucional/visitante, signup y logout.
   - map_bp (/ y /map): Navegador peatonal interactivo del campus y escaneo QR en casetas.
   - lost_found_object_bp (/lost-found-object): Catálogo de objetos, reporte y panel de custodia del Edificio A.
   - api_bp (/api): Servicios web RESTful (rutas Dijkstra, puntos de interés, catálogo JSON y pines).

3. Sistema de Internacionalización (i18n):
   - Inyección de contexto con context_processor para habilitar la función de traducción t(clave)
     en todas las plantillas Jinja2.
   - Lectura de archivos JSON en 'languages/' (spa.json y eng.json).
   - Detección de idioma preferido en la sesión del usuario ('session["idioma"]').

4. Manejo Global de Errores HTTP:
   - Controladores para páginas de error personalizadas:
     - Error 404 (Recurso o aula no encontrada).
     - Error 500 (Fallo interno del servidor).

5. Inicialización de la Base de Datos:
   - Llamada a inicializarBd() de 'database.py' en el arranque para garantizar que
     el esquema SQLite y los registros semilla estén creados.

6. Bloque de Ejecución Principal (__main__):
   - app.run(host="0.0.0.0", port=5000, debug=True) para desarrollo local.
"""

# Aquí se implementa la inicialización de la aplicación Flask, el registro de Blueprints,
# el context processor de traducción i18n y el bloque de ejecución del servidor.
