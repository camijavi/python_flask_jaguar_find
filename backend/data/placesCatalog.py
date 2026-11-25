"""
placesCatalog.py
================================================================================
Comprehensive catalog of all campus rooms, labs, faculties, food areas,
drinking fountains, restrooms, and parking spaces strictly synchronized with
buildings.txt and coordenadas.txt.
Enforces exact building/floor mappings, left-to-right ordering, and
non-hyphenated room nomenclature (e.g. B101, NOT B-101).
================================================================================
"""

from backend.data.campusCategories import CampusCategory

# Master list of all internal and external campus points of interest
PLACES_CATALOG = [
    # -------------------------------------------------------------------------
    # BUILDING A: Administrative, Student Services & DPA (Floors 1, 2, 3)
    # -------------------------------------------------------------------------
    # Floor 1 (exact order from buildings.txt)
    {
        "placeId": "accountingOfficeA",
        "name": "Contabilidad (A101)",
        "category": CampusCategory.ADMINISTRATIVE,
        "parentBuildingId": "buildingA",
        "floorLevel": 1,
        "isAccessible": True,
        "latitude": 12.108503,
        "longitude": -86.256678,
        "locationNotes": "Edificio A, Piso 1, junto a cajeros.",
        "keywords": ["contabilidad", "a101", "a-101", "a 101", "accounting"]
    },
    {
        "placeId": "studentCareCenterA",
        "name": "Centro de Atención al Estudiante (CAE) / Zona Común",
        "category": CampusCategory.ADMINISTRATIVE,
        "parentBuildingId": "buildingA",
        "floorLevel": 1,
        "isAccessible": True,
        "latitude": 12.108543,
        "longitude": -86.256496,
        "locationNotes": "Edificio A, Piso 1, vestíbulo principal.",
        "keywords": ["cae", "atencion al estudiante", "zona comun", "student services"]
    },
    {
        "placeId": "admissionsMarketingA",
        "name": "Dirección de Mercadeo y Admisión",
        "category": CampusCategory.ADMINISTRATIVE,
        "parentBuildingId": "buildingA",
        "floorLevel": 1,
        "isAccessible": True,
        "latitude": 12.108543,
        "longitude": -86.256496,
        "locationNotes": "Edificio A, Piso 1, zona CAE.",
        "keywords": ["direccion de mercadeo y admision", "mercadeo y admision", "admisiones", "admision"]
    },
    {
        "placeId": "academicRecordsA",
        "name": "Registro Académico",
        "category": CampusCategory.ADMINISTRATIVE,
        "parentBuildingId": "buildingA",
        "floorLevel": 1,
        "isAccessible": True,
        "latitude": 12.108417,
        "longitude": -86.256656,
        "locationNotes": "Edificio A, Piso 1, recepción y atención académica.",
        "keywords": ["registro", "registro academico", "notas", "matricula", "certificados"]
    },
    {
        "placeId": "collectionsOfficeA",
        "name": "Cartera y Cobro",
        "category": CampusCategory.ADMINISTRATIVE,
        "parentBuildingId": "buildingA",
        "floorLevel": 1,
        "isAccessible": True,
        "latitude": 12.108543,
        "longitude": -86.256496,
        "locationNotes": "Edificio A, Piso 1, atención financiera.",
        "keywords": ["cartera y cobro", "cartera", "cobro", "cobros"]
    },
    {
        "placeId": "academicDirectorateA",
        "name": "Dirección Académica (Edificio A)",
        "category": CampusCategory.ADMINISTRATIVE,
        "parentBuildingId": "buildingA",
        "floorLevel": 1,
        "isAccessible": True,
        "latitude": 12.108543,
        "longitude": -86.256496,
        "locationNotes": "Edificio A, Piso 1.",
        "keywords": ["direccion academica", "direccion academica a"]
    },
    {
        "placeId": "financialDirectorateA",
        "name": "Dirección Financiera",
        "category": CampusCategory.ADMINISTRATIVE,
        "parentBuildingId": "buildingA",
        "floorLevel": 1,
        "isAccessible": True,
        "latitude": 12.108543,
        "longitude": -86.256496,
        "locationNotes": "Edificio A, Piso 1.",
        "keywords": ["direccion financiera", "finanzas", "finance"]
    },
    {
        "placeId": "lostAndFoundOfficeA",
        "name": "Objetos Perdidos (JaguarFind) y Recepción",
        "category": CampusCategory.ADMINISTRATIVE,
        "parentBuildingId": "buildingA",
        "floorLevel": 1,
        "isAccessible": True,
        "latitude": 12.108417,
        "longitude": -86.256656,
        "locationNotes": "Edificio A, Piso 1, mostrador de recepción.",
        "keywords": ["objetos perdidos", "lost and found", "perdido", "custodia", "jaguarfind", "recepcion a"]
    },
    {
        "placeId": "atmMachinesA",
        "name": "Cajeros Automáticos (BAC y LAFISE) y Mapa UAM",
        "category": CampusCategory.ADMINISTRATIVE,
        "parentBuildingId": "buildingA",
        "floorLevel": 1,
        "isAccessible": True,
        "latitude": 12.108560,
        "longitude": -86.256574,
        "locationNotes": "Fuera del Edificio A, fachada principal junto al Mapa UAM.",
        "keywords": ["cajero", "cajeros", "cajeros automaticos", "atm", "bac", "lafise", "dinero", "efectivo", "mapa uam a"]
    },
    # Floor 2 (exact order from buildings.txt)
    {
        "placeId": "adminDirectorateA",
        "name": "Dirección Administrativa (A201)",
        "category": CampusCategory.ADMINISTRATIVE,
        "parentBuildingId": "buildingA",
        "floorLevel": 2,
        "isAccessible": False,
        "latitude": 12.108543,
        "longitude": -86.256609,
        "locationNotes": "Edificio A, Piso 2.",
        "keywords": ["a201", "a-201", "a 201", "direccion administrativa", "departamento administrativo"]
    },
    {
        "placeId": "academicLogisticsA",
        "name": "Logística Académica",
        "category": CampusCategory.ADMINISTRATIVE,
        "parentBuildingId": "buildingA",
        "floorLevel": 2,
        "isAccessible": False,
        "latitude": 12.108543,
        "longitude": -86.256609,
        "locationNotes": "Edificio A, Piso 2.",
        "keywords": ["logistica academica", "logistica a"]
    },
    {
        "placeId": "ticDirectorateA",
        "name": "Dirección Tecnología de la Información y Comunicación - TIC (A203)",
        "category": CampusCategory.ADMINISTRATIVE,
        "parentBuildingId": "buildingA",
        "floorLevel": 2,
        "isAccessible": False,
        "latitude": 12.108412,
        "longitude": -86.256682,
        "locationNotes": "Edificio A, Piso 2.",
        "keywords": ["a203", "a-203", "a 203", "tic", "direccion tecnologia de la informacion y comunicacion", "tecnologia"]
    },
    {
        "placeId": "marketingAdvertisingA",
        "name": "Mercadeo y Publicidad (A204)",
        "category": CampusCategory.ADMINISTRATIVE,
        "parentBuildingId": "buildingA",
        "floorLevel": 2,
        "isAccessible": False,
        "latitude": 12.108412,
        "longitude": -86.256682,
        "locationNotes": "Edificio A, Piso 2.",
        "keywords": ["a204", "a-204", "a 204", "mercadeo y publicidad", "publicidad"]
    },
    {
        "placeId": "talentDirectorateA",
        "name": "Dirección de Gestión del Talento",
        "category": CampusCategory.ADMINISTRATIVE,
        "parentBuildingId": "buildingA",
        "floorLevel": 2,
        "isAccessible": False,
        "latitude": 12.108416,
        "longitude": -86.256709,
        "locationNotes": "Edificio A, Piso 2.",
        "keywords": ["direccion de gestion del talento", "gestion del talento", "talento humano"]
    },
    {
        "placeId": "hrTalentA",
        "name": "Recursos Humanos (A205)",
        "category": CampusCategory.ADMINISTRATIVE,
        "parentBuildingId": "buildingA",
        "floorLevel": 2,
        "isAccessible": False,
        "latitude": 12.108416,
        "longitude": -86.256709,
        "locationNotes": "Edificio A, Piso 2.",
        "keywords": ["a205", "a-205", "a 205", "recursos humanos", "rrhh", "hr"]
    },
    # Floor 3 (exact order from buildings.txt — DPA / A301 belongs strictly to Building A)
    {
        "placeId": "dpaAudiovisualA",
        "name": "Dirección de Producción Audiovisual (DPA / A301)",
        "category": CampusCategory.CLASSROOM,
        "parentBuildingId": "buildingA",
        "floorLevel": 3,
        "isAccessible": False,
        "latitude": 12.108418,
        "longitude": -86.256706,
        "locationNotes": "Edificio A, Piso 3.",
        "keywords": ["dpa", "a301", "a-301", "a 301", "produccion audiovisual", "estudio audiovisual", "studioA301"]
    },
    {
        "placeId": "cycloramaSetA",
        "name": "Set de Grabación Ciclograma",
        "category": CampusCategory.CLASSROOM,
        "parentBuildingId": "buildingA",
        "floorLevel": 3,
        "isAccessible": False,
        "latitude": 12.108418,
        "longitude": -86.256706,
        "locationNotes": "Edificio A, Piso 3 (DPA).",
        "keywords": ["set de grabacion ciclograma", "ciclograma", "grabacion", "dpa"]
    },
    {
        "placeId": "soundStudioA",
        "name": "Estudio de Sonido",
        "category": CampusCategory.CLASSROOM,
        "parentBuildingId": "buildingA",
        "floorLevel": 3,
        "isAccessible": False,
        "latitude": 12.108418,
        "longitude": -86.256706,
        "locationNotes": "Edificio A, Piso 3 (DPA).",
        "keywords": ["estudio de sonido", "sonido", "audio", "dpa"]
    },
    {
        "placeId": "dpaAuxOfficesA",
        "name": "Oficinas Auxiliares DPA",
        "category": CampusCategory.ADMINISTRATIVE,
        "parentBuildingId": "buildingA",
        "floorLevel": 3,
        "isAccessible": False,
        "latitude": 12.108418,
        "longitude": -86.256706,
        "locationNotes": "Edificio A, Piso 3 (DPA).",
        "keywords": ["oficinas auxiliares dpa", "dpa"]
    },
    {
        "placeId": "masterControlA",
        "name": "Control Máster",
        "category": CampusCategory.CLASSROOM,
        "parentBuildingId": "buildingA",
        "floorLevel": 3,
        "isAccessible": False,
        "latitude": 12.108418,
        "longitude": -86.256706,
        "locationNotes": "Edificio A, Piso 3 (DPA).",
        "keywords": ["control master", "master", "dpa"]
    },
    {
        "placeId": "radioSetA",
        "name": "Set de Radio",
        "category": CampusCategory.CLASSROOM,
        "parentBuildingId": "buildingA",
        "floorLevel": 3,
        "isAccessible": False,
        "latitude": 12.108418,
        "longitude": -86.256706,
        "locationNotes": "Edificio A, Piso 3 (DPA).",
        "keywords": ["set de radio", "radio", "dpa"]
    },

    # -------------------------------------------------------------------------
    # BUILDING B: Main Classrooms B101-B210, Pharmacy & Photocopy (Floors 1 & 2)
    # -------------------------------------------------------------------------
    # Floor 1 (exact left-to-right order)
    {
        "placeId": "pharmacyB",
        "name": "Módulo Comercial 1 (Farmacia)",
        "category": CampusCategory.ADMINISTRATIVE,
        "parentBuildingId": "buildingB",
        "floorLevel": 1,
        "isAccessible": True,
        "latitude": 12.108563,
        "longitude": -86.256783,
        "locationNotes": "Edificio B, Piso 1, extremo izquierdo junto al Aula B101.",
        "keywords": ["farmacia", "farmacia del valle", "medicamentos", "modulo comercial 1"]
    },
    {
        "placeId": "classroomB101", "name": "Aula B101", "category": CampusCategory.CLASSROOM,
        "parentBuildingId": "buildingB", "floorLevel": 1, "isAccessible": True,
        "latitude": 12.108563, "longitude": -86.256783,
        "locationNotes": "Edificio B, Piso 1, junto a Farmacia.", "keywords": ["b101", "b-101", "b 101", "aula b101"]
    },
    {
        "placeId": "classroomB102", "name": "Aula B102", "category": CampusCategory.CLASSROOM,
        "parentBuildingId": "buildingB", "floorLevel": 1, "isAccessible": True,
        "latitude": 12.108574, "longitude": -86.256820,
        "locationNotes": "Edificio B, Piso 1.", "keywords": ["b102", "b-102", "b 102", "aula b102"]
    },
    {
        "placeId": "classroomB103", "name": "Aula B103", "category": CampusCategory.CLASSROOM,
        "parentBuildingId": "buildingB", "floorLevel": 1, "isAccessible": True,
        "latitude": 12.108585, "longitude": -86.256858,
        "locationNotes": "Edificio B, Piso 1.", "keywords": ["b103", "b-103", "b 103", "aula b103"]
    },
    {
        "placeId": "classroomB104", "name": "Aula B104", "category": CampusCategory.CLASSROOM,
        "parentBuildingId": "buildingB", "floorLevel": 1, "isAccessible": True,
        "latitude": 12.108585, "longitude": -86.256858,
        "locationNotes": "Edificio B, Piso 1.", "keywords": ["b104", "b-104", "b 104", "aula b104"]
    },
    {
        "placeId": "classroomB105", "name": "Aula B105", "category": CampusCategory.CLASSROOM,
        "parentBuildingId": "buildingB", "floorLevel": 1, "isAccessible": True,
        "latitude": 12.108568, "longitude": -86.256991,
        "locationNotes": "Edificio B, Piso 1, pasillo central.", "keywords": ["b105", "b-105", "b 105", "aula b105"]
    },
    {
        "placeId": "classroomB106", "name": "Aula B106", "category": CampusCategory.CLASSROOM,
        "parentBuildingId": "buildingB", "floorLevel": 1, "isAccessible": True,
        "latitude": 12.108568, "longitude": -86.256991,
        "locationNotes": "Edificio B, Piso 1, pasillo central.", "keywords": ["b106", "b-106", "b 106", "aula b106"]
    },
    {
        "placeId": "classroomB107", "name": "Aula B107", "category": CampusCategory.CLASSROOM,
        "parentBuildingId": "buildingB", "floorLevel": 1, "isAccessible": True,
        "latitude": 12.108610, "longitude": -86.257099,
        "locationNotes": "Edificio B, Piso 1.", "keywords": ["b107", "b-107", "b 107", "aula b107"]
    },
    {
        "placeId": "classroomB108", "name": "Aula B108", "category": CampusCategory.CLASSROOM,
        "parentBuildingId": "buildingB", "floorLevel": 1, "isAccessible": True,
        "latitude": 12.108575, "longitude": -86.257225,
        "locationNotes": "Edificio B, Piso 1.", "keywords": ["b108", "b-108", "b 108", "aula b108"]
    },
    {
        "placeId": "classroomB109", "name": "Aula B109", "category": CampusCategory.CLASSROOM,
        "parentBuildingId": "buildingB", "floorLevel": 1, "isAccessible": True,
        "latitude": 12.108575, "longitude": -86.257225,
        "locationNotes": "Edificio B, Piso 1.", "keywords": ["b109", "b-109", "b 109", "aula b109"]
    },
    {
        "placeId": "restroomsMenB1",
        "name": "Servicios Sanitarios Hombres (Edificio B)",
        "category": CampusCategory.RESTROOM,
        "parentBuildingId": "buildingB",
        "floorLevel": 1,
        "isAccessible": True,
        "latitude": 12.108590,
        "longitude": -86.257332,
        "locationNotes": "Edificio B, Piso 1.",
        "keywords": ["bano hombres b", "sanitarios hombres b", "sanitarios b", "bano"]
    },
    {
        "placeId": "drinkingFountainB1",
        "name": "Bebedero de Agua (Edificio B)",
        "category": CampusCategory.DRINKING_FOUNTAIN,
        "parentBuildingId": "buildingB",
        "floorLevel": 1,
        "isAccessible": True,
        "latitude": 12.108590,
        "longitude": -86.257332,
        "locationNotes": "Edificio B, Piso 1, entre baños de hombres y mujeres.",
        "keywords": ["bebedero", "agua", "tomar agua", "water fountain", "bebedero b"]
    },
    {
        "placeId": "restroomsWomenB1",
        "name": "Servicios Sanitarios Mujeres (Edificio B)",
        "category": CampusCategory.RESTROOM,
        "parentBuildingId": "buildingB",
        "floorLevel": 1,
        "isAccessible": True,
        "latitude": 12.108590,
        "longitude": -86.257332,
        "locationNotes": "Edificio B, Piso 1.",
        "keywords": ["bano mujeres b", "sanitarios mujeres b", "sanitarios b", "bano"]
    },
    {
        "placeId": "photocopyShopB",
        "name": "Fotocopias (Edificio B)",
        "category": CampusCategory.ADMINISTRATIVE,
        "parentBuildingId": "buildingB",
        "floorLevel": 1,
        "isAccessible": True,
        "latitude": 12.108590,
        "longitude": -86.257332,
        "locationNotes": "Edificio B, Piso 1, extremo del pasillo junto a sanitarios.",
        "keywords": ["fotocopias", "impresiones", "copias", "fotocopias b"]
    },
    {
        "placeId": "drinkingFountainBetweenBC",
        "name": "Bebedero de Agua (Entre Edificio C y B)",
        "category": CampusCategory.DRINKING_FOUNTAIN,
        "parentBuildingId": "buildingB",
        "floorLevel": 1,
        "isAccessible": True,
        "latitude": 12.108545,
        "longitude": -86.257057,
        "locationNotes": "Pasillo exterior entre Edificio C y Edificio B.",
        "keywords": ["bebedero entre b y c", "bebedero entre c y b", "agua b c", "bebedero exterior"]
    },
    # Floor 2 (exact left-to-right order: B201..B210)
    {
        "placeId": "classroomB201", "name": "Aula B201", "category": CampusCategory.CLASSROOM,
        "parentBuildingId": "buildingB", "floorLevel": 2, "isAccessible": False,
        "latitude": 12.108556, "longitude": -86.256730,
        "locationNotes": "Edificio B, Piso 2.", "keywords": ["b201", "b-201", "b 201", "aula b201"]
    },
    {
        "placeId": "classroomB202", "name": "Aula B202", "category": CampusCategory.CLASSROOM,
        "parentBuildingId": "buildingB", "floorLevel": 2, "isAccessible": False,
        "latitude": 12.108527, "longitude": -86.256795,
        "locationNotes": "Edificio B, Piso 2.", "keywords": ["b202", "b-202", "b 202", "aula b202"]
    },
    {
        "placeId": "classroomB203", "name": "Aula B203", "category": CampusCategory.CLASSROOM,
        "parentBuildingId": "buildingB", "floorLevel": 2, "isAccessible": False,
        "latitude": 12.108527, "longitude": -86.256795,
        "locationNotes": "Edificio B, Piso 2.", "keywords": ["b203", "b-203", "b 203", "aula b203"]
    },
    {
        "placeId": "classroomB204", "name": "Aula B204", "category": CampusCategory.CLASSROOM,
        "parentBuildingId": "buildingB", "floorLevel": 2, "isAccessible": False,
        "latitude": 12.108552, "longitude": -86.256826,
        "locationNotes": "Edificio B, Piso 2.", "keywords": ["b204", "b-204", "b 204", "aula b204"]
    },
    {
        "placeId": "classroomB205", "name": "Aula B205", "category": CampusCategory.CLASSROOM,
        "parentBuildingId": "buildingB", "floorLevel": 2, "isAccessible": False,
        "latitude": 12.108552, "longitude": -86.256826,
        "locationNotes": "Edificio B, Piso 2.", "keywords": ["b205", "b-205", "b 205", "aula b205"]
    },
    {
        "placeId": "classroomB206", "name": "Aula B206", "category": CampusCategory.CLASSROOM,
        "parentBuildingId": "buildingB", "floorLevel": 2, "isAccessible": False,
        "latitude": 12.108558, "longitude": -86.256985,
        "locationNotes": "Edificio B, Piso 2, pasillo central.", "keywords": ["b206", "b-206", "b 206", "aula b206"]
    },
    {
        "placeId": "classroomB207", "name": "Aula B207", "category": CampusCategory.CLASSROOM,
        "parentBuildingId": "buildingB", "floorLevel": 2, "isAccessible": False,
        "latitude": 12.108507, "longitude": -86.257117,
        "locationNotes": "Edificio B, Piso 2.", "keywords": ["b207", "b-207", "b 207", "aula b207"]
    },
    {
        "placeId": "classroomB208", "name": "Aula B208", "category": CampusCategory.CLASSROOM,
        "parentBuildingId": "buildingB", "floorLevel": 2, "isAccessible": False,
        "latitude": 12.108507, "longitude": -86.257117,
        "locationNotes": "Edificio B, Piso 2.", "keywords": ["b208", "b-208", "b 208", "aula b208"]
    },
    {
        "placeId": "classroomB209", "name": "Aula B209", "category": CampusCategory.CLASSROOM,
        "parentBuildingId": "buildingB", "floorLevel": 2, "isAccessible": False,
        "latitude": 12.108525, "longitude": -86.257271,
        "locationNotes": "Edificio B, Piso 2, junto a escaleras.", "keywords": ["b209", "b-209", "b 209", "aula b209"]
    },
    {
        "placeId": "classroomB210", "name": "Aula B210", "category": CampusCategory.CLASSROOM,
        "parentBuildingId": "buildingB", "floorLevel": 2, "isAccessible": False,
        "latitude": 12.108525, "longitude": -86.257271,
        "locationNotes": "Edificio B, Piso 2, junto a escaleras.", "keywords": ["b210", "b-210", "b 210", "aula b210"]
    },

    # -------------------------------------------------------------------------
    # BUILDING C: Classrooms, Computer Labs, Cashier & Treasury (Floors 1, 2, 3)
    # -------------------------------------------------------------------------
    # Floor 1 (exact left-to-right order)
    {
        "placeId": "auditoriumC101", "name": "Auditorio C101", "category": CampusCategory.AUDITORIUM,
        "parentBuildingId": "buildingC", "floorLevel": 1, "isAccessible": True,
        "latitude": 12.108528, "longitude": -86.256743,
        "locationNotes": "Edificio C, Piso 1, junto a escaleras izquierda.", "keywords": ["auditorio c101", "auditorio c", "c101", "c-101", "c 101"]
    },
    {
        "placeId": "classroomC102", "name": "Aula C102", "category": CampusCategory.CLASSROOM,
        "parentBuildingId": "buildingC", "floorLevel": 1, "isAccessible": True,
        "latitude": 12.108549, "longitude": -86.256848,
        "locationNotes": "Edificio C, Piso 1.", "keywords": ["c102", "c-102", "c 102", "aula c102"]
    },
    {
        "placeId": "classroomC103", "name": "Aula C103", "category": CampusCategory.CLASSROOM,
        "parentBuildingId": "buildingC", "floorLevel": 1, "isAccessible": True,
        "latitude": 12.108527, "longitude": -86.256908,
        "locationNotes": "Edificio C, Piso 1.", "keywords": ["c103", "c-103", "c 103", "aula c103"]
    },
    {
        "placeId": "classroomC104", "name": "Aula C104", "category": CampusCategory.CLASSROOM,
        "parentBuildingId": "buildingC", "floorLevel": 1, "isAccessible": True,
        "latitude": 12.108583, "longitude": -86.256918,
        "locationNotes": "Edificio C, Piso 1.", "keywords": ["c104", "c-104", "c 104", "aula c104"]
    },
    {
        "placeId": "treasuryC105", "name": "Tesorería UAM (C105)", "category": CampusCategory.ADMINISTRATIVE,
        "parentBuildingId": "buildingC", "floorLevel": 1, "isAccessible": True,
        "latitude": 12.108557, "longitude": -86.257120,
        "locationNotes": "Edificio C, Piso 1, oficina de tesorería.", "keywords": ["tesoreria", "c105", "c-105", "c 105", "tesoreria uam"]
    },
    {
        "placeId": "drinkingFountainC1", "name": "Bebedero de Agua (Edificio C - Piso 1)", "category": CampusCategory.DRINKING_FOUNTAIN,
        "parentBuildingId": "buildingC", "floorLevel": 1, "isAccessible": True,
        "latitude": 12.108527, "longitude": -86.256908,
        "locationNotes": "Edificio C, Piso 1, junto al Aula C103.", "keywords": ["bebedero c", "agua c", "bebedero c1"]
    },
    {
        "placeId": "cashierUamC", "name": "Caja UAM / Tesorería", "category": CampusCategory.ADMINISTRATIVE,
        "parentBuildingId": "buildingC", "floorLevel": 1, "isAccessible": True,
        "latitude": 12.108446, "longitude": -86.257021,
        "locationNotes": "Edificio C, Piso 1, vestíbulo central frente a rampa accesible.", "keywords": ["caja", "caja uam", "pagos", "aranceles", "colegiatura", "cashier"]
    },
    {
        "placeId": "classroomC106", "name": "Aula C106", "category": CampusCategory.CLASSROOM,
        "parentBuildingId": "buildingC", "floorLevel": 1, "isAccessible": True,
        "latitude": 12.108522, "longitude": -86.257194,
        "locationNotes": "Edificio C, Piso 1.", "keywords": ["c106", "c-106", "c 106", "aula c106"]
    },
    {
        "placeId": "macLabC107", "name": "Laboratorio MAC C107", "category": CampusCategory.CLASSROOM,
        "parentBuildingId": "buildingC", "floorLevel": 1, "isAccessible": True,
        "latitude": 12.108540, "longitude": -86.257206,
        "locationNotes": "Edificio C, Piso 1.", "keywords": ["mac 107", "lab mac", "computadoras apple", "c107", "c-107", "c 107"]
    },
    {
        "placeId": "erasmusLabC108", "name": "Laboratorio de Computación ACAI-Erasmus+ (C108)", "category": CampusCategory.CLASSROOM,
        "parentBuildingId": "buildingC", "floorLevel": 1, "isAccessible": True,
        "latitude": 12.108531, "longitude": -86.257233,
        "locationNotes": "Edificio C, Piso 1.", "keywords": ["erasmus", "acai", "c108", "c-108", "c 108", "lab computacion acai"]
    },
    {
        "placeId": "auditoriumC109", "name": "Auditorio C109", "category": CampusCategory.AUDITORIUM,
        "parentBuildingId": "buildingC", "floorLevel": 1, "isAccessible": True,
        "latitude": 12.108581, "longitude": -86.257279,
        "locationNotes": "Edificio C, Piso 1, junto a escaleras derecha.", "keywords": ["auditorio c109", "auditorio 109", "c109", "c-109", "c 109"]
    },
    {
        "placeId": "mapUamC_F1", "name": "Mapa UAM (Entrada Edificio C)", "category": CampusCategory.ADMINISTRATIVE,
        "parentBuildingId": "buildingC", "floorLevel": 1, "isAccessible": True,
        "latitude": 12.108446, "longitude": -86.257021,
        "locationNotes": "Edificio C, Piso 1, entrada y directorio.", "keywords": ["mapa", "mapa uam", "directorio edificio c"]
    },
    {
        "placeId": "rampC_F1", "name": "Rampa Accesible Edificio C", "category": CampusCategory.ACCESSIBLE_RAMP,
        "parentBuildingId": "buildingC", "floorLevel": 1, "isAccessible": True,
        "latitude": 12.108394, "longitude": -86.256997,
        "locationNotes": "Acceso accesible exterior frente a Caja UAM.", "keywords": ["rampa", "rampla", "rampa c", "rampa accesible edificio c"]
    },
    # Floor 2 (exact left-to-right order: C201..C211)
    {
        "placeId": "computerLabC201", "name": "Laboratorio de Computación C201", "category": CampusCategory.CLASSROOM,
        "parentBuildingId": "buildingC", "floorLevel": 2, "isAccessible": False,
        "latitude": 12.108453, "longitude": -86.256760,
        "locationNotes": "Edificio C, Piso 2.", "keywords": ["c201", "c-201", "c 201", "lab computo 201"]
    },
    {
        "placeId": "computerLabC202", "name": "Laboratorio de Computación C202", "category": CampusCategory.CLASSROOM,
        "parentBuildingId": "buildingC", "floorLevel": 2, "isAccessible": False,
        "latitude": 12.108415, "longitude": -86.256742,
        "locationNotes": "Edificio C, Piso 2.", "keywords": ["c202", "c-202", "c 202", "lab computo 202"]
    },
    {
        "placeId": "macLabC203", "name": "Laboratorio MAC C203", "category": CampusCategory.CLASSROOM,
        "parentBuildingId": "buildingC", "floorLevel": 2, "isAccessible": False,
        "latitude": 12.108528, "longitude": -86.256800,
        "locationNotes": "Edificio C, Piso 2.", "keywords": ["mac 203", "c203", "c-203", "c 203", "lab mac 203"]
    },
    {
        "placeId": "computerLabC204", "name": "Laboratorio de Computación C204", "category": CampusCategory.CLASSROOM,
        "parentBuildingId": "buildingC", "floorLevel": 2, "isAccessible": False,
        "latitude": 12.108510, "longitude": -86.256951,
        "locationNotes": "Edificio C, Piso 2.", "keywords": ["c204", "c-204", "c 204", "lab computo 204"]
    },
    {
        "placeId": "drinkingFountainC2", "name": "Bebedero de Agua (Edificio C - Piso 2)", "category": CampusCategory.DRINKING_FOUNTAIN,
        "parentBuildingId": "buildingC", "floorLevel": 2, "isAccessible": False,
        "latitude": 12.108510, "longitude": -86.256951,
        "locationNotes": "Edificio C, Piso 2, junto al Lab C204.", "keywords": ["bebedero c2", "agua c2", "bebedero piso 2"]
    },
    {
        "placeId": "computerLabC205", "name": "Laboratorio de Computación C205", "category": CampusCategory.CLASSROOM,
        "parentBuildingId": "buildingC", "floorLevel": 2, "isAccessible": False,
        "latitude": 12.108433, "longitude": -86.257043,
        "locationNotes": "Edificio C, Piso 2.", "keywords": ["c205", "c-205", "c 205", "lab computo 205"]
    },
    {
        "placeId": "warehouseC206", "name": "Bodega de Logística Académica (C206)", "category": CampusCategory.ADMINISTRATIVE,
        "parentBuildingId": "buildingC", "floorLevel": 2, "isAccessible": False,
        "latitude": 12.108435, "longitude": -86.257044,
        "locationNotes": "Edificio C, Piso 2.", "keywords": ["c206", "c-206", "c 206", "bodega", "logistica academica"]
    },
    {
        "placeId": "restroomsMenC2", "name": "Servicios Sanitarios Hombres (Edificio C - Piso 2)", "category": CampusCategory.RESTROOM,
        "parentBuildingId": "buildingC", "floorLevel": 2, "isAccessible": False,
        "latitude": 12.108423, "longitude": -86.257051,
        "locationNotes": "Edificio C, Piso 2.", "keywords": ["baños hombres c", "banos hombres c", "sanitarios hombres c"]
    },
    {
        "placeId": "restroomsWomenC2", "name": "Servicios Sanitarios Mujeres (Edificio C - Piso 2)", "category": CampusCategory.RESTROOM,
        "parentBuildingId": "buildingC", "floorLevel": 2, "isAccessible": False,
        "latitude": 12.108423, "longitude": -86.257051,
        "locationNotes": "Edificio C, Piso 2.", "keywords": ["baños mujeres c", "banos mujeres c", "sanitarios mujeres c"]
    },
    {
        "placeId": "classroomC209", "name": "Aula C209", "category": CampusCategory.CLASSROOM,
        "parentBuildingId": "buildingC", "floorLevel": 2, "isAccessible": False,
        "latitude": 12.108496, "longitude": -86.257203,
        "locationNotes": "Edificio C, Piso 2.", "keywords": ["c209", "c-209", "c 209", "aula c209"]
    },
    {
        "placeId": "classroomC210", "name": "Aula C210", "category": CampusCategory.CLASSROOM,
        "parentBuildingId": "buildingC", "floorLevel": 2, "isAccessible": False,
        "latitude": 12.108491, "longitude": -86.257192,
        "locationNotes": "Edificio C, Piso 2.", "keywords": ["c210", "c-210", "c 210", "aula c210"]
    },
    {
        "placeId": "classroomC211", "name": "Aula C211", "category": CampusCategory.CLASSROOM,
        "parentBuildingId": "buildingC", "floorLevel": 2, "isAccessible": False,
        "latitude": 12.108500, "longitude": -86.257267,
        "locationNotes": "Edificio C, Piso 2, junto a escaleras derecha.", "keywords": ["c211", "c-211", "c 211", "aula c211"]
    },
    # Floor 3 (exact left-to-right order: C301..C310)
    {
        "placeId": "classroomC301", "name": "Aula C301", "category": CampusCategory.CLASSROOM,
        "parentBuildingId": "buildingC", "floorLevel": 3, "isAccessible": False,
        "latitude": 12.108406, "longitude": -86.256819,
        "locationNotes": "Edificio C, Piso 3.", "keywords": ["c301", "c-301", "c 301", "aula c301"]
    },
    {
        "placeId": "classroomC302", "name": "Aula C302", "category": CampusCategory.CLASSROOM,
        "parentBuildingId": "buildingC", "floorLevel": 3, "isAccessible": False,
        "latitude": 12.108418, "longitude": -86.256821,
        "locationNotes": "Edificio C, Piso 3.", "keywords": ["c302", "c-302", "c 302", "aula c302"]
    },
    {
        "placeId": "classroomC303", "name": "Aula C303", "category": CampusCategory.CLASSROOM,
        "parentBuildingId": "buildingC", "floorLevel": 3, "isAccessible": False,
        "latitude": 12.108434, "longitude": -86.256861,
        "locationNotes": "Edificio C, Piso 3.", "keywords": ["c303", "c-303", "c 303", "aula c303"]
    },
    {
        "placeId": "classroomC304", "name": "Aula C304", "category": CampusCategory.CLASSROOM,
        "parentBuildingId": "buildingC", "floorLevel": 3, "isAccessible": False,
        "latitude": 12.108415, "longitude": -86.257020,
        "locationNotes": "Edificio C, Piso 3.", "keywords": ["c304", "c-304", "c 304", "aula c304"]
    },
    {
        "placeId": "classroomC305", "name": "Aula C305", "category": CampusCategory.CLASSROOM,
        "parentBuildingId": "buildingC", "floorLevel": 3, "isAccessible": False,
        "latitude": 12.108408, "longitude": -86.257028,
        "locationNotes": "Edificio C, Piso 3, entre C304 y Coordinación de Compras.", "keywords": ["c305", "c-305", "c 305", "aula c305"]
    },
    {
        "placeId": "procurementCoordC306", "name": "Coordinación de Compras (C306)", "category": CampusCategory.ADMINISTRATIVE,
        "parentBuildingId": "buildingC", "floorLevel": 3, "isAccessible": False,
        "latitude": 12.108402, "longitude": -86.257035,
        "locationNotes": "Edificio C, Piso 3, departamento de compras.", "keywords": ["compras", "c306", "c-306", "c 306", "coordinacion de compras"]
    },
    {
        "placeId": "classroomC307", "name": "Aula C307", "category": CampusCategory.CLASSROOM,
        "parentBuildingId": "buildingC", "floorLevel": 3, "isAccessible": False,
        "latitude": 12.108395, "longitude": -86.257064,
        "locationNotes": "Edificio C, Piso 3.", "keywords": ["c307", "c-307", "c 307", "aula c307"]
    },
    {
        "placeId": "classroomC308", "name": "Aula C308", "category": CampusCategory.CLASSROOM,
        "parentBuildingId": "buildingC", "floorLevel": 3, "isAccessible": False,
        "latitude": 12.108397, "longitude": -86.257083,
        "locationNotes": "Edificio C, Piso 3.", "keywords": ["c308", "c-308", "c 308", "aula c308"]
    },
    {
        "placeId": "classroomC309", "name": "Aula C309", "category": CampusCategory.CLASSROOM,
        "parentBuildingId": "buildingC", "floorLevel": 3, "isAccessible": False,
        "latitude": 12.108420, "longitude": -86.257240,
        "locationNotes": "Edificio C, Piso 3.", "keywords": ["c309", "c-309", "c 309", "aula c309"]
    },
    {
        "placeId": "classroomC310", "name": "Aula C310", "category": CampusCategory.CLASSROOM,
        "parentBuildingId": "buildingC", "floorLevel": 3, "isAccessible": False,
        "latitude": 12.108376, "longitude": -86.257292,
        "locationNotes": "Edificio C, Piso 3, junto a escaleras derecha.", "keywords": ["c310", "c-310", "c 310", "aula c310"]
    },

    # -------------------------------------------------------------------------
    # BUILDING D: Digital Dentistry (1 Floor — exact order from buildings.txt)
    # -------------------------------------------------------------------------
    {
        "placeId": "classroomD102", "name": "Aula D102", "category": CampusCategory.CLASSROOM,
        "parentBuildingId": "buildingD", "floorLevel": 1, "isAccessible": True,
        "latitude": 12.108029, "longitude": -86.256911,
        "locationNotes": "Edificio D, Planta Única.", "keywords": ["d102", "d-102", "d 102", "aula d102", "salon d102"]
    },
    {
        "placeId": "camCamLabD", "name": "Laboratorio de Odontología Digital CAM-CAM", "category": CampusCategory.DENTAL_LAB,
        "parentBuildingId": "buildingD", "floorLevel": 1, "isAccessible": True,
        "latitude": 12.108046, "longitude": -86.256819,
        "locationNotes": "Edificio D, Planta Única.", "keywords": ["cam cam", "cam-cam", "odontologia digital", "cad cam", "lab d"]
    },
    {
        "placeId": "customerServiceD", "name": "Oficina de Servicio al Cliente", "category": CampusCategory.ADMINISTRATIVE,
        "parentBuildingId": "buildingD", "floorLevel": 1, "isAccessible": True,
        "latitude": 12.108128, "longitude": -86.256945,
        "locationNotes": "Edificio D, Planta Única.", "keywords": ["servicio al cliente", "oficina de servicio al cliente", "atencion d"]
    },
    {
        "placeId": "meetingRoomD", "name": "Sala de Reunión (Edificio D)", "category": CampusCategory.ADMINISTRATIVE,
        "parentBuildingId": "buildingD", "floorLevel": 1, "isAccessible": True,
        "latitude": 12.108128, "longitude": -86.256945,
        "locationNotes": "Edificio D, Planta Única.", "keywords": ["sala de reunion", "sala de reuniones", "reunion d"]
    },
    {
        "placeId": "uamMapD", "name": "Mapa UAM (Entrada Edificio D)", "category": CampusCategory.ADMINISTRATIVE,
        "parentBuildingId": "buildingD", "floorLevel": 1, "isAccessible": True,
        "latitude": 12.108128, "longitude": -86.256945,
        "locationNotes": "Edificio D, Entrada principal.", "keywords": ["mapa uam", "mapa d", "directorio d"]
    },

    # -------------------------------------------------------------------------
    # BUILDING E: Medical Sciences & Clinics (Floors 1 & 2 — exact order)
    # -------------------------------------------------------------------------
    # Floor 1
    {
        "placeId": "medicalClinicsE", "name": "Clínicas Médicas", "category": CampusCategory.MEDICAL_LAB,
        "parentBuildingId": "buildingE", "floorLevel": 1, "isAccessible": True,
        "latitude": 12.108882, "longitude": -86.257119,
        "locationNotes": "Edificio E, Piso 1.", "keywords": ["clinicas medicas", "clinica medica", "consulta medica", "medicina"]
    },
    {
        "placeId": "restroomsMenE", "name": "Servicios Sanitarios Hombres (Edificio E)", "category": CampusCategory.RESTROOM,
        "parentBuildingId": "buildingE", "floorLevel": 1, "isAccessible": True,
        "latitude": 12.109072, "longitude": -86.257603,
        "locationNotes": "Edificio E, Piso 1.", "keywords": ["bano hombres e", "sanitarios hombres e", "banos e"]
    },
    {
        "placeId": "restroomsWomenE", "name": "Servicios Sanitarios Mujeres (Edificio E)", "category": CampusCategory.RESTROOM,
        "parentBuildingId": "buildingE", "floorLevel": 1, "isAccessible": True,
        "latitude": 12.109072, "longitude": -86.257603,
        "locationNotes": "Edificio E, Piso 1.", "keywords": ["bano mujeres e", "sanitarios mujeres e", "banos e"]
    },
    {
        "placeId": "accessibleRestroomE", "name": "Servicios Sanitarios Personas con Discapacidades Mixtos (Edificio E)", "category": CampusCategory.RESTROOM,
        "parentBuildingId": "buildingE", "floorLevel": 1, "isAccessible": True,
        "latitude": 12.109072, "longitude": -86.257603,
        "locationNotes": "Edificio E, Piso 1, junto a sanitarios generales.", "keywords": ["bano discapacitados", "bano accesible", "bano silla de ruedas", "sanitarios mixtos e"]
    },
    {
        "placeId": "cardiologyCenterE", "name": "Centro de Cardiología", "category": CampusCategory.MEDICAL_LAB,
        "parentBuildingId": "buildingE", "floorLevel": 1, "isAccessible": True,
        "latitude": 12.109062, "longitude": -86.257375,
        "locationNotes": "Edificio E, Piso 1.", "keywords": ["cardiologia", "centro de cardiologia", "corazon"]
    },
    {
        "placeId": "facultyMedicineE", "name": "Facultad de Ciencias Médicas", "category": CampusCategory.FACULTY,
        "parentBuildingId": "buildingE", "floorLevel": 1, "isAccessible": True,
        "latitude": 12.109346, "longitude": -86.257217,
        "locationNotes": "Edificio E, Piso 1, decanatura.", "keywords": ["facultad de medicina", "ciencias medicas", "decanatura medicina"]
    },
    {
        "placeId": "studentLifeOfficeE", "name": "Dirección de Vida Estudiantil (Anexo Oeste)", "category": CampusCategory.ADMINISTRATIVE,
        "parentBuildingId": "buildingE", "floorLevel": 1, "isAccessible": True,
        "latitude": 12.109081, "longitude": -86.257416,
        "locationNotes": "Edificio E, Piso 1, anexo oeste.", "keywords": ["vida estudiantil", "dve", "asuntos estudiantiles"]
    },
    {
        "placeId": "innovationOfficeE", "name": "Dirección de Innovación y Emprendimientos (DIE) (Anexo Norte)", "category": CampusCategory.ADMINISTRATIVE,
        "parentBuildingId": "buildingE", "floorLevel": 1, "isAccessible": True,
        "latitude": 12.109312, "longitude": -86.257369,
        "locationNotes": "Edificio E, Piso 1, anexo norte.", "keywords": ["die", "innovacion", "emprendimiento", "emprendimientos"]
    },
    {
        "placeId": "benchesE", "name": "Bancas (Edificio E)", "category": CampusCategory.FOOD_AREA,
        "parentBuildingId": "buildingE", "floorLevel": 1, "isAccessible": True,
        "latitude": 12.109055, "longitude": -86.257355,
        "locationNotes": "Edificio E, Piso 1, área de descanso.", "keywords": ["bancas", "bancas e", "descanso e"]
    },
    # Floor 2 (exact order from buildings.txt)
    {
        "placeId": "medicalSimulatorsE2", "name": "Laboratorio Simuladores de Habilidades Medicina (E201)", "category": CampusCategory.MEDICAL_LAB,
        "parentBuildingId": "buildingE", "floorLevel": 2, "isAccessible": False,
        "latitude": 12.108874, "longitude": -86.257213,
        "locationNotes": "Edificio E, Piso 2 (Centro de Simulación E201).", "keywords": ["e201", "e-201", "e 201", "simuladores", "simuladores medicina", "centro de simulacion", "lab habilidades"]
    },
    {
        "placeId": "medicalSimulatorsWardE2", "name": "Laboratorio Simuladores de Medicina (Pediatría, Neonatología y Salas de Control)", "category": CampusCategory.MEDICAL_LAB,
        "parentBuildingId": "buildingE", "floorLevel": 2, "isAccessible": False,
        "latitude": 12.108902, "longitude": -86.257221,
        "locationNotes": "Edificio E, Piso 2, Pediatría, Neonatología, Salas de Control 1 y 2, Cuidados Médicos.", "keywords": ["laboratorio simuladores de medicina", "pediatria", "neonatologia", "sala de control", "cuidados medicos"]
    },
    {
        "placeId": "psychologyOfficeE", "name": "Oficina Psicología", "category": CampusCategory.ADMINISTRATIVE,
        "parentBuildingId": "buildingE", "floorLevel": 2, "isAccessible": False,
        "latitude": 12.109180, "longitude": -86.257158,
        "locationNotes": "Edificio E, Piso 2.", "keywords": ["oficina psicologia", "oficina de psicologia", "psicologia", "psicologa"]
    },
    {
        "placeId": "clinicalMedicineLabE", "name": "Laboratorio Clínico de Medicina", "category": CampusCategory.MEDICAL_LAB,
        "parentBuildingId": "buildingE", "floorLevel": 2, "isAccessible": False,
        "latitude": 12.109286, "longitude": -86.257194,
        "locationNotes": "Edificio E, Piso 2.", "keywords": ["laboratorio clinico de medicina", "laboratorio clinico", "lab clinico"]
    },

    # -------------------------------------------------------------------------
    # BUILDING F: Business, Economics & Marketing (1 Floor — exact order)
    # -------------------------------------------------------------------------
    {
        "placeId": "teachersLoungeF", "name": "Salón de Profesores (Edificio F)", "category": CampusCategory.FACULTY,
        "parentBuildingId": "buildingF", "floorLevel": 1, "isAccessible": True,
        "latitude": 12.108908, "longitude": -86.257390,
        "locationNotes": "Edificio F, Planta Única.", "keywords": ["salon de profesores", "profesores f"]
    },
    {
        "placeId": "postgraduateDirectorateF", "name": "Dirección de Posgrados y Educación Continua", "category": CampusCategory.ADMINISTRATIVE,
        "parentBuildingId": "buildingF", "floorLevel": 1, "isAccessible": True,
        "latitude": 12.108939, "longitude": -86.257347,
        "locationNotes": "Edificio F, Planta Única.", "keywords": ["posgrados", "maestrias", "educacion continua"]
    },
    {
        "placeId": "facultyBusinessF", "name": "Facultad de Ciencias Administrativas y Económicas (FCAE)", "category": CampusCategory.FACULTY,
        "parentBuildingId": "buildingF", "floorLevel": 1, "isAccessible": True,
        "latitude": 12.108938, "longitude": -86.257431,
        "locationNotes": "Edificio F, Planta Única.", "keywords": ["fcae", "administracion", "economia", "facultad de administracion"]
    },
    {
        "placeId": "facultyMarketingF", "name": "Facultad de Marketing, Diseño y Ciencias de la Comunicación (FMDCC)", "category": CampusCategory.FACULTY,
        "parentBuildingId": "buildingF", "floorLevel": 1, "isAccessible": True,
        "latitude": 12.109078, "longitude": -86.257563,
        "locationNotes": "Edificio F, Planta Única.", "keywords": ["fmdcc", "marketing", "diseno", "comunicacion"]
    },

    # -------------------------------------------------------------------------
    # BUILDING G: Law School FCJHRI & Central Auditorium (Floors 1 & 2)
    # -------------------------------------------------------------------------
    # Floor 1 (exact order)
    {
        "placeId": "facultyLawG", "name": "Facultad de Ciencias Jurídicas, Humanidades y Relaciones Internacionales (FCJHRI)", "category": CampusCategory.FACULTY,
        "parentBuildingId": "buildingG", "floorLevel": 1, "isAccessible": True,
        "latitude": 12.108630, "longitude": -86.257479,
        "locationNotes": "Edificio G, Piso 1.", "keywords": ["derecho", "humanidades", "relaciones internacionales", "juridicas", "fcjhri"]
    },
    {
        "placeId": "auditoriumFcjhriG", "name": "Auditorio FCJHRI", "category": CampusCategory.AUDITORIUM,
        "parentBuildingId": "buildingG", "floorLevel": 1, "isAccessible": True,
        "latitude": 12.108630, "longitude": -86.257479,
        "locationNotes": "Edificio G, Piso 1.", "keywords": ["auditorio fcjhri", "fcjhri", "auditorio derecho"]
    },
    {
        "placeId": "mediationCenterG", "name": "Centro de Mediación y Arbitraje", "category": CampusCategory.ADMINISTRATIVE,
        "parentBuildingId": "buildingG", "floorLevel": 1, "isAccessible": True,
        "latitude": 12.108630, "longitude": -86.257479,
        "locationNotes": "Edificio G, Piso 1.", "keywords": ["centro de mediacion y arbitraje", "centro de mediacion", "arbitraje", "mediacion"]
    },
    {
        "placeId": "languageCenterG", "name": "Language Center", "category": CampusCategory.CLASSROOM,
        "parentBuildingId": "buildingG", "floorLevel": 1, "isAccessible": True,
        "latitude": 12.108779, "longitude": -86.257498,
        "locationNotes": "Edificio G, Piso 1.", "keywords": ["language center", "ingles", "idiomas"]
    },
    {
        "placeId": "uamCollegeG", "name": "UAM College", "category": CampusCategory.FACULTY,
        "parentBuildingId": "buildingG", "floorLevel": 1, "isAccessible": True,
        "latitude": 12.108779, "longitude": -86.257498,
        "locationNotes": "Edificio G, Piso 1.", "keywords": ["uam college", "college"]
    },
    {
        "placeId": "intlRelationsG", "name": "Dirección de Relaciones Internacionales e Internacionalización", "category": CampusCategory.ADMINISTRATIVE,
        "parentBuildingId": "buildingG", "floorLevel": 1, "isAccessible": True,
        "latitude": 12.108779, "longitude": -86.257498,
        "locationNotes": "Edificio G, Piso 1.", "keywords": ["direccion de relaciones internacionales e internacionalizacion", "relaciones internacionales", "internacionalizacion"]
    },
    {
        "placeId": "mixedRestroomG", "name": "Baños Mixtos (Edificio G)", "category": CampusCategory.RESTROOM,
        "parentBuildingId": "buildingG", "floorLevel": 1, "isAccessible": True,
        "latitude": 12.108652, "longitude": -86.257520,
        "locationNotes": "Edificio G, Piso 1.", "keywords": ["banos mixtos", "banos g", "sanitarios g"]
    },
    {
        "placeId": "accessibleRestroomG", "name": "Baños para Personas con Discapacidades Mixtos (Edificio G)", "category": CampusCategory.RESTROOM,
        "parentBuildingId": "buildingG", "floorLevel": 1, "isAccessible": True,
        "latitude": 12.108652, "longitude": -86.257520,
        "locationNotes": "Edificio G, Piso 1.", "keywords": ["bano accesible g", "bano silla de ruedas g", "banos para personas con discapacidades mixtos"]
    },
    # Floor 2
    {
        "placeId": "auditoriumCentralG", "name": "Auditorio Central / Auditorio Rubén Darío", "category": CampusCategory.AUDITORIUM,
        "parentBuildingId": "buildingG", "floorLevel": 2, "isAccessible": True,
        "latitude": 12.108695, "longitude": -86.257600,
        "locationNotes": "Edificio G, Piso 2.", "keywords": ["auditorio central", "ruben dario", "auditorio ruben dario", "auditorio g", "graduaciones"]
    },

    # -------------------------------------------------------------------------
    # BUILDING H: Medical Laboratories (H101-H107 Floor 1, H201-H207 Floor 2)
    # -------------------------------------------------------------------------
    # Floor 1 (exact order from buildings.txt)
    {
        "placeId": "restroomsMenH1", "name": "Baños Hombres (Edificio H)", "category": CampusCategory.RESTROOM,
        "parentBuildingId": "buildingH", "floorLevel": 1, "isAccessible": True,
        "latitude": 12.108255, "longitude": -86.257537,
        "locationNotes": "Edificio H, Piso 1.", "keywords": ["banos hombres h", "banos h", "sanitarios h"]
    },
    {
        "placeId": "restroomsWomenH1", "name": "Baños Mujeres (Edificio H)", "category": CampusCategory.RESTROOM,
        "parentBuildingId": "buildingH", "floorLevel": 1, "isAccessible": True,
        "latitude": 12.108255, "longitude": -86.257537,
        "locationNotes": "Edificio H, Piso 1.", "keywords": ["banos mujeres h", "banos h", "sanitarios h"]
    },
    {
        "placeId": "medicalLabH101", "name": "Laboratorio de Medicina H101", "category": CampusCategory.MEDICAL_LAB,
        "parentBuildingId": "buildingH", "floorLevel": 1, "isAccessible": True,
        "latitude": 12.108272, "longitude": -86.257569,
        "locationNotes": "Edificio H, Piso 1.", "keywords": ["h101", "h-101", "h 101", "lab med h101"]
    },
    {
        "placeId": "medicalLabH102", "name": "Laboratorio de Medicina H102", "category": CampusCategory.MEDICAL_LAB,
        "parentBuildingId": "buildingH", "floorLevel": 1, "isAccessible": True,
        "latitude": 12.108265, "longitude": -86.257549,
        "locationNotes": "Edificio H, Piso 1.", "keywords": ["h102", "h-102", "h 102", "lab med h102"]
    },
    {
        "placeId": "medicalLabH103", "name": "Laboratorio de Medicina H103", "category": CampusCategory.MEDICAL_LAB,
        "parentBuildingId": "buildingH", "floorLevel": 1, "isAccessible": True,
        "latitude": 12.108265, "longitude": -86.257549,
        "locationNotes": "Edificio H, Piso 1.", "keywords": ["h103", "h-103", "h 103", "lab med h103"]
    },
    {
        "placeId": "medicalLabH104", "name": "Coordinación de Gestión de Calidad (Laboratorio H104)", "category": CampusCategory.MEDICAL_LAB,
        "parentBuildingId": "buildingH", "floorLevel": 1, "isAccessible": True,
        "latitude": 12.108263, "longitude": -86.257695,
        "locationNotes": "Edificio H, Piso 1.", "keywords": ["h104", "h-104", "h 104", "lab med h104", "coordinacion de gestion de calidad", "gestion de calidad"]
    },
    {
        "placeId": "labSupervisionOfficeH", "name": "Oficina de Supervisión de Laboratorios de Medicina (Necroteca)", "category": CampusCategory.MEDICAL_LAB,
        "parentBuildingId": "buildingH", "floorLevel": 1, "isAccessible": True,
        "latitude": 12.108304, "longitude": -86.257660,
        "locationNotes": "Edificio H, Piso 1, Supervisión de Laboratorios y acceso Necroteca.", "keywords": ["oficina de supervision de laboratorios de medicina", "supervision laboratorios", "necroteca"]
    },
    {
        "placeId": "medicalLabH105", "name": "Laboratorio de Medicina H105", "category": CampusCategory.MEDICAL_LAB,
        "parentBuildingId": "buildingH", "floorLevel": 1, "isAccessible": True,
        "latitude": 12.108200, "longitude": -86.257812,
        "locationNotes": "Edificio H, Piso 1.", "keywords": ["h105", "h-105", "h 105", "lab med h105"]
    },
    {
        "placeId": "medicalLabH106", "name": "Laboratorio de Medicina H106", "category": CampusCategory.MEDICAL_LAB,
        "parentBuildingId": "buildingH", "floorLevel": 1, "isAccessible": True,
        "latitude": 12.108156, "longitude": -86.257708,
        "locationNotes": "Edificio H, Piso 1.", "keywords": ["h106", "h-106", "h 106", "lab med h106"]
    },
    {
        "placeId": "medicalLabH107", "name": "Laboratorio de Medicina H107", "category": CampusCategory.MEDICAL_LAB,
        "parentBuildingId": "buildingH", "floorLevel": 1, "isAccessible": True,
        "latitude": 12.108156, "longitude": -86.257708,
        "locationNotes": "Edificio H, Piso 1.", "keywords": ["h107", "h-107", "h 107", "lab med h107"]
    },
    {
        "placeId": "foodScienceLabH", "name": "Laboratorio de Ciencias de los Alimentos", "category": CampusCategory.MEDICAL_LAB,
        "parentBuildingId": "buildingH", "floorLevel": 1, "isAccessible": True,
        "latitude": 12.108156, "longitude": -86.257647,
        "locationNotes": "Edificio H, Piso 1.", "keywords": ["ciencias de los alimentos", "laboratorio de ciencias de los alimentos"]
    },
    # Floor 2 (exact order: H201..H207)
    {
        "placeId": "medicalLabH201", "name": "Laboratorio de Medicina H201", "category": CampusCategory.MEDICAL_LAB,
        "parentBuildingId": "buildingH", "floorLevel": 2, "isAccessible": False,
        "latitude": 12.108236, "longitude": -86.257552,
        "locationNotes": "Edificio H, Piso 2.", "keywords": ["h201", "h-201", "h 201", "lab med h201"]
    },
    {
        "placeId": "medicalLabH202", "name": "Laboratorio de Medicina H202", "category": CampusCategory.MEDICAL_LAB,
        "parentBuildingId": "buildingH", "floorLevel": 2, "isAccessible": False,
        "latitude": 12.108231, "longitude": -86.257608,
        "locationNotes": "Edificio H, Piso 2.", "keywords": ["h202", "h-202", "h 202", "lab med h202"]
    },
    {
        "placeId": "medicalLabH203", "name": "Laboratorio de Medicina H203", "category": CampusCategory.MEDICAL_LAB,
        "parentBuildingId": "buildingH", "floorLevel": 2, "isAccessible": False,
        "latitude": 12.108270, "longitude": -86.257560,
        "locationNotes": "Edificio H, Piso 2.", "keywords": ["h203", "h-203", "h 203", "lab med h203"]
    },
    {
        "placeId": "medicalLabH204", "name": "Laboratorio de Medicina H204", "category": CampusCategory.MEDICAL_LAB,
        "parentBuildingId": "buildingH", "floorLevel": 2, "isAccessible": False,
        "latitude": 12.108270, "longitude": -86.257560,
        "locationNotes": "Edificio H, Piso 2.", "keywords": ["h204", "h-204", "h 204", "lab med h204"]
    },
    {
        "placeId": "medicalLabH205", "name": "Laboratorio de Medicina H205", "category": CampusCategory.MEDICAL_LAB,
        "parentBuildingId": "buildingH", "floorLevel": 2, "isAccessible": False,
        "latitude": 12.108211, "longitude": -86.257727,
        "locationNotes": "Edificio H, Piso 2.", "keywords": ["h205", "h-205", "h 205", "lab med h205"]
    },
    {
        "placeId": "medicalLabH206", "name": "Laboratorio de Medicina H206", "category": CampusCategory.MEDICAL_LAB,
        "parentBuildingId": "buildingH", "floorLevel": 2, "isAccessible": False,
        "latitude": 12.108211, "longitude": -86.257727,
        "locationNotes": "Edificio H, Piso 2.", "keywords": ["h206", "h-206", "h 206", "lab med h206"]
    },
    {
        "placeId": "medicalLabH207", "name": "Laboratorio de Medicina H207", "category": CampusCategory.MEDICAL_LAB,
        "parentBuildingId": "buildingH", "floorLevel": 2, "isAccessible": False,
        "latitude": 12.108211, "longitude": -86.257727,
        "locationNotes": "Edificio H, Piso 2.", "keywords": ["h207", "h-207", "h 207", "lab med h207"]
    },

    # -------------------------------------------------------------------------
    # BUILDING I: Rectorate & Central Library (1 Floor — exact order)
    # -------------------------------------------------------------------------
    {
        "placeId": "vicePresidencyI", "name": "Vicepresidencia y Mapa UAM", "category": CampusCategory.ADMINISTRATIVE,
        "parentBuildingId": "buildingI", "floorLevel": 1, "isAccessible": True,
        "latitude": 12.109119, "longitude": -86.257918,
        "locationNotes": "Edificio I, Piso 1.", "keywords": ["vicepresidencia", "mapa uam i"]
    },
    {
        "placeId": "directorsMeetingRoomI", "name": "Sala de Reunión Directores", "category": CampusCategory.ADMINISTRATIVE,
        "parentBuildingId": "buildingI", "floorLevel": 1, "isAccessible": True,
        "latitude": 12.109255, "longitude": -86.258170,
        "locationNotes": "Edificio I, Piso 1.", "keywords": ["sala de reunion directores", "sala de directores", "presidencia uam"]
    },
    {
        "placeId": "academicDirectorateI", "name": "Dirección Académica (Edificio I)", "category": CampusCategory.ADMINISTRATIVE,
        "parentBuildingId": "buildingI", "floorLevel": 1, "isAccessible": True,
        "latitude": 12.109152, "longitude": -86.257914,
        "locationNotes": "Edificio I, Piso 1.", "keywords": ["direccion academica i", "direccion academica"]
    },
    {
        "placeId": "rectorateOfficeI", "name": "Rectoría", "category": CampusCategory.ADMINISTRATIVE,
        "parentBuildingId": "buildingI", "floorLevel": 1, "isAccessible": True,
        "latitude": 12.109237, "longitude": -86.258051,
        "locationNotes": "Edificio I, Piso 1, ala ejecutiva.", "keywords": ["rectoria", "rector", "rectoria uam"]
    },
    {
        "placeId": "generalManagementI", "name": "Gerencia General", "category": CampusCategory.ADMINISTRATIVE,
        "parentBuildingId": "buildingI", "floorLevel": 1, "isAccessible": True,
        "latitude": 12.109237, "longitude": -86.258051,
        "locationNotes": "Edificio I, Piso 1.", "keywords": ["gerencia general", "gerencia"]
    },
    {
        "placeId": "generalSecretariatI", "name": "Secretaría General", "category": CampusCategory.ADMINISTRATIVE,
        "parentBuildingId": "buildingI", "floorLevel": 1, "isAccessible": True,
        "latitude": 12.109237, "longitude": -86.258051,
        "locationNotes": "Edificio I, Piso 1.", "keywords": ["secretaria general", "secretaria"]
    },
    {
        "placeId": "meetingRoomI", "name": "Oficina / Sala de Reunión (Edificio I)", "category": CampusCategory.ADMINISTRATIVE,
        "parentBuildingId": "buildingI", "floorLevel": 1, "isAccessible": True,
        "latitude": 12.109237, "longitude": -86.258051,
        "locationNotes": "Edificio I, Piso 1.", "keywords": ["oficina sala de reunion", "sala de reunion i"]
    },
    {
        "placeId": "centralLibraryI", "name": "Biblioteca Pablo Antonio Cuadra", "category": CampusCategory.ADMINISTRATIVE,
        "parentBuildingId": "buildingI", "floorLevel": 1, "isAccessible": True,
        "latitude": 12.109547, "longitude": -86.257996,
        "locationNotes": "Edificio I, Piso 1, acceso biblioteca.", "keywords": ["biblioteca", "biblioteca central", "pablo antonio cuadra", "libros", "estudiar", "library"]
    },
    {
        "placeId": "restroomsLibraryMenI", "name": "Baños Biblioteca Hombres", "category": CampusCategory.RESTROOM,
        "parentBuildingId": "buildingI", "floorLevel": 1, "isAccessible": True,
        "latitude": 12.109526, "longitude": -86.258323,
        "locationNotes": "Edificio I, Biblioteca, izquierda hombres.", "keywords": ["banos biblioteca hombre", "banos biblioteca", "sanitarios biblioteca"]
    },
    {
        "placeId": "restroomsLibraryWomenI", "name": "Baños Biblioteca Mujeres", "category": CampusCategory.RESTROOM,
        "parentBuildingId": "buildingI", "floorLevel": 1, "isAccessible": True,
        "latitude": 12.109526, "longitude": -86.258323,
        "locationNotes": "Edificio I, Biblioteca, derecha mujeres.", "keywords": ["banos biblioteca mujer", "banos biblioteca", "sanitarios biblioteca"]
    },
    {
        "placeId": "publicRelationsI", "name": "Dirección de Relaciones Públicas", "category": CampusCategory.ADMINISTRATIVE,
        "parentBuildingId": "buildingI", "floorLevel": 1, "isAccessible": True,
        "latitude": 12.109255, "longitude": -86.258170,
        "locationNotes": "Edificio I, Piso 1.", "keywords": ["direccion de relaciones publicas", "relaciones publicas"]
    },
    {
        "placeId": "presidencyI", "name": "Presidencia UAM", "category": CampusCategory.ADMINISTRATIVE,
        "parentBuildingId": "buildingI", "floorLevel": 1, "isAccessible": True,
        "latitude": 12.109255, "longitude": -86.258170,
        "locationNotes": "Edificio I, Piso 1.", "keywords": ["presidencia", "presidencia uam"]
    },

    # -------------------------------------------------------------------------
    # BUILDING J: Pre-Clinical Dentistry Labs (1 Floor — exact order)
    # -------------------------------------------------------------------------
    {
        "placeId": "dentalLabJ101", "name": "Laboratorio de Odontología J101", "category": CampusCategory.DENTAL_LAB,
        "parentBuildingId": "buildingJ", "floorLevel": 1, "isAccessible": True,
        "latitude": 12.108126, "longitude": -86.256780,
        "locationNotes": "Edificio J, Planta Única.", "keywords": ["j101", "j-101", "j 101", "lab odonto j101", "simulacion dental"]
    },
    {
        "placeId": "dentalLabJ102", "name": "Laboratorio de Odontología J102", "category": CampusCategory.DENTAL_LAB,
        "parentBuildingId": "buildingJ", "floorLevel": 1, "isAccessible": True,
        "latitude": 12.108094, "longitude": -86.256756,
        "locationNotes": "Edificio J, Planta Única.", "keywords": ["j102", "j-102", "j 102", "lab odonto j102"]
    },
    {
        "placeId": "restroomsMenJ", "name": "Baños Hombres (Edificio J)", "category": CampusCategory.RESTROOM,
        "parentBuildingId": "buildingJ", "floorLevel": 1, "isAccessible": True,
        "latitude": 12.108030, "longitude": -86.256830,
        "locationNotes": "Edificio J, Planta Única.", "keywords": ["baño hombres j", "baños hombres j", "sanitarios hombres j", "baño j"]
    },
    {
        "placeId": "restroomsWomenJ", "name": "Baños Mujeres (Edificio J)", "category": CampusCategory.RESTROOM,
        "parentBuildingId": "buildingJ", "floorLevel": 1, "isAccessible": True,
        "latitude": 12.108070, "longitude": -86.256815,
        "locationNotes": "Edificio J, Planta Única.", "keywords": ["baño mujeres j", "baños mujeres j", "sanitarios mujeres j", "baños j"]
    },
    {
        "placeId": "uamMapJ", "name": "Mapa UAM (Edificio J)", "category": CampusCategory.ADMINISTRATIVE,
        "parentBuildingId": "buildingJ", "floorLevel": 1, "isAccessible": True,
        "latitude": 12.108097, "longitude": -86.256693,
        "locationNotes": "Edificio J, mapa físico de la universidad.", "keywords": ["mapa j", "mapa uam j"]
    },
    {
        "placeId": "entranceJ", "name": "Entrada Principal Edificio J", "category": CampusCategory.DENTAL_LAB,
        "parentBuildingId": "buildingJ", "floorLevel": 1, "isAccessible": True,
        "latitude": 12.108126, "longitude": -86.256780,
        "locationNotes": "Edificio J, acceso principal.", "keywords": ["entrada j", "acceso j", "edificio j"]
    },

    # -------------------------------------------------------------------------
    # BUILDING K: Dining, Cafeteria, Jaguar Shop & Terraces (Floors 1 & 2)
    # -------------------------------------------------------------------------
    # Floor 1 (exact order from buildings.txt)
    {
        "placeId": "restroomsMenK1", "name": "Baños Hombres (Edificio K)", "category": CampusCategory.RESTROOM,
        "parentBuildingId": "buildingK", "floorLevel": 1, "isAccessible": True,
        "latitude": 12.108815, "longitude": -86.256730,
        "locationNotes": "Edificio K, Piso 1.", "keywords": ["banos hombres k", "banos k"]
    },
    {
        "placeId": "restroomsWomenK1", "name": "Baños Mujeres (Edificio K)", "category": CampusCategory.RESTROOM,
        "parentBuildingId": "buildingK", "floorLevel": 1, "isAccessible": True,
        "latitude": 12.108815, "longitude": -86.256730,
        "locationNotes": "Edificio K, Piso 1.", "keywords": ["banos mujeres k", "banos k"]
    },
    {
        "placeId": "tablesAreaK1", "name": "Área de Mesas (Edificio K - Piso 1)", "category": CampusCategory.FOOD_AREA,
        "parentBuildingId": "buildingK", "floorLevel": 1, "isAccessible": True,
        "latitude": 12.108805, "longitude": -86.256785,
        "locationNotes": "Edificio K, Piso 1.", "keywords": ["area de mesas k", "mesas cafeteria"]
    },
    {
        "placeId": "foodKiosksK", "name": "Terrazas (Edificio K)", "category": CampusCategory.FOOD_AREA,
        "parentBuildingId": "buildingK", "floorLevel": 1, "isAccessible": True,
        "latitude": 12.108805, "longitude": -86.256785,
        "locationNotes": "Edificio K, Piso 1.", "keywords": ["terrazas", "terrazas k"]
    },
    {
        "placeId": "jaguarShopK", "name": "Jaguar Shop (Edificio K)", "category": CampusCategory.ADMINISTRATIVE,
        "parentBuildingId": "buildingK", "floorLevel": 1, "isAccessible": True,
        "latitude": 12.108750, "longitude": -86.256735,
        "locationNotes": "Edificio K, Piso 1.", "keywords": ["jaguar shop", "tienda uam", "tienda"]
    },
    {
        "placeId": "centralCafeteriaK", "name": "Módulos Comerciales (Food Court)", "category": CampusCategory.FOOD_AREA,
        "parentBuildingId": "buildingK", "floorLevel": 1, "isAccessible": True,
        "latitude": 12.108775, "longitude": -86.256755,
        "locationNotes": "Edificio K, Piso 1, food court central.", "keywords": ["cafeteria", "almuerzo", "jaguar corner", "comida", "food court", "modulos comerciales", "comer"]
    },
    {
        "placeId": "kiosk1K1", "name": "Kiosko 1 (Edificio K - Piso 1)", "category": CampusCategory.FOOD_AREA,
        "parentBuildingId": "buildingK", "floorLevel": 1, "isAccessible": True,
        "latitude": 12.108775, "longitude": -86.256755,
        "locationNotes": "Edificio K, Piso 1.", "keywords": ["kiosko 1", "kiosko 1 k"]
    },
    # Floor 2 (exact order from buildings.txt)
    {
        "placeId": "kiosk1K2", "name": "Kiosko 1 (Edificio K - Piso 2)", "category": CampusCategory.FOOD_AREA,
        "parentBuildingId": "buildingK", "floorLevel": 2, "isAccessible": False,
        "latitude": 12.108775, "longitude": -86.256755,
        "locationNotes": "Edificio K, Piso 2.", "keywords": ["kiosko 1 piso 2", "kiosko 1 k2"]
    },
    {
        "placeId": "kiosk2K2", "name": "Kiosko 2 (Edificio K - Piso 2)", "category": CampusCategory.FOOD_AREA,
        "parentBuildingId": "buildingK", "floorLevel": 2, "isAccessible": False,
        "latitude": 12.108775, "longitude": -86.256755,
        "locationNotes": "Edificio K, Piso 2.", "keywords": ["kiosko 2", "kiosko 2 piso 2"]
    },
    {
        "placeId": "tablesAreaK2", "name": "Área de Mesas (Edificio K - Piso 2)", "category": CampusCategory.FOOD_AREA,
        "parentBuildingId": "buildingK", "floorLevel": 2, "isAccessible": False,
        "latitude": 12.108800, "longitude": -86.256780,
        "locationNotes": "Edificio K, Piso 2.", "keywords": ["area de mesas k2", "terraza superior", "mesas piso 2 k"]
    },

    # -------------------------------------------------------------------------
    # BUILDING L: Culture, Music & Locker Rooms (1 Floor — exact order)
    # -------------------------------------------------------------------------
    {
        "placeId": "showersVisitorsL", "name": "Duchas Visitantes (Edificio L)", "category": CampusCategory.SPORTS,
        "parentBuildingId": "buildingL", "floorLevel": 1, "isAccessible": True,
        "latitude": 12.108952, "longitude": -86.258551,
        "locationNotes": "Edificio L, Planta Única (derecha).", "keywords": ["duchas visitantes", "duchas away", "duchas l", "vestidores l"]
    },
    {
        "placeId": "showersHomeL", "name": "Duchas Home (Edificio L)", "category": CampusCategory.SPORTS,
        "parentBuildingId": "buildingL", "floorLevel": 1, "isAccessible": True,
        "latitude": 12.108952, "longitude": -86.258551,
        "locationNotes": "Edificio L, Planta Única (izquierda).", "keywords": ["duchas home", "duchas", "vestidores home"]
    },
    {
        "placeId": "cultureHallL", "name": "Salón de Cultura y Mapa UAM (Edificio L)", "category": CampusCategory.CLASSROOM,
        "parentBuildingId": "buildingL", "floorLevel": 1, "isAccessible": True,
        "latitude": 12.109123, "longitude": -86.258504,
        "locationNotes": "Edificio L, Planta Única.", "keywords": ["salon de cultura", "cultura", "mapa uam l", "edificio l"]
    },
    {
        "placeId": "musicClassroomL", "name": "Aula de Música (Edificio L)", "category": CampusCategory.CLASSROOM,
        "parentBuildingId": "buildingL", "floorLevel": 1, "isAccessible": True,
        "latitude": 12.109120, "longitude": -86.258513,
        "locationNotes": "Edificio L, Planta Única.", "keywords": ["aula de musica", "musica", "area de musica"]
    },
    {
        "placeId": "restroomsMenL", "name": "Baños Hombres (Edificio L)", "category": CampusCategory.RESTROOM,
        "parentBuildingId": "buildingL", "floorLevel": 1, "isAccessible": True,
        "latitude": 12.108905, "longitude": -86.258519,
        "locationNotes": "Edificio L, Planta Única.", "keywords": ["banos hombres l", "banos l"]
    },
    {
        "placeId": "restroomsWomenL", "name": "Baños Mujeres (Edificio L)", "category": CampusCategory.RESTROOM,
        "parentBuildingId": "buildingL", "floorLevel": 1, "isAccessible": True,
        "latitude": 12.108905, "longitude": -86.258519,
        "locationNotes": "Edificio L, Planta Única.", "keywords": ["banos mujeres l", "banos l"]
    },

    # -------------------------------------------------------------------------
    # BUILDING M: Auditoriums & Classrooms (Floors 1, 2, 3 — exact order)
    # -------------------------------------------------------------------------
    # Floor 1
    {
        "placeId": "auditoriumM101", "name": "Auditorio M101", "category": CampusCategory.AUDITORIUM,
        "parentBuildingId": "buildingM", "floorLevel": 1, "isAccessible": True,
        "latitude": 12.108452, "longitude": -86.257566,
        "locationNotes": "Edificio M, Piso 1.", "keywords": ["m101", "m-101", "m 101", "auditorio m101"]
    },
    {
        "placeId": "auditoriumM102", "name": "Auditorio M102", "category": CampusCategory.AUDITORIUM,
        "parentBuildingId": "buildingM", "floorLevel": 1, "isAccessible": True,
        "latitude": 12.108439, "longitude": -86.257594,
        "locationNotes": "Edificio M, Piso 1.", "keywords": ["m102", "m-102", "m 102", "auditorio m102"]
    },
    {
        "placeId": "environmentalDirectorateM", "name": "Dirección de Gestión Ambiental y Energética", "category": CampusCategory.ADMINISTRATIVE,
        "parentBuildingId": "buildingM", "floorLevel": 1, "isAccessible": True,
        "latitude": 12.108331, "longitude": -86.257559,
        "locationNotes": "Edificio M, Piso 1.", "keywords": ["direccion de gestion ambiental y energetica", "gestion ambiental", "energetica"]
    },
    {
        "placeId": "researchExtensionM", "name": "Dirección Investigación y Extensión Universitaria", "category": CampusCategory.ADMINISTRATIVE,
        "parentBuildingId": "buildingM", "floorLevel": 1, "isAccessible": True,
        "latitude": 12.108331, "longitude": -86.257559,
        "locationNotes": "Edificio M, Piso 1.", "keywords": ["direccion investigacion y extension universitaria", "investigacion", "extension universitaria"]
    },
    {
        "placeId": "classroomM1", "name": "Aula (Edificio M - Piso 1)", "category": CampusCategory.CLASSROOM,
        "parentBuildingId": "buildingM", "floorLevel": 1, "isAccessible": True,
        "latitude": 12.108385, "longitude": -86.257550,
        "locationNotes": "Edificio M, Piso 1.", "keywords": ["aula m", "aula piso 1 m"]
    },
    {
        "placeId": "restroomsMenM1", "name": "Baños Hombres (Edificio M)", "category": CampusCategory.RESTROOM,
        "parentBuildingId": "buildingM", "floorLevel": 1, "isAccessible": True,
        "latitude": 12.108366, "longitude": -86.257520,
        "locationNotes": "Edificio M, Piso 1.", "keywords": ["banos hombres m", "banos m"]
    },
    {
        "placeId": "restroomsWomenM1", "name": "Baños Mujeres (Edificio M)", "category": CampusCategory.RESTROOM,
        "parentBuildingId": "buildingM", "floorLevel": 1, "isAccessible": True,
        "latitude": 12.108366, "longitude": -86.257520,
        "locationNotes": "Edificio M, Piso 1.", "keywords": ["banos mujeres m", "banos m"]
    },
    {
        "placeId": "accessibleRestroomM1", "name": "Servicios Mixtos Discapacitados (Edificio M)", "category": CampusCategory.RESTROOM,
        "parentBuildingId": "buildingM", "floorLevel": 1, "isAccessible": True,
        "latitude": 12.108366, "longitude": -86.257520,
        "locationNotes": "Edificio M, Piso 1.", "keywords": ["servicios mixtos discapacitados", "bano accesible m"]
    },
    {
        "placeId": "drinkingFountainM1", "name": "Bebedero de Agua (Edificio M)", "category": CampusCategory.DRINKING_FOUNTAIN,
        "parentBuildingId": "buildingM", "floorLevel": 1, "isAccessible": True,
        "latitude": 12.108426, "longitude": -86.257560,
        "locationNotes": "Edificio M, Piso 1.", "keywords": ["bebedero m", "agua m"]
    },
    # Floor 2 (M201..M204)
    {
        "placeId": "classroomM201", "name": "Aula M201", "category": CampusCategory.CLASSROOM,
        "parentBuildingId": "buildingM", "floorLevel": 2, "isAccessible": False,
        "latitude": 12.108402, "longitude": -86.257582,
        "locationNotes": "Edificio M, Piso 2.", "keywords": ["m201", "m-201", "m 201", "aula m201"]
    },
    {
        "placeId": "classroomM202", "name": "Aula M202", "category": CampusCategory.CLASSROOM,
        "parentBuildingId": "buildingM", "floorLevel": 2, "isAccessible": False,
        "latitude": 12.108402, "longitude": -86.257582,
        "locationNotes": "Edificio M, Piso 2.", "keywords": ["m202", "m-202", "m 202", "aula m202"]
    },
    {
        "placeId": "classroomM203", "name": "Aula M203", "category": CampusCategory.CLASSROOM,
        "parentBuildingId": "buildingM", "floorLevel": 2, "isAccessible": False,
        "latitude": 12.108437, "longitude": -86.257556,
        "locationNotes": "Edificio M, Piso 2.", "keywords": ["m203", "m-203", "m 203", "aula m203"]
    },
    {
        "placeId": "classroomM204", "name": "Aula M204", "category": CampusCategory.CLASSROOM,
        "parentBuildingId": "buildingM", "floorLevel": 2, "isAccessible": False,
        "latitude": 12.108437, "longitude": -86.257556,
        "locationNotes": "Edificio M, Piso 2.", "keywords": ["m204", "m-204", "m 204", "aula m204"]
    },
    # Floor 3 (M301..M304)
    {
        "placeId": "classroomM301", "name": "Aula M301", "category": CampusCategory.CLASSROOM,
        "parentBuildingId": "buildingM", "floorLevel": 3, "isAccessible": False,
        "latitude": 12.108493, "longitude": -86.257603,
        "locationNotes": "Edificio M, Piso 3.", "keywords": ["m301", "m-301", "m 301", "aula m301"]
    },
    {
        "placeId": "classroomM302", "name": "Aula M302", "category": CampusCategory.CLASSROOM,
        "parentBuildingId": "buildingM", "floorLevel": 3, "isAccessible": False,
        "latitude": 12.108493, "longitude": -86.257603,
        "locationNotes": "Edificio M, Piso 3.", "keywords": ["m302", "m-302", "m 302", "aula m302"]
    },
    {
        "placeId": "classroomM303", "name": "Aula M303", "category": CampusCategory.CLASSROOM,
        "parentBuildingId": "buildingM", "floorLevel": 3, "isAccessible": False,
        "latitude": 12.108450, "longitude": -86.257575,
        "locationNotes": "Edificio M, Piso 3.", "keywords": ["m303", "m-303", "m 303", "aula m303"]
    },
    {
        "placeId": "classroomM304", "name": "Aula M304", "category": CampusCategory.CLASSROOM,
        "parentBuildingId": "buildingM", "floorLevel": 3, "isAccessible": False,
        "latitude": 12.108450, "longitude": -86.257575,
        "locationNotes": "Edificio M, Piso 3.", "keywords": ["m304", "m-304", "m 304", "aula m304"]
    },

    # -------------------------------------------------------------------------
    # BUILDING N: Dental Clinics & FODO (Gateway Pattern — Floors 1 & 2)
    # -------------------------------------------------------------------------
    {
        "placeId": "dentistryReceptionN",
        "name": "Recepción de Clínicas Odontológicas y Archivo - Caja (Edificio N)",
        "category": CampusCategory.DENTAL_LAB,
        "parentBuildingId": "buildingN",
        "floorLevel": 1,
        "isAccessible": True,
        "latitude": 12.107871,
        "longitude": -86.256967,
        "locationNotes": "Edificio N, Piso 1 (Recepción Gateway): Quirófanos 1-2, Archivo-Caja, Clínicas Médicas A/B/E, Archivo y Expedientes, Coordinación de Clínicas, Radiología 1-3, Proveeduría, Interpretación Radiográfica, Tomografía, Lavado, Empaque, Esterilización, Clínicas Post-Grado C-D, Lab Fabricación Digital, Bodega Archivo, Oficina IDEA, Supervisión Clínicas y Archivo.",
        "keywords": [
            "clinicas odontologicas", "recepcion dental", "recepcion n", "archivo caja", "caja dental",
            "odontologia", "quirofano 1", "quirofano 2", "quirofano", "clinica medica a", "clinica medica b",
            "clinica medica e", "oficina archivo y expedientes", "coordinacion de clinicas",
            "radiologia 1", "radiologia 2", "radiologia 3", "proveeduria", "interpretacion radiografica",
            "tomografia", "lavado de instrumentos", "preparacion y empaque", "esterilizacion",
            "clinicas post grado c-d", "laboratorio de fabricacion digital", "bodega archivo",
            "oficina idea", "oficina de supervision clinicas odontologicas", "archivo"
        ]
    },
    {
        "placeId": "restroomsMenN1",
        "name": "Servicios Sanitarios Hombres (Edificio N - junto a Plaza Chilamates)",
        "category": CampusCategory.RESTROOM,
        "parentBuildingId": "buildingN",
        "floorLevel": 1,
        "isAccessible": True,
        "latitude": 12.107741,
        "longitude": -86.256842,
        "locationNotes": "Edificio N, Piso 1, junto a Plaza Chilamates.",
        "keywords": ["sanitarios hombres n", "banos hombres n", "banos n", "banos chilamate"]
    },
    {
        "placeId": "restroomsWomenN1",
        "name": "Servicios Sanitarios Mujeres (Edificio N - junto a Plaza Chilamates)",
        "category": CampusCategory.RESTROOM,
        "parentBuildingId": "buildingN",
        "floorLevel": 1,
        "isAccessible": True,
        "latitude": 12.107741,
        "longitude": -86.256842,
        "locationNotes": "Edificio N, Piso 1, junto a Plaza Chilamates.",
        "keywords": ["sanitarios mujeres n", "banos mujeres n", "banos n", "banos chilamate"]
    },
    {
        "placeId": "facultyDentistryN",
        "name": "Facultad de Odontología (FODO) — Recepción Piso 2",
        "category": CampusCategory.FACULTY,
        "parentBuildingId": "buildingN",
        "floorLevel": 2,
        "isAccessible": False,
        "latitude": 12.107871,
        "longitude": -86.256967,
        "locationNotes": "Edificio N, Piso 2 (Recepción FODO): Técnicos Odontológicos, Lab Simuladores, Lab de Grado, Proveeduría, Lab Post-Grado, Radiología No.1 - No.2 y Revelado Digital.",
        "keywords": [
            "fodo", "facultad de odontologia", "decanatura odonto", "tecnicos odontologicos",
            "lab simuladores", "lab de grado", "proveeduria fodo", "lab post-grado",
            "radiologia no1 - no 2", "revelado digital"
        ]
    },

    # -------------------------------------------------------------------------
    # BUILDING O: Engineering & Architecture (FIA) - Floors 1 & 2 (exact order)
    # -------------------------------------------------------------------------
    # Floor 1
    {
        "placeId": "facultyEngineeringO", "name": "Facultad de Ingeniería y Arquitectura (O101)", "category": CampusCategory.FACULTY,
        "parentBuildingId": "buildingO", "floorLevel": 1, "isAccessible": True,
        "latitude": 12.107664, "longitude": -86.257761,
        "locationNotes": "Edificio O, Piso 1, Decanatura FIA.", "keywords": ["fia", "ingenieria", "arquitectura", "facultad de ingenieria", "decanatura fia", "o101", "o-101", "o 101"]
    },
    {
        "placeId": "soilMechanicsLabO", "name": "Laboratorio de Mecánica de Suelos (O102)", "category": CampusCategory.FACULTY,
        "parentBuildingId": "buildingO", "floorLevel": 1, "isAccessible": True,
        "latitude": 12.107535, "longitude": -86.257643,
        "locationNotes": "Edificio O, Piso 1.", "keywords": ["suelos", "mecanica de suelos", "laboratorio civil", "o102", "o-102", "o 102"]
    },
    {
        "placeId": "exhibitionAreaO", "name": "Área de Exhibición (Edificio O)", "category": CampusCategory.FACULTY,
        "parentBuildingId": "buildingO", "floorLevel": 1, "isAccessible": True,
        "latitude": 12.107518, "longitude": -86.257615,
        "locationNotes": "Edificio O, Piso 1.", "keywords": ["exhibicion", "area de exhibicion", "exposicion"]
    },
    {
        "placeId": "materialsLabO", "name": "Laboratorio de Resistencia de Materiales (O104)", "category": CampusCategory.FACULTY,
        "parentBuildingId": "buildingO", "floorLevel": 1, "isAccessible": True,
        "latitude": 12.107502, "longitude": -86.257586,
        "locationNotes": "Edificio O, Piso 1.", "keywords": ["materiales", "resistencia de materiales", "lab materiales", "o104", "o-104", "o 104"]
    },
    {
        "placeId": "mixingAreaO", "name": "Área de Mezclado (Lab Materiales)", "category": CampusCategory.FACULTY,
        "parentBuildingId": "buildingO", "floorLevel": 1, "isAccessible": True,
        "latitude": 12.107490, "longitude": -86.257570,
        "locationNotes": "Edificio O, Piso 1.", "keywords": ["mezclado", "area de mezclado"]
    },
    {
        "placeId": "curingAreaO", "name": "Área de Curado (Lab Materiales)", "category": CampusCategory.FACULTY,
        "parentBuildingId": "buildingO", "floorLevel": 1, "isAccessible": True,
        "latitude": 12.107485, "longitude": -86.257560,
        "locationNotes": "Edificio O, Piso 1.", "keywords": ["curado", "area de curado", "curado de probetas"]
    },
    {
        "placeId": "labTechniciansO", "name": "Técnicos de Laboratorio (Edificio O)", "category": CampusCategory.ADMINISTRATIVE,
        "parentBuildingId": "buildingO", "floorLevel": 1, "isAccessible": True,
        "latitude": 12.107510, "longitude": -86.257575,
        "locationNotes": "Edificio O, Piso 1.", "keywords": ["tecnicos", "tecnicos de lab", "oficina tecnicos"]
    },
    {
        "placeId": "fluidMechanicsLabO", "name": "Laboratorio de Mecánica de Fluidos", "category": CampusCategory.FACULTY,
        "parentBuildingId": "buildingO", "floorLevel": 1, "isAccessible": True,
        "latitude": 12.107515, "longitude": -86.257550,
        "locationNotes": "Edificio O, Piso 1.", "keywords": ["fluidos", "mecanica de fluidos", "lab fluidos"]
    },
    {
        "placeId": "restroomsMenO", "name": "Baños Hombres (Anexo FIA)", "category": CampusCategory.RESTROOM,
        "parentBuildingId": "buildingO", "floorLevel": 1, "isAccessible": True,
        "latitude": 12.108151, "longitude": -86.257888,
        "locationNotes": "Edificio O, Anexo norte FIA.", "keywords": ["baños hombres o", "banos hombres o", "sanitarios hombres fia"]
    },
    {
        "placeId": "restroomsWomenO", "name": "Baños Mujeres (Anexo FIA)", "category": CampusCategory.RESTROOM,
        "parentBuildingId": "buildingO", "floorLevel": 1, "isAccessible": True,
        "latitude": 12.108151, "longitude": -86.257888,
        "locationNotes": "Edificio O, Anexo norte FIA.", "keywords": ["baños mujeres o", "banos mujeres o", "sanitarios mujeres fia"]
    },
    {
        "placeId": "teachersLoungeO", "name": "Sala de Maestros FIA (Anexo Norte)", "category": CampusCategory.FACULTY,
        "parentBuildingId": "buildingO", "floorLevel": 1, "isAccessible": True,
        "latitude": 12.108229, "longitude": -86.257948,
        "locationNotes": "Edificio O, Anexo norte FIA.", "keywords": ["sala de maestros", "maestros fia", "profesores fia", "anexo norte"]
    },
    {
        "placeId": "disasterRiskCoordO", "name": "Coordinación de Gestión Integral de Riesgos de Desastres (O105)", "category": CampusCategory.ADMINISTRATIVE,
        "parentBuildingId": "buildingO", "floorLevel": 1, "isAccessible": True,
        "latitude": 12.107545, "longitude": -86.257437,
        "locationNotes": "Edificio O, Piso 1.", "keywords": ["riesgos", "gestion de riesgos", "desastres", "o105", "o-105", "o 105"]
    },
    {
        "placeId": "mapUamO", "name": "Mapa UAM (Entrada Edificio O)", "category": CampusCategory.ADMINISTRATIVE,
        "parentBuildingId": "buildingO", "floorLevel": 1, "isAccessible": True,
        "latitude": 12.107478, "longitude": -86.257555,
        "locationNotes": "Entrada principal y directorio del Edificio O.", "keywords": ["mapa o", "mapa uam o", "directorio edificio o"]
    },
    {
        "placeId": "rampParkingO", "name": "Rampa Accesible del O al Parqueo", "category": CampusCategory.ACCESSIBLE_RAMP,
        "parentBuildingId": "buildingO", "floorLevel": 1, "isAccessible": True,
        "latitude": 12.107612, "longitude": -86.257442,
        "locationNotes": "Conexión accesible entre Edificio O y parqueo.", "keywords": ["rampa o", "rampa parqueo o", "rampa accesible fia"]
    },
    # Floor 2 (exact order from buildings.txt)
    {
        "placeId": "networksLabO", "name": "Laboratorio de Redes O201", "category": CampusCategory.CLASSROOM,
        "parentBuildingId": "buildingO", "floorLevel": 2, "isAccessible": False,
        "latitude": 12.107520, "longitude": -86.257586,
        "locationNotes": "Edificio O, Piso 2.", "keywords": ["redes", "lab redes", "o201", "o-201", "o 201"]
    },
    {
        "placeId": "classroomO202", "name": "Aula O202", "category": CampusCategory.CLASSROOM,
        "parentBuildingId": "buildingO", "floorLevel": 2, "isAccessible": False,
        "latitude": 12.107741, "longitude": -86.257507,
        "locationNotes": "Edificio O, Piso 2.", "keywords": ["o202", "o-202", "o 202", "aula o202"]
    },
    {
        "placeId": "tutoringRoomO", "name": "Sala de Tutoría FIA", "category": CampusCategory.CLASSROOM,
        "parentBuildingId": "buildingO", "floorLevel": 2, "isAccessible": False,
        "latitude": 12.107632, "longitude": -86.257548,
        "locationNotes": "Edificio O, Piso 2.", "keywords": ["tutoria", "sala de tutoria", "tutorias fia"]
    },
    {
        "placeId": "ciarLabO", "name": "Centro de Inteligencia Artificial y Robótica (CIAR)", "category": CampusCategory.FACULTY,
        "parentBuildingId": "buildingO", "floorLevel": 2, "isAccessible": False,
        "latitude": 12.107599, "longitude": -86.257561,
        "locationNotes": "Edificio O, Piso 2.", "keywords": ["ciar", "inteligencia artificial", "centro de inteligencia artificial y robotica"]
    },
    {
        "placeId": "networksCenterO", "name": "Centro de Redes (Edificio O)", "category": CampusCategory.ADMINISTRATIVE,
        "parentBuildingId": "buildingO", "floorLevel": 2, "isAccessible": False,
        "latitude": 12.107550, "longitude": -86.257575,
        "locationNotes": "Edificio O, Piso 2.", "keywords": ["centro de redes", "redes uam"]
    },
    {
        "placeId": "roboticsAreaO", "name": "Área de Robótica (CIAR)", "category": CampusCategory.FACULTY,
        "parentBuildingId": "buildingO", "floorLevel": 2, "isAccessible": False,
        "latitude": 12.107585, "longitude": -86.257567,
        "locationNotes": "Edificio O, Piso 2.", "keywords": ["robotica", "lab robotica", "area de robotica"]
    },
    {
        "placeId": "drinkingFountainO_F2", "name": "Bebedero de Agua (Edificio O - Piso 2)", "category": CampusCategory.DRINKING_FOUNTAIN,
        "parentBuildingId": "buildingO", "floorLevel": 2, "isAccessible": False,
        "latitude": 12.107585, "longitude": -86.257567,
        "locationNotes": "Edificio O, Piso 2, junto a robótica.", "keywords": ["bebedero o", "agua piso 2 o"]
    },

    # -------------------------------------------------------------------------
    # BUILDING P: Copernicus Observatory & Classrooms (Floors 1-5 — exact order)
    # -------------------------------------------------------------------------
    # Floor 1
    {
        "placeId": "weatherStationP", "name": "Estación de Meteorología (Edificio P)", "category": CampusCategory.CLASSROOM,
        "parentBuildingId": "buildingP", "floorLevel": 1, "isAccessible": True,
        "latitude": 12.107470, "longitude": -86.256753,
        "locationNotes": "Edificio P, Piso 1, acceso este.", "keywords": ["estacion de meteorologia", "meteorologia", "clima"]
    },
    {
        "placeId": "classroomP101", "name": "Aula P101", "category": CampusCategory.CLASSROOM,
        "parentBuildingId": "buildingP", "floorLevel": 1, "isAccessible": True,
        "latitude": 12.107460, "longitude": -86.256743,
        "locationNotes": "Edificio P, Piso 1.", "keywords": ["p101", "p-101", "p 101", "salon 101", "aula p101"]
    },
    {
        "placeId": "drinkingFountainP1", "name": "Bebedero de Agua (Edificio P - Piso 1 Este)", "category": CampusCategory.DRINKING_FOUNTAIN,
        "parentBuildingId": "buildingP", "floorLevel": 1, "isAccessible": True,
        "latitude": 12.107460, "longitude": -86.256743,
        "locationNotes": "Edificio P, Piso 1, junto al Aula P101.", "keywords": ["bebedero p", "bebedero p1", "agua p1"]
    },
    {
        "placeId": "classroomP102", "name": "Aula P102", "category": CampusCategory.CLASSROOM,
        "parentBuildingId": "buildingP", "floorLevel": 1, "isAccessible": True,
        "latitude": 12.107431, "longitude": -86.256783,
        "locationNotes": "Edificio P, Piso 1.", "keywords": ["p102", "p-102", "p 102", "salon 102", "aula p102"]
    },
    {
        "placeId": "classroomP103", "name": "Aula P103", "category": CampusCategory.CLASSROOM,
        "parentBuildingId": "buildingP", "floorLevel": 1, "isAccessible": True,
        "latitude": 12.107439, "longitude": -86.256947,
        "locationNotes": "Edificio P, Piso 1.", "keywords": ["p103", "p-103", "p 103", "salon 103", "aula p103"]
    },
    {
        "placeId": "classroomP104", "name": "Aula P104", "category": CampusCategory.CLASSROOM,
        "parentBuildingId": "buildingP", "floorLevel": 1, "isAccessible": True,
        "latitude": 12.107455, "longitude": -86.256981,
        "locationNotes": "Edificio P, Piso 1.", "keywords": ["p104", "p-104", "p 104", "salon 104", "aula p104"]
    },
    {
        "placeId": "classroomP105", "name": "Aula P105", "category": CampusCategory.CLASSROOM,
        "parentBuildingId": "buildingP", "floorLevel": 1, "isAccessible": True,
        "latitude": 12.107453, "longitude": -86.257149,
        "locationNotes": "Edificio P, Piso 1.", "keywords": ["p105", "p-105", "p 105", "salon 105", "aula p105"]
    },
    {
        "placeId": "classroomP106", "name": "Aula P106", "category": CampusCategory.CLASSROOM,
        "parentBuildingId": "buildingP", "floorLevel": 1, "isAccessible": True,
        "latitude": 12.107467, "longitude": -86.257202,
        "locationNotes": "Edificio P, Piso 1.", "keywords": ["p106", "p-106", "p 106", "salon 106", "aula p106"]
    },
    {
        "placeId": "classroomP107", "name": "Aula P107", "category": CampusCategory.CLASSROOM,
        "parentBuildingId": "buildingP", "floorLevel": 1, "isAccessible": True,
        "latitude": 12.107450, "longitude": -86.257270,
        "locationNotes": "Edificio P, Piso 1.", "keywords": ["p107", "p-107", "p 107", "salon 107", "aula p107"]
    },
    {
        "placeId": "classroomP108", "name": "Aula P108", "category": CampusCategory.CLASSROOM,
        "parentBuildingId": "buildingP", "floorLevel": 1, "isAccessible": True,
        "latitude": 12.107477, "longitude": -86.257206,
        "locationNotes": "Edificio P, Piso 1.", "keywords": ["p108", "p-108", "p 108", "salon 108", "aula p108"]
    },
    {
        "placeId": "drinkingFountainP1West", "name": "Bebedero de Agua (Edificio P - Piso 1 Oeste)", "category": CampusCategory.DRINKING_FOUNTAIN,
        "parentBuildingId": "buildingP", "floorLevel": 1, "isAccessible": True,
        "latitude": 12.107459, "longitude": -86.257314,
        "locationNotes": "Edificio P, Piso 1, entre P108 y baños.", "keywords": ["bebedero p1 oeste", "bebedero p1"]
    },
    {
        "placeId": "restroomsMenP1", "name": "Baños Hombres (Edificio P - Piso 1)", "category": CampusCategory.RESTROOM,
        "parentBuildingId": "buildingP", "floorLevel": 1, "isAccessible": True,
        "latitude": 12.107441, "longitude": -86.257422,
        "locationNotes": "Edificio P, Piso 1 (izquierda).", "keywords": ["baños p", "baño p", "baños hombres p1", "sanitarios p1"]
    },
    {
        "placeId": "restroomsWomenP1", "name": "Baños Mujeres (Edificio P - Piso 1)", "category": CampusCategory.RESTROOM,
        "parentBuildingId": "buildingP", "floorLevel": 1, "isAccessible": True,
        "latitude": 12.107441, "longitude": -86.257422,
        "locationNotes": "Edificio P, Piso 1 (derecha).", "keywords": ["baños mujeres p1", "sanitarios p1"]
    },
    {
        "placeId": "rampParkingP", "name": "Rampa del Estacionamiento hacia Edificio P", "category": CampusCategory.ACCESSIBLE_RAMP,
        "parentBuildingId": "buildingP", "floorLevel": 1, "isAccessible": True,
        "latitude": 12.106991, "longitude": -86.258233,
        "locationNotes": "Rampa del estacionamiento hacia el Edificio P, enfrente del Edificio O.", "keywords": ["rampa p", "rampa edificio p", "rampa estacionamiento p"]
    },
    # Floor 2
    {
        "placeId": "classroomP201", "name": "Aula P201", "category": CampusCategory.CLASSROOM,
        "parentBuildingId": "buildingP", "floorLevel": 2, "isAccessible": False,
        "latitude": 12.107484, "longitude": -86.256721,
        "locationNotes": "Edificio P, Piso 2.", "keywords": ["p201", "p-201", "p 201", "salon 201", "aula p201"]
    },
    {
        "placeId": "drinkingFountainP2East", "name": "Bebedero de Agua (Edificio P - Piso 2 Este)", "category": CampusCategory.DRINKING_FOUNTAIN,
        "parentBuildingId": "buildingP", "floorLevel": 2, "isAccessible": False,
        "latitude": 12.107434, "longitude": -86.256781,
        "locationNotes": "Edificio P, Piso 2, entre P201 y P202.", "keywords": ["bebedero p2", "agua p2", "bebedero p2 este"]
    },
    {
        "placeId": "classroomP202", "name": "Aula P202", "category": CampusCategory.CLASSROOM,
        "parentBuildingId": "buildingP", "floorLevel": 2, "isAccessible": False,
        "latitude": 12.107428, "longitude": -86.256817,
        "locationNotes": "Edificio P, Piso 2.", "keywords": ["p202", "p-202", "p 202", "salon 202", "aula p202"]
    },
    {
        "placeId": "classroomP203", "name": "Aula P203", "category": CampusCategory.CLASSROOM,
        "parentBuildingId": "buildingP", "floorLevel": 2, "isAccessible": False,
        "latitude": 12.107447, "longitude": -86.256957,
        "locationNotes": "Edificio P, Piso 2.", "keywords": ["p203", "p-203", "p 203", "salon 203", "aula p203"]
    },
    {
        "placeId": "classroomP204", "name": "Aula P204", "category": CampusCategory.CLASSROOM,
        "parentBuildingId": "buildingP", "floorLevel": 2, "isAccessible": False,
        "latitude": 12.107434, "longitude": -86.257043,
        "locationNotes": "Edificio P, Piso 2.", "keywords": ["p204", "p-204", "p 204", "salon 204", "aula p204"]
    },
    {
        "placeId": "classroomP205", "name": "Aula P205", "category": CampusCategory.CLASSROOM,
        "parentBuildingId": "buildingP", "floorLevel": 2, "isAccessible": False,
        "latitude": 12.107492, "longitude": -86.257090,
        "locationNotes": "Edificio P, Piso 2.", "keywords": ["p205", "p-205", "p 205", "salon 205", "aula p205"]
    },
    {
        "placeId": "classroomP206", "name": "Aula P206", "category": CampusCategory.CLASSROOM,
        "parentBuildingId": "buildingP", "floorLevel": 2, "isAccessible": False,
        "latitude": 12.107413, "longitude": -86.257153,
        "locationNotes": "Edificio P, Piso 2.", "keywords": ["p206", "p-206", "p 206", "salon 206", "aula p206"]
    },
    {
        "placeId": "classroomP207", "name": "Aula P207", "category": CampusCategory.CLASSROOM,
        "parentBuildingId": "buildingP", "floorLevel": 2, "isAccessible": False,
        "latitude": 12.107427, "longitude": -86.257217,
        "locationNotes": "Edificio P, Piso 2.", "keywords": ["p207", "p-207", "p 207", "salon 207", "aula p207"]
    },
    {
        "placeId": "classroomP208", "name": "Aula P208", "category": CampusCategory.CLASSROOM,
        "parentBuildingId": "buildingP", "floorLevel": 2, "isAccessible": False,
        "latitude": 12.107402, "longitude": -86.257297,
        "locationNotes": "Edificio P, Piso 2.", "keywords": ["p208", "p-208", "p 208", "salon 208", "aula p208"]
    },
    {
        "placeId": "drinkingFountainP2West", "name": "Bebedero de Agua (Edificio P - Piso 2 Oeste)", "category": CampusCategory.DRINKING_FOUNTAIN,
        "parentBuildingId": "buildingP", "floorLevel": 2, "isAccessible": False,
        "latitude": 12.107407, "longitude": -86.257298,
        "locationNotes": "Edificio P, Piso 2, junto al Aula P208.", "keywords": ["bebedero p2 oeste", "bebedero p2"]
    },
    {
        "placeId": "restroomsMenP2", "name": "Baños Hombres (Edificio P - Piso 2)", "category": CampusCategory.RESTROOM,
        "parentBuildingId": "buildingP", "floorLevel": 2, "isAccessible": False,
        "latitude": 12.107480, "longitude": -86.257337,
        "locationNotes": "Edificio P, Piso 2.", "keywords": ["baños hombres p2", "baños p2", "sanitarios p2"]
    },
    {
        "placeId": "restroomsWomenP2", "name": "Baños Mujeres (Edificio P - Piso 2)", "category": CampusCategory.RESTROOM,
        "parentBuildingId": "buildingP", "floorLevel": 2, "isAccessible": False,
        "latitude": 12.107480, "longitude": -86.257337,
        "locationNotes": "Edificio P, Piso 2.", "keywords": ["baños mujeres p2", "sanitarios p2"]
    },
    # Floor 3 (True P301..P308 aligned 1:1 with coordenadas.txt)
    {
        "placeId": "classroomP301", "name": "Aula P301", "category": CampusCategory.CLASSROOM,
        "parentBuildingId": "buildingP", "floorLevel": 3, "isAccessible": False,
        "latitude": 12.107461, "longitude": -86.256717,
        "locationNotes": "Edificio P, Piso 3.", "keywords": ["p301", "p-301", "p 301", "salon 301", "aula p301"]
    },
    {
        "placeId": "drinkingFountainP3", "name": "Bebedero de Agua (Edificio P - Piso 3 Este)", "category": CampusCategory.DRINKING_FOUNTAIN,
        "parentBuildingId": "buildingP", "floorLevel": 3, "isAccessible": False,
        "latitude": 12.107434, "longitude": -86.256751,
        "locationNotes": "Edificio P, Piso 3, entre P301 y P302.", "keywords": ["bebedero p3", "agua p3", "bebedero p3 este"]
    },
    {
        "placeId": "classroomP302", "name": "Aula P302", "category": CampusCategory.CLASSROOM,
        "parentBuildingId": "buildingP", "floorLevel": 3, "isAccessible": False,
        "latitude": 12.107462, "longitude": -86.256862,
        "locationNotes": "Edificio P, Piso 3.", "keywords": ["p302", "p-302", "p 302", "salon 302", "aula p302"]
    },
    {
        "placeId": "classroomP303", "name": "Aula P303", "category": CampusCategory.CLASSROOM,
        "parentBuildingId": "buildingP", "floorLevel": 3, "isAccessible": False,
        "latitude": 12.107443, "longitude": -86.256934,
        "locationNotes": "Edificio P, Piso 3.", "keywords": ["p303", "p-303", "p 303", "salon 303", "aula p303"]
    },
    {
        "placeId": "classroomP304", "name": "Aula P304", "category": CampusCategory.CLASSROOM,
        "parentBuildingId": "buildingP", "floorLevel": 3, "isAccessible": False,
        "latitude": 12.107442, "longitude": -86.256936,
        "locationNotes": "Edificio P, Piso 3.", "keywords": ["p304", "p-304", "p 304", "salon 304", "aula p304"]
    },
    {
        "placeId": "classroomP305", "name": "Aula P305", "category": CampusCategory.CLASSROOM,
        "parentBuildingId": "buildingP", "floorLevel": 3, "isAccessible": False,
        "latitude": 12.107443, "longitude": -86.256999,
        "locationNotes": "Edificio P, Piso 3.", "keywords": ["p305", "p-305", "p 305", "salon 305", "aula p305"]
    },
    {
        "placeId": "classroomP306", "name": "Aula P306", "category": CampusCategory.CLASSROOM,
        "parentBuildingId": "buildingP", "floorLevel": 3, "isAccessible": False,
        "latitude": 12.107454, "longitude": -86.257114,
        "locationNotes": "Edificio P, Piso 3.", "keywords": ["p306", "p-306", "p 306", "salon 306", "aula p306"]
    },
    {
        "placeId": "classroomP307", "name": "Aula P307", "category": CampusCategory.CLASSROOM,
        "parentBuildingId": "buildingP", "floorLevel": 3, "isAccessible": False,
        "latitude": 12.107461, "longitude": -86.257145,
        "locationNotes": "Edificio P, Piso 3.", "keywords": ["p307", "p-307", "p 307", "salon 307", "aula p307"]
    },
    {
        "placeId": "classroomP308", "name": "Aula P308", "category": CampusCategory.CLASSROOM,
        "parentBuildingId": "buildingP", "floorLevel": 3, "isAccessible": False,
        "latitude": 12.107435, "longitude": -86.257136,
        "locationNotes": "Edificio P, Piso 3.", "keywords": ["p308", "p-308", "p 308", "salon 308", "aula p308"]
    },
    {
        "placeId": "drinkingFountainP3West", "name": "Bebedero de Agua (Edificio P - Piso 3 Oeste)", "category": CampusCategory.DRINKING_FOUNTAIN,
        "parentBuildingId": "buildingP", "floorLevel": 3, "isAccessible": False,
        "latitude": 12.107452, "longitude": -86.257162,
        "locationNotes": "Edificio P, Piso 3, entre P308 y baños.", "keywords": ["bebedero p3 oeste", "bebedero p3"]
    },
    {
        "placeId": "restroomsMenP3", "name": "Baños Hombres (Edificio P - Piso 3)", "category": CampusCategory.RESTROOM,
        "parentBuildingId": "buildingP", "floorLevel": 3, "isAccessible": False,
        "latitude": 12.107468, "longitude": -86.257189,
        "locationNotes": "Edificio P, Piso 3.", "keywords": ["baños hombres p3", "baños p3", "sanitarios p3"]
    },
    {
        "placeId": "restroomsWomenP3", "name": "Baños Mujeres (Edificio P - Piso 3)", "category": CampusCategory.RESTROOM,
        "parentBuildingId": "buildingP", "floorLevel": 3, "isAccessible": False,
        "latitude": 12.107468, "longitude": -86.257189,
        "locationNotes": "Edificio P, Piso 3.", "keywords": ["baños mujeres p3", "sanitarios p3"]
    },
    # Floor 4
    {
        "placeId": "classroomP401", "name": "Aula P401", "category": CampusCategory.CLASSROOM,
        "parentBuildingId": "buildingP", "floorLevel": 4, "isAccessible": False,
        "latitude": 12.107470, "longitude": -86.256753,
        "locationNotes": "Edificio P, Piso 4 (acceso por escalera este).", "keywords": ["p401", "p-401", "p 401", "aula 401", "salon 401", "aula p401"]
    },
    # Floor 5
    {
        "placeId": "copernicusObservatoryP", "name": "Observatorio Copérnico (P501)", "category": CampusCategory.CLASSROOM,
        "parentBuildingId": "buildingP", "floorLevel": 5, "isAccessible": False,
        "latitude": 12.107470, "longitude": -86.256753,
        "locationNotes": "Edificio P, Piso 5 (cúpula / acceso por escalera este).", "keywords": ["copernico", "observatorio", "observatorio copernico", "telescopio", "piso 5", "p501", "p-501"]
    },

    # -------------------------------------------------------------------------
    # CAMPOS DEPORTIVOS (sportsZone — exact order from buildings.txt)
    # -------------------------------------------------------------------------
    {
        "placeId": "baseballStadium", "name": "Estadio de Baseball (Jaguar Stadium)", "category": CampusCategory.SPORTS,
        "parentBuildingId": "sportsZone", "floorLevel": 1, "isAccessible": True,
        "latitude": 12.107238, "longitude": -86.258449,
        "locationNotes": "Campos Deportivos.", "keywords": ["estadio", "beisbol", "baseball", "jaguar stadium", "campo beisbol"]
    },
    {
        "placeId": "soccerField", "name": "Cancha de Fútbol", "category": CampusCategory.SPORTS,
        "parentBuildingId": "sportsZone", "floorLevel": 1, "isAccessible": True,
        "latitude": 12.108450, "longitude": -86.258461,
        "locationNotes": "Campos Deportivos.", "keywords": ["cancha futbol", "cancha de futbol", "campo de futbol", "futbol", "soccer"]
    },
    {
        "placeId": "restroomsMenSZ", "name": "Baños Hombres (Campos Deportivos)", "category": CampusCategory.RESTROOM,
        "parentBuildingId": "sportsZone", "floorLevel": 1, "isAccessible": True,
        "latitude": 12.108105, "longitude": -86.257954,
        "locationNotes": "Campos Deportivos, junto a Kiosko Jaguarcito.", "keywords": ["banos hombres deportes", "banos campos deportivos"]
    },
    {
        "placeId": "restroomsWomenSZ", "name": "Baños Mujeres (Campos Deportivos)", "category": CampusCategory.RESTROOM,
        "parentBuildingId": "sportsZone", "floorLevel": 1, "isAccessible": True,
        "latitude": 12.108083, "longitude": -86.257861,
        "locationNotes": "Campos Deportivos, junto a Kiosko Jaguarcito.", "keywords": ["banos mujeres deportes", "banos campos deportivos"]
    },
    {
        "placeId": "kioskJaguarcitoSZ", "name": "Kiosko Jaguarcito", "category": CampusCategory.FOOD_AREA,
        "parentBuildingId": "sportsZone", "floorLevel": 1, "isAccessible": True,
        "latitude": 12.108100, "longitude": -86.257939,
        "locationNotes": "Campos Deportivos.", "keywords": ["kiosko jaguarcito", "jaguarcito"]
    },
    {
        "placeId": "sportsOfficesSZ", "name": "Oficinas de Deportes", "category": CampusCategory.SPORTS,
        "parentBuildingId": "sportsZone", "floorLevel": 1, "isAccessible": True,
        "latitude": 12.109252, "longitude": -86.258709,
        "locationNotes": "Campos Deportivos / Complejo Deportivo.", "keywords": ["oficinas de deportes", "oficina de deportes"]
    },
    {
        "placeId": "sportsWarehouseSZ", "name": "Bodega de Deportes", "category": CampusCategory.SPORTS,
        "parentBuildingId": "sportsZone", "floorLevel": 1, "isAccessible": True,
        "latitude": 12.108164, "longitude": -86.258313,
        "locationNotes": "Campos Deportivos.", "keywords": ["bodega de deportes"]
    },

    # -------------------------------------------------------------------------
    # COMPLEJO DEPORTIVO JAGUAR CENTER & BODEGA GENERAL (exact order)
    # -------------------------------------------------------------------------
    {
        "placeId": "martialArtsHallJC", "name": "Salón de Artes Marciales", "category": CampusCategory.SPORTS,
        "parentBuildingId": "jaguarCenter", "floorLevel": 1, "isAccessible": True,
        "latitude": 12.109284, "longitude": -86.258871,
        "locationNotes": "Complejo Deportivo Jaguar Center.", "keywords": ["salon de artes marciales", "artes marciales"]
    },
    {
        "placeId": "multipurposeHallJC", "name": "Salón de Usos Múltiples - DVE", "category": CampusCategory.SPORTS,
        "parentBuildingId": "jaguarCenter", "floorLevel": 1, "isAccessible": True,
        "latitude": 12.109279, "longitude": -86.258881,
        "locationNotes": "Complejo Deportivo Jaguar Center.", "keywords": ["salon de usos multiples", "usos multiples", "dve"]
    },
    {
        "placeId": "multipurposeCourtJC", "name": "Cancha Multi-Usos (Jaguar Center)", "category": CampusCategory.SPORTS,
        "parentBuildingId": "jaguarCenter", "floorLevel": 1, "isAccessible": True,
        "latitude": 12.109195, "longitude": -86.258695,
        "locationNotes": "Complejo Deportivo Jaguar Center.", "keywords": ["cancha multi-usos", "cancha multi usos", "cancha multiusos"]
    },
    {
        "placeId": "beachVolleyballJC", "name": "Cancha de Volleyball Arena (Jaguar Center)", "category": CampusCategory.SPORTS,
        "parentBuildingId": "jaguarCenter", "floorLevel": 1, "isAccessible": True,
        "latitude": 12.109225, "longitude": -86.258740,
        "locationNotes": "Complejo Deportivo Jaguar Center.", "keywords": ["cancha de volleyball arena", "volleyball arena", "voleibol arena"]
    },
    {
        "placeId": "kioskJaguarSportJC", "name": "Kiosko Jaguar Sport", "category": CampusCategory.FOOD_AREA,
        "parentBuildingId": "jaguarCenter", "floorLevel": 1, "isAccessible": True,
        "latitude": 12.109245, "longitude": -86.258720,
        "locationNotes": "Complejo Deportivo Jaguar Center.", "keywords": ["kiosko jaguar sport", "jaguar sport"]
    },
    {
        "placeId": "physiotherapyClinic", "name": "Clínica Fisioterapia", "category": CampusCategory.MEDICAL_LAB,
        "parentBuildingId": "physiotherapy", "floorLevel": 1, "isAccessible": True,
        "latitude": 12.109303, "longitude": -86.258511,
        "locationNotes": "Complejo Deportivo Jaguar Center, al norte de Jaguar Gym.", "keywords": ["fisioterapia", "physiotherapy", "fisio", "terapia fisica", "rehabilitacion", "clinica fisioterapia"]
    },
    {
        "placeId": "jaguarGym", "name": "Gimnasio JAGUAR GYM", "category": CampusCategory.SPORTS,
        "parentBuildingId": "jaguarGym", "floorLevel": 1, "isAccessible": True,
        "latitude": 12.109309, "longitude": -86.258508,
        "locationNotes": "Complejo Deportivo Jaguar Center, con bebedero contiguo.", "keywords": ["gimnasio", "gym", "pesas", "jaguar gym", "entrenar"]
    },
    {
        "placeId": "sportsPsychJC", "name": "Oficina Psicología Deportiva", "category": CampusCategory.ADMINISTRATIVE,
        "parentBuildingId": "jaguarCenter", "floorLevel": 1, "isAccessible": True,
        "latitude": 12.109280, "longitude": -86.258880,
        "locationNotes": "Complejo Deportivo Jaguar Center.", "keywords": ["oficina psicologia deportiva", "psicologia deportiva"]
    },
    # Bodega general y contenedores (buildings.txt lines 370-373)
    {
        "placeId": "generalWarehouseJC", "name": "Bodega General y Contenedores", "category": CampusCategory.ADMINISTRATIVE,
        "parentBuildingId": "jaguarCenter", "floorLevel": 1, "isAccessible": True,
        "latitude": 12.109312, "longitude": -86.258888,
        "locationNotes": "Sector Bodega General y Contenedores.", "keywords": ["bodega general", "bodega general y contenedores", "contenedores"]
    },
    {
        "placeId": "sportsOfficesJC", "name": "Oficinas Deportivas 1-3", "category": CampusCategory.SPORTS,
        "parentBuildingId": "jaguarCenter", "floorLevel": 1, "isAccessible": True,
        "latitude": 12.109252, "longitude": -86.258709,
        "locationNotes": "Sector Bodega General y Complejo Jaguar Center.", "keywords": ["oficinas deportivas 1-3", "oficinas deportivas"]
    },
    {
        "placeId": "staffDiningJC", "name": "Comedor de Colaboradores", "category": CampusCategory.FOOD_AREA,
        "parentBuildingId": "jaguarCenter", "floorLevel": 1, "isAccessible": True,
        "latitude": 12.109312, "longitude": -86.258888,
        "locationNotes": "Sector Bodega General y Complejo Jaguar Center.", "keywords": ["comedor de colaboradores", "comedor colaboradores"]
    },

    # -------------------------------------------------------------------------
    # PLAZA CHILAMATES & CENTRAL OUTDOOR ZONES
    # -------------------------------------------------------------------------
    {
        "placeId": "chilamatesDining",
        "name": "Plaza Chilamates (Módulos Comerciales 1, 2 y 3, Área de Mesas & Fast Point)",
        "category": CampusCategory.FOOD_AREA,
        "parentBuildingId": "chilamatesPlaza",
        "floorLevel": 1,
        "isAccessible": True,
        "latitude": 12.108027,
        "longitude": -86.256705,
        "locationNotes": "Plaza Chilamates: Módulo Comercial 1, 2 y 3 (3 kioskos), Área de Mesas, Fast Point y Máquina Expendedora.",
        "keywords": ["chilamates", "plaza chilamates", "modulo comercial 1 2 y 3", "fast point", "maquina expendedora", "kiosko chilamates", "area de mesas chilamates"]
    },
    {
        "placeId": "jaguarJungleGarden",
        "name": "Jaguar Jungle (Jardín & Senderos Centrales)",
        "category": CampusCategory.FOOD_AREA,
        "parentBuildingId": "jaguarJungle",
        "floorLevel": 1,
        "isAccessible": True,
        "latitude": 12.108073,
        "longitude": -86.257787,
        "locationNotes": "Área verde sombreada entre Edificio O, Mi Ranchito, Edificio H y vía interna.",
        "keywords": ["jaguar jungle", "jungle", "jungla", "jardin jaguar", "area verde", "sendero o h"]
    },
    {
        "placeId": "miRanchitoPavilion",
        "name": "Mi Ranchito (Ranchón Universitario)",
        "category": CampusCategory.FOOD_AREA,
        "parentBuildingId": "miRanchito",
        "floorLevel": 1,
        "isAccessible": True,
        "latitude": 12.108058,
        "longitude": -86.257323,
        "locationNotes": "Pabellón exterior con kiosko y baños (12.108059, -86.257324) junto a Jaguar Jungle y Edificio N.",
        "keywords": ["mi ranchito", "ranchito", "ranchon", "ranch", "kiosko ranchon", "banos ranchito"]
    },
    {
        "placeId": "labDigitalFiaRoom",
        "name": "Lab Digital FIA (Laboratorio Digital de Ingeniería)",
        "category": CampusCategory.FACULTY,
        "parentBuildingId": "labDigitalFia",
        "floorLevel": 1,
        "isAccessible": True,
        "latitude": 12.108110,
        "longitude": -86.257290,
        "locationNotes": "Laboratorio Digital FIA junto al Edificio N, Mi Ranchito y Área de Mesas.",
        "keywords": ["lab digital fia", "laboratorio digital fia", "lab fia", "digital fia", "digital laboratory fia"]
    },
    {
        "placeId": "areaDeMesasTerrace",
        "name": "Área de Mesas (Terraza Exterior de Estudio)",
        "category": CampusCategory.FOOD_AREA,
        "parentBuildingId": "areaDeMesas",
        "floorLevel": 1,
        "isAccessible": True,
        "latitude": 12.108195,
        "longitude": -86.257314,
        "locationNotes": "Mesas exteriores entre Lab Digital FIA, Parqueo Central y Edificio C.",
        "keywords": ["area de mesas", "área de mesas", "mesas", "mesas exteriores", "outdoor tables", "terraza mesas"]
    },

    # -------------------------------------------------------------------------
    # PARKING LOTS & MAIN GATES
    # -------------------------------------------------------------------------
    {
        "placeId": "mainParkingSouth",
        "name": "Parqueo Principal & Caseta Sur",
        "category": CampusCategory.PARKING_LOT,
        "parentBuildingId": "mainParking",
        "floorLevel": 1,
        "isAccessible": True,
        "latitude": 12.109617,
        "longitude": -86.256553,
        "locationNotes": "Acceso vehicular y peatonal principal sur.",
        "keywords": ["parqueo principal", "estacionamiento", "caseta sur", "entrada principal", "porton sur"]
    },
    {
        "placeId": "thirdAccessRoad",
        "name": "Tercer Acceso / Third Access (Portón Copérnico)",
        "category": CampusCategory.PARKING_LOT,
        "parentBuildingId": "northGate",
        "floorLevel": 1,
        "isAccessible": True,
        "latitude": 12.107223,
        "longitude": -86.256261,
        "locationNotes": "Acceso vehicular y peatonal noroeste junto a Estación de Meteorología y Edificio P.",
        "keywords": ["tercer acceso", "third access", "third access road", "acceso 3", "3er acceso", "entrada 3", "porton norte", "caseta norte", "acceso copernico"]
    },
    {
        "placeId": "secondAccessRoad",
        "name": "Segundo Acceso / Camino Estadio Jaguar (Second Access Road)",
        "category": CampusCategory.PARKING_LOT,
        "parentBuildingId": "northeastGate",
        "floorLevel": 1,
        "isAccessible": True,
        "latitude": 12.106364,
        "longitude": -86.258808,
        "locationNotes": "Acceso vehicular y peatonal junto al Estadio de Baseball Jaguar hacia Parqueo Deportes y Edificio O.",
        "keywords": ["segundo acceso", "second access", "camino segundo acceso", "second access road", "jaguar stadium road", "camino estadio jaguar", "acceso 2", "2do acceso", "entrada 2", "acceso deportivo", "porton deportes", "caseta noreste"]
    },

    # -------------------------------------------------------------------------
    # ACCESSIBLE RAMPS (INCLUSIVITY)
    # -------------------------------------------------------------------------
    {
        "placeId": "rampBuildingA",
        "name": "Rampa de Acceso Edificio A",
        "category": CampusCategory.ACCESSIBLE_RAMP,
        "parentBuildingId": "buildingA",
        "floorLevel": 1,
        "isAccessible": True,
        "latitude": 12.108543,
        "longitude": -86.256496,
        "locationNotes": "Rampa de acceso principal al Edificio A.",
        "keywords": ["rampa a", "rampa edificio a", "acceso silla de ruedas a"]
    },
    {
        "placeId": "rampBuildingB",
        "name": "Rampa de Acceso Edificio B",
        "category": CampusCategory.ACCESSIBLE_RAMP,
        "parentBuildingId": "buildingB",
        "floorLevel": 1,
        "isAccessible": True,
        "latitude": 12.108563,
        "longitude": -86.256783,
        "locationNotes": "Rampa de acceso al Edificio B.",
        "keywords": ["rampa b", "rampa edificio b", "acceso inclusivo b"]
    },
    {
        "placeId": "rampBuildingG",
        "name": "Rampa Auditorio Central Edificio G",
        "category": CampusCategory.ACCESSIBLE_RAMP,
        "parentBuildingId": "buildingG",
        "floorLevel": 1,
        "isAccessible": True,
        "latitude": 12.108801,
        "longitude": -86.257410,
        "locationNotes": "Rampa entre Edificios G y F con acceso al Auditorio Central.",
        "keywords": ["rampa g", "rampa auditorio"]
    },
    {
        "placeId": "rampJaguarCenter",
        "name": "Rampa de Acceso Jaguar Center",
        "category": CampusCategory.ACCESSIBLE_RAMP,
        "parentBuildingId": "jaguarCenter",
        "floorLevel": 1,
        "isAccessible": True,
        "latitude": 12.109111,
        "longitude": -86.258514,
        "locationNotes": "Acceso accesible al Complejo Deportivo Jaguar Center.",
        "keywords": ["rampa jaguar center", "rampa gimnasio"]
    }
]


def getPlacesByCategory(category: str):
    """Filters places by their specific CampusCategory string."""
    return [place for place in PLACES_CATALOG if place["category"] == category]


def getPlacesByBuilding(buildingId: str):
    """Retrieves all classrooms, labs or services located inside a specific building."""
    return [place for place in PLACES_CATALOG if place["parentBuildingId"] == buildingId]
