"""
database.py
================================================================================
CAPA DE PERSISTENCIA Y GESTIÓN DE BASE DE DATOS RELACIONAL (SQLITE3)
================================================================================

Propósito del Archivo:
----------------------
Administra la conexión a la base de datos relacional SQLite, define el esquema
DDL de tablas relacionales, gestiona migraciones de esquema, ejecuta la política de
retención por inactividad de visitantes (6 meses) y siembra datos iniciales de prueba.

Estructuras de Tablas y Esquemas DDL que van en este archivo:
------------------------------------------------------------
1. Tabla 'usuarios':
   - id: INTEGER PRIMARY KEY AUTOINCREMENT.
   - correo: TEXT UNIQUE NOT NULL (Valida @uamv.edu.ni para estudiantes/colaboradores, o general para visitantes).
   - nombreCompleto: TEXT NOT NULL.
   - passwordHash: TEXT NULL (Obligatorio con hash para Estudiantes/Colaboradores/Admin; NULL para Visitantes).
   - rol: TEXT NOT NULL CHECK(rol IN ('ESTUDIANTE', 'COLABORADOR', 'ADMINISTRADOR', 'VISITANTE')).
   - cif: TEXT NULL (Exactamente 8 dígitos para estudiantes).
   - cedula: TEXT NULL (Cédula nacional para colaboradores y visitantes).
   - facultadPrincipal, facultadSecundaria: TEXT NULL (Soporte oficial de doble titulación).
   - carreraPrincipal, carreraSecundaria: TEXT NULL (Hasta 2 carreras simultáneas en UAM).
   - fechaRegistro: DATETIME DEFAULT CURRENT_TIMESTAMP.
   - ultimoAcceso: DATETIME DEFAULT CURRENT_TIMESTAMP (Para seguimiento de inactividad).

2. Tabla 'objetosPerdidos':
   - id: INTEGER PRIMARY KEY AUTOINCREMENT.
   - titulo: TEXT NOT NULL (Nombre o título del artículo extraviado).
   - categoria: TEXT NOT NULL (ELECTRONICOS, DOCUMENTOS, OTROS, etc.).
   - descripcionPublica: TEXT NOT NULL (Visible públicamente en catálogo y mapa).
   - detalleSecretoValidacion: TEXT NOT NULL (Dato confidencial para regla antifraude, aislado de consultas públicas).
   - ubicacionHallazgo: TEXT NOT NULL (Identificador del nodo del campus, ej. 'B_103', 'A_CAFETERIA').
   - estado: TEXT NOT NULL DEFAULT 'REPORTADO' CHECK(estado IN ('REPORTADO', 'VERIFICADO', 'ENTREGADO')).
   - usuarioReportaId: INTEGER NOT NULL (FK a usuarios.id).
   - usuarioReclamaId: INTEGER NULL (FK a usuarios.id, asignado al entregar el bien).
   - fechaReporte: DATETIME DEFAULT CURRENT_TIMESTAMP.
   - fechaVerificacion: DATETIME NULL (Registro del momento en que ingresa a custodia en Edificio A).
   - fechaEntrega: DATETIME NULL (Momento del descargo legal al dueño).
   - notaEntrega: TEXT NULL (Observaciones del recepcionista).

Funciones y Procedimientos que van en este archivo:
--------------------------------------------------
- getDbConnection():
  Abre y retorna una conexión SQLite configurando conn.row_factory = sqlite3.Row
  y activando claves foráneas con 'PRAGMA foreign_keys = ON;'.

- migrarEsquemaUsuarios(conn):
  Aplica transformaciones de esquema cuando se añaden nuevas columnas (como ultimoAcceso)
  o se amplían restricciones CHECK (como el soporte del 4to rol VISITANTE).

- depurarVisitantesInactivos(diasInactividad=180):
  Implementa la regla de negocio de privacidad y retención:
  Ejecuta 'DELETE FROM usuarios WHERE rol = "VISITANTE" AND julianday("now") - julianday(ultimoAcceso) >= ?'
  para purgar automáticamente cuentas de visitantes sin actividad en más de 6 meses.

- inicializarBd():
  Crea las tablas DDL, ejecuta migraciones y siembra los 4 perfiles iniciales de prueba:
  1) Administrador (admin@uamv.edu.ni / uam2026).
  2) Estudiante con doble titulación (estudiante@uamv.edu.ni / CIF: 22019845).
  3) Colaborador docente/administrativo (colaborador@uamv.edu.ni / Cédula).
  4) Visitante passwordless (carlos.mendoza@gmail.com / Cédula: 001-180775-0023V).
  Así como objetos en cada uno de los 3 estados de custodia (REPORTADO, VERIFICADO, ENTREGADO).
"""

# Aquí se implementan las funciones getDbConnection(), migrarEsquemaUsuarios(),
# inicializarBd() y depurarVisitantesInactivos().
