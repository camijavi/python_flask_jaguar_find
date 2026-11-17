# Lost & Found Management & User Roles / Gestión de Objetos Perdidos y Usuarios

---

<details open>
<summary><b>🇪🇸 Versión en Español</b></summary>

### 1. Autenticación y Modelo de Usuarios (4 Roles)
A diferencia del mapa abierto, este módulo salvaguarda la custodia patrimonial implementando 4 roles de usuario:
* **Estudiante:** Nombre completo, correo `@uamv.edu.ni`, contraseña (>= 6 car.), número CIF (8 dígitos exactos) y soporte para hasta 2 carreras simultáneas (doble titulación).
* **Colaborador:** Nombre completo, correo `@uamv.edu.ni`, contraseña y cédula nacional (docentes y personal administrativo).
* **Administrador:** Coordinación del Edificio A. Sin autorregistro público; se asigna y delega desde el panel `/admin/usuarios`.
* **Visitante (Externo / Transitorio):** Nombre completo, correo electrónico personal (Gmail, Outlook, etc.) y cédula de identidad nacional.
  * **Sin Contraseña (Passwordless):** Dado su carácter transitorio (padres de familia, pacientes de clínicas odontológicas, público de eventos), no requiere memorizar contraseñas; accede directamente con su Correo y Cédula.
  * **Política de Retención y Depuración por Inactividad (6 Meses):** Cuentas temporales con ciclo de vida efímero que se eliminan automáticamente tras 180 días sin actividad en el sistema (`depurarVisitantesInactivos(dias=180)`).

---

### 2. El Ciclo de Vida en 3 Estados
1. **Estado 1: Reportado (En camino al Edificio A):** El usuario halla el bien, recibe sugerencia de edificio por GPS y lo registra en `/reportar`.
2. **Estado 2: En Custodia (Recibido en Edificio A):** Entrega física en el Edificio A. El administrador asienta la cédula del entregador y verifica el artículo.
3. **Estado 3: Entregado a su Dueño (Archivado):** El dueño reclama en el Edificio A respondiendo a la pregunta de validación basada en el `detalleOcultoValidador`.

---

### 3. Regla Antifraude (`detalleOcultoValidador`)
En la vista pública solo se muestran datos generales (categoría, color, edificio y fecha). El detalle íntimo (ej. fondo de pantalla, stickers, iniciales grabadas) permanece **oculto al público** y solo lo ve el Administrador para confrontar la respuesta del reclamante antes de entregar el bien físico.

---

### 4. Relación y Búsqueda por Lugar y Fecha (Pines en el Grafo del Mapa)

#### A. Pines de Objetos Ubicados sobre el Grafo:
* El grafo del campus **no se utiliza para relacionar objetos entre sí**. En su lugar, el grafo del mapa proyecta **pines o marcadores interactivos (📍)** en los nodos donde se encuentran o fueron reportados los objetos (ej. pin sobre `B_103` o `A_CAFETERIA`).
* Al tocar un pin en el mapa interactivo, se despliega la tarjeta informativa con el nombre del artículo, fecha y botón para reclamarlo en el Edificio A.

#### B. Relación por Lugar y Fecha vs. Lugar + Fecha + Hora:
* **¿Cuál opción es mejor?** La relación por **Lugar y Fecha** es significativamente superior a *Lugar + Fecha + Hora* por los siguientes motivos:
  1. **Asincronía Temporal Inevitable:** La hora en que alguien extravía un objeto nunca coincide con la hora en que alguien lo encuentra (ej. extraviado a las 9:15 AM durante una clase y hallado por conserjería a las 2:00 PM). Un filtro estricto por hora descartaría el objeto verdadero generando falsos negativos.
  2. **Memoria del Usuario:** Los estudiantes recuerdan claramente el día y el aula/área ("el martes en B-103"), pero difícilmente el minuto exacto.
  3. **Consulta Determinista:** Permite agrupar los hallazgos de ese día escolar en esa aula de manera limpia:
     ```sql
     SELECT * FROM objetosPerdidos 
     WHERE ubicacionHallazgo = ? AND DATE(fechaReporte) = ?
       AND estado IN ('REPORTADO', 'VERIFICADO');
     ```
  4. **Franja Horaria Opcional:** Se puede incorporar una franja aproximada (Mañana / Tarde / Noche) como filtro secundario opcional, nunca restrictivo al minuto.

---

