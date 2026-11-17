"""
api/lost_found_endpoints.py
================================================================================
ENDPOINTS RESTFUL PARA CATÁLOGO Y PINES GEORREFERENCIADOS DE OBJETOS PERDIDOS
================================================================================

Propósito del Archivo:
----------------------
Provee servicios web JSON para consultar el catálogo de artículos perdidos
filtrables por Lugar y Fecha, así como para alimentar la capa de pines interactivos
del mapa del campus universitario.

Endpoints que van en este archivo:
---------------------------------
1. GET /api/objetos:
   - Parámetros de consulta URL opcionales:
     * ?lugar=B_103: Identificador del nodo donde se halló el artículo.
     * ?fecha=2026-11-10: Fecha en formato YYYY-MM-DD.
     * ?categoria=ELECTRONICOS: Categoría del objeto.
   - Proceso:
     Ejecuta consulta relacional indexada en SQLite aplicando el modelo validado de
     búsqueda por Lugar y Fecha (evitando exclusiones indebidas por discrepancia horaria).
   - NOTA DE SEGURIDAD ANTIFRAUDE:
     Aísla estrictamente la columna 'detalleSecretoValidacion'.
   - Salida JSON:
     Lista de objetos activos con título, categoría, descripción pública, nodo y fecha.

2. GET /api/pines-mapa:
   - Proceso:
     Consulta todos los artículos bajo custodia activa en estado 'REPORTADO' o 'VERIFICADO'.
     Vincula cada registro con las coordenadas cartesianas (x, y) de su nodo físico correspondiente.
   - Salida JSON:
     Retorna un array de pines georreferenciados para que 'mapaInteractivo.js' dibuje
     marcadores interactivos (📍) sobre el plano SVG del campus UAM. Al hacer clic sobre
     el pin, se despliega una ficha flotante con información del objeto y enlace de reclamo.

3. GET /api/estadisticas:
   - Retorna métricas generales agregadas del módulo de objetos perdidos
     (total registrados, total en custodia en Edificio A, porcentaje de entrega exitosa).
"""

# Aquí se implementan los controladores GET /api/objetos, GET /api/pines-mapa y GET /api/estadisticas.
