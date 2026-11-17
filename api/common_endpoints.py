"""
api/common_endpoints.py
================================================================================
ENDPOINTS COMUNES, INTERNACIONALIZACIÓN (I18N) Y ESTADO DEL SISTEMA
================================================================================

Propósito del Archivo:
----------------------
Contiene endpoints transversales que dan soporte al cambio dinámico de idioma
entre Español e Inglés, y la verificación del estado de salud de la aplicación.

Endpoints que van en este archivo:
---------------------------------
1. GET /api/idioma/<lang>:
   - Parámetro de ruta:
     * lang: 'spa' o 'eng'.
   - Proceso:
     Valida que el código de idioma sea admitido.
     Actualiza la variable de sesión en Flask: 'session["idioma"] = lang'.
   - Salida JSON:
     {
       "exito": true,
       "idiomaActual": "spa",
       "mensaje": "Idioma actualizado a Español"
     }

2. GET /api/status:
   - Proceso:
     Verifica la conectividad activa con el archivo de base de datos SQLite
     y el estado de los módulos de la aplicación.
   - Salida JSON:
     {
       "estado": "operativo",
       "baseDeDatos": "conectada",
       "sistema": "JaguarFind & JaguarMaps UAM",
       "version": "3.1"
     }
"""

# Aquí se implementan los controladores GET /api/idioma/<lang> y GET /api/status.
