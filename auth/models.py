"""
auth/models.py
================================================================================
OBJETOS DE ACCESO A DATOS (DAO) PARA LA TABLA 'USUARIOS'
================================================================================

Propósito del Archivo:
----------------------
Aísla todas las operaciones SQL directas (consultas SELECT, inserciones INSERT,
actualizaciones UPDATE y eliminaciones DELETE) relacionadas con los usuarios del sistema.
Garantiza un desacoplamiento limpio entre la base de datos y la lógica de controladores.

Funciones de Acceso a Datos que van en este archivo:
---------------------------------------------------
1. buscarUsuarioPorCorreo(correo):
   - Ejecuta SELECT * FROM usuarios WHERE LOWER(correo) = LOWER(?).
   - Retorna un diccionario con los datos del usuario o None si no existe.

2. buscarUsuarioPorId(usuarioId):
   - Ejecuta SELECT * FROM usuarios WHERE id = ?.
   - Retorna la entidad del usuario según su clave primaria.

3. buscarVisitantePorCorreoYCedula(correo, cedula):
   - Realiza la búsqueda de coincidencia para la autenticación sin contraseña:
     SELECT * FROM usuarios WHERE correo = ? AND cedula = ? AND rol = 'VISITANTE'.
   - Normaliza cadenas ignorando espacios o guiones para evitar rechazos por formato.

4. actualizarUltimoAcceso(usuarioId):
   - Ejecuta UPDATE usuarios SET ultimoAcceso = CURRENT_TIMESTAMP WHERE id = ?.
   - Mantiene actualizada la marca de tiempo de actividad para la política de retención de 6 meses.

5. crearUsuario(correo, nombreCompleto, passwordHash, rol, cif, cedula, facultadPrincipal, carreraPrincipal, facultadSecundaria, carreraSecundaria):
   - Inserta un nuevo registro en la tabla 'usuarios'.
   - Para visitantes, passwordHash se almacena como NULL.
   - Retorna el ID autoincremental generado ('cursor.lastrowid').

6. listarTodosUsuarios():
   - Retorna la lista completa de usuarios ordenados por fecha/ID descendente
     para alimentar la tabla del panel administrativo del Edificio A.

7. actualizarRolUsuario(usuarioId, nuevoRol):
   - Ejecuta UPDATE usuarios SET rol = ? WHERE id = ?.
   - Valida que nuevoRol pertenezca a ('ESTUDIANTE', 'COLABORADOR', 'ADMINISTRADOR', 'VISITANTE').
   - Permite al Administrador promover a otros colaboradores como administradores de custodia.

8. eliminarVisitantesInactivos(dias=180):
   - Invoca el procedimiento de depuración de visitantes inactivos definido en 'database.py'.
"""

# Aquí se implementan las funciones DAO para interactuar con SQLite mediante getDbConnection().
