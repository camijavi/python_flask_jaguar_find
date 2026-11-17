"""
config.py
================================================================================
CONFIGURACIÓN CENTRAL DEL SISTEMA JAGUARFIND & JAGUARMAPS
================================================================================

Propósito del Archivo:
----------------------
Centraliza todos los parámetros de configuración, constantes de entorno,
rutas de persistencia del sistema de archivos y políticas de negocio para
la aplicación Flask de la Universidad Americana (UAM).

Variables y Parámetros que van en este archivo:
----------------------------------------------
1. SECRET_KEY:
   - Clave criptográfica para la firma de sesiones de usuario y cookies seguras.
   - Debe provenir de variables de entorno (os.environ) o usar un valor por defecto
     para entornos de desarrollo académico.

2. DATABASE_PATH:
   - Ruta absoluta o relativa hacia el archivo de base de datos relacional SQLite
     (jaguarFind.db) en el directorio raíz del proyecto.

3. LANGUAGES_DIR:
   - Ruta a la carpeta 'languages/', donde residen los diccionarios de internacionalización
     en formato JSON ('spa.json' para Español y 'eng.json' para Inglés).

4. DEFAULT_LANGUAGE:
   - Idioma predeterminado del sistema ('spa').

5. DIAS_INACTIVIDAD_VISITANTE:
   - Constante que define el plazo de inactividad permitido para cuentas con rol
     VISITANTE (180 días / aproximadamente 6 meses) antes de ser depuradas
     automáticamente por la política de retención de datos personales.

6. ROLES_PERMITIDOS:
   - Tupla de validación para los 4 roles del sistema:
     ('ESTUDIANTE', 'COLABORADOR', 'ADMINISTRADOR', 'VISITANTE').

7. ESTADOS_CUSTODIA:
   - Tupla para la máquina de estados del Edificio A:
     ('REPORTADO', 'VERIFICADO', 'ENTREGADO').
"""

# Aquí se define la clase Config con las variables estáticas mencionadas arriba.
