"""
lost_found/routes.py
================================================================================
ENRUTADOR Y CONTROLADORES PARA CUSTODIA Y OBJETOS PERDIDOS
================================================================================

Propósito del Archivo:
----------------------
Contiene los controladores web para la consulta pública de pertenencias,
el formulario de registro de hallazgos, la ficha de detalle, el cuaderno de recepción
y custodia física del Edificio A, y el panel administrativo de delegación de roles.

Rutas y Lógica que van en este archivo:
--------------------------------------
1. GET /lost-found/catalogo:
   - Muestra la lista de objetos reportados y verificados.
   - Procesa los filtros de búsqueda por LUGAR (nodo físico) y FECHA (día escolar),
     con selector opcional de franja horaria (Mañana/Tarde/Noche).
   - Sanitiza estrictamente los datos para no exponer el 'detalleSecretoValidacion'.

2. GET/POST /lost-found/reportar (@loginRequerido):
   - Permite a cualquier usuario autenticado (Estudiante, Colaborador o Visitante)
     reportar un objeto que encontró en el campus.
   - Campos: Título, categoría, descripción pública, nodo/lugar de hallazgo, fecha,
     y el OBLIGATORIO 'detalleSecretoValidacion' (secreto antifraude).
   - Asigna el estado inicial 'REPORTADO' e inserta el ticket en la base de datos.

3. GET /lost-found/detalle/<int:objetoId>:
   - Renderiza la ficha pública de un artículo con su fotografía o descripción general,
     lugar y fecha de hallazgo, e instrucciones de cómo reclamarlo en el Edificio A.

4. GET /lost-found/admin (@adminRequerido):
   - Cuaderno digital oficial de recepción del Edificio A.
   - Permite a los administradores visualizar todos los objetos en sus 3 estados:
     * REPORTADO: Objeto en posesión del reportante mientras camina hacia el Edificio A.
     * VERIFICADO: Objeto recibido y custodiado físicamente en recepción (activa pin en mapa).
     * ENTREGADO: Objeto devuelto exitosamente a su dueño legítimo.
   - Muestra el 'detalleSecretoValidacion' exclusivamente al administrador para la
     confrontación oral en ventanilla durante el reclamo.

5. POST /lost-found/admin/cambiar-estado (@adminRequerido):
   - Procesa la transición de estado:
     * De REPORTADO a VERIFICADO (ingreso a custodia física).
     * De VERIFICADO a ENTREGADO (asentando cédula/CIF del dueño, fecha, hora y nota de descargo).

6. GET /lost-found/admin/usuarios (@adminRequerido):
   - Lista todas las cuentas del sistema (estudiantes, colaboradores, administradores y visitantes).
   - Permite crear cuentas administrativas directamente.
   - Permite delegar/promover usuarios al rol ADMINISTRADOR.

7. POST /lost-found/admin/usuarios/rol (@adminRequerido):
   - Actualiza el rol de un usuario en base de datos.

8. POST /lost-found/admin/usuarios/depurar-visitantes (@adminRequerido):
   - Ejecuta manualmente la política de retención para eliminar visitantes inactivos
     por más de 6 meses (180 días), informando el total de cuentas purgadas.
"""

# Aquí se definen los decoradores @lost_found_bp.route para catalogo, reportar,
# detalle, admin, cambio de estados, administración de roles y depuración de visitantes.