### 5. Esquema DDL en SQLite3 (`database.py`)
```sql
CREATE TABLE IF NOT EXISTS usuarios (
    correoInstitucional TEXT PRIMARY KEY,
    passwordHash TEXT NOT NULL,
    nombreCompleto TEXT NOT NULL,
    rolUsuario TEXT NOT NULL CHECK(rolUsuario IN ('estudiante', 'colaborador', 'admin')),
    cif TEXT,
    cedula TEXT,
    facultadPrincipal TEXT,
    facultadSecundaria TEXT,
    carreraPrincipal TEXT,
    carreraSecundaria TEXT,
    fechaRegistro TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS objetosPerdidos (
    idTicket INTEGER PRIMARY KEY AUTOINCREMENT,
    categoria TEXT NOT NULL,
    color TEXT NOT NULL,
    descripcion TEXT NOT NULL,
    detalleOcultoValidador TEXT,
    idNodoHallazgo TEXT NOT NULL,
    fechaHoraHallazgo TEXT NOT NULL,
    estadoTicket INTEGER NOT NULL CHECK(estadoTicket IN (1, 2, 3)),
    correoEncontro TEXT NOT NULL,
    cedulaEncontro TEXT,
    correoDueno TEXT,
    cifDueno TEXT,
    nombreDueno TEXT,
    carreraDueno TEXT,
    cedulaDueno TEXT,
    fechaEntrega TEXT,
    FOREIGN KEY (correoEncontro) REFERENCES usuarios(correoInstitucional)
);
```

</details>

---

<details open>
<summary><b>🇺🇸 English Version</b></summary>

### 1. Authentication and User Roles (4 Roles)
Unlike the open public map, this module safeguards property custody implementing 4 distinct user roles:
* **Student:** Full name, institutional email (`@uamv.edu.ni`), password (>= 6 chars), 8-digit CIF, and official support for double degrees (up to 2 majors).
* **Collaborator:** Full name, institutional email (`@uamv.edu.ni`), password, and national ID (faculty and administrative staff).
* **Administrator:** Building A Coordination. No public sign-up; assigned and delegated via internal `/admin/usuarios` panel.
* **Visitor (External / Transient):** Full name, personal email (Gmail, Outlook, etc.), and national ID.
  * **Passwordless Access:** Designed for transient guests (parents, dental clinic patients, event visitors); requires no password and signs in directly via matching Email and National ID.
  * **Inactivity Retention & Purge Policy (6 Months):** Temporary accounts automatically deleted after 180 days (~6 months) of inactivity (`depurarVisitantesInactivos(dias=180)`).

---

### 2. The 3-State Lifecycle
1. **State 1: Reported (En route to Building A):** Found item reported with nearest GPS building suggestion.
2. **State 2: In Custody (Building A Intake):** Physical intake at Building A. Administrator logs finder's ID.
3. **State 3: Returned to Owner (Archived):** Owner verifies ownership via anti-fraud question, logs credentials, and ticket is archived.

---

### 3. Anti-Fraud Secret Rule (`detalleOcultoValidador`)
The public feed only displays generic metadata (category, color, building, date). Distinctive private attributes remain hidden from the public and are accessible exclusively to Building A administrators during owner claims.

---

### 4. Correlation & Search by Location and Date (Map Graph Pins)

#### A. Pins of Located Items on the Graph:
* The campus graph is **not used to relate objects to each other**. Instead, the map graph projects **interactive pins (📍)** on the physical nodes where items have been reported or held in custody (e.g. pin on `B_103` or `A_CAFETERIA`).
* Tapping a pin on the interactive campus map reveals the item's summary card with its name, date, and instructions to claim it at Building A.

#### B. Location and Date vs. Location + Date + Time:
* **Which option is better?** Correlation by **Location and Date** is significantly superior to *Location + Date + Time* for the following reasons:
  1. **Inevitable Temporal Discrepancy:** The moment an item is lost rarely matches the moment someone finds it (e.g., dropped at 9:15 AM during a lecture, found by cleaning staff at 2:00 PM). A strict time filter generates false negatives and causes valid claims to be missed.
  2. **User Recall:** Students reliably remember the day and the classroom/facility ("Tuesday in B-103"), but seldom the exact minute.
  3. **Deterministic Querying:** Groups all findings from that academic day in that classroom cleanly:
     ```sql
     SELECT * FROM objetosPerdidos 
     WHERE ubicacionHallazgo = ? AND DATE(fechaReporte) = ?
       AND estado IN ('REPORTADO', 'VERIFICADO');
     ```
  4. **Optional Time Blocks:** A flexible window (Morning / Afternoon / Evening) can be added as an optional guide, never as a strict minute restriction.

</details>
