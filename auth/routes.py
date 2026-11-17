"""
auth/routes.py
================================================================================
ENRUTADOR Y CONTROLADORES HTTP DE AUTENTICACIÓN
================================================================================

Propósito del Archivo:
----------------------
Contiene las rutas y controladores web de la aplicación Flask para la gestión
de sesiones de usuario en JaguarFind. Implementa tanto el acceso institucional
tradicional con contraseña como el acceso simplificado (passwordless) para visitantes.

Rutas y Lógica que van en este archivo:
--------------------------------------
1. GET/POST /auth/login:
   - Maneja el inicio de sesión del sistema con dos modalidades:
     a) Modalidad Institucional:
        - Recibe: correo (@uamv.edu.ni) y password.
        - Valida credenciales contra el hash almacenado en base de datos.
        - Si es Administrador, redirige a /lost-found/admin; si es Estudiante o Colaborador,
          redirige al catálogo de pertenencias /lost-found/catalogo.
     b) Modalidad Visitante (Passwordless):
        - Recibe: correo personal y cédula de identidad nacional.
        - Autentica por coincidencia sin exigir contraseña (ideal para padres, pacientes y externos).
        - Renueva el campo 'ultimoAcceso' del visitante para mantener activa su cuenta por 6 meses.
   - Si las credenciales fallan, emite mensajes flash explicativos con categoría 'danger'.

2. GET/POST /auth/signup:
   - Renderiza y procesa el formulario de autoregistro para 3 roles públicos:
     a) ESTUDIANTE:
        - Requiere: Nombre completo, correo @uamv.edu.ni, contraseña (>= 6 car.),
          CIF numérico (8 dígitos exactos), facultad y carrera principal.
        - Opcional: Segunda facultad y segunda carrera (soporte de doble titulación en UAM).
     b) COLABORADOR:
        - Requiere: Nombre completo, correo @uamv.edu.ni, contraseña y cédula nacional.
     c) VISITANTE:
        - Requiere: Nombre completo, correo personal válido (sin exigir dominio UAM) y cédula.
        - Contraseña: No requerida (passwordless).
        - Advierte sobre la política de purga automática tras 6 meses de inactividad.
   - Nota: El rol ADMINISTRADOR NO está disponible en el formulario público por motivos de seguridad;
     solo puede ser asignado internamente por otro administrador desde el panel del Edificio A.

3. GET /auth/logout:
   - Limpia la sesión activa en Flask ('session.clear()').
   - Emite mensaje flash informativo y redirige al usuario a la vista del mapa ('map.index').
"""

# Aquí se definen los decoradores @auth_bp.route para login, signup y logout,
# invocando los métodos de negocio de services.py e interactuando con la sesión de Flask.
