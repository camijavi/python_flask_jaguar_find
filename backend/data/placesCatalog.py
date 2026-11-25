"""
placesCatalog.py
================================================================================
Comprehensive catalog of all campus rooms, labs, faculties, food areas, 
drinking fountains, restrooms, and parking spaces extracted from buildings.txt.
Linked hierarchically to parent buildings with floor level and accessibility.
================================================================================
"""

from backend.data.campusCategories import CampusCategory

# Master list of all internal and external campus points of interest
PLACES_CATALOG = [
    # -------------------------------------------------------------------------
    # BUILDING A: Administrative & Student Services
    # -------------------------------------------------------------------------
    {
        "placeId": "accountingOfficeA",
        "name": "Contabilidad & Finanzas",
        "category": CampusCategory.ADMINISTRATIVE,
        "parentBuildingId": "buildingA",
        "floorLevel": 1,
        "isAccessible": True,
        "locationNotes": "First floor, left hallway near CAE.",
        "keywords": ["contabilidad", "finanzas", "accounting", "cobros"]
    },
    {
        "placeId": "studentCareCenterA",
        "name": "Centro de Atención al Estudiante (CAE)",
        "category": CampusCategory.ADMINISTRATIVE,
        "parentBuildingId": "buildingA",
        "floorLevel": 1,
        "isAccessible": True,
        "locationNotes": "First floor, central lobby.",
        "keywords": ["cae", "atencion al estudiante", "student services", "atencion"]
    },
    {
        "placeId": "academicRecordsA",
        "name": "Registro Académico",
        "category": CampusCategory.ADMINISTRATIVE,
        "parentBuildingId": "buildingA",
        "floorLevel": 1,
        "isAccessible": True,
        "locationNotes": "First floor, main service desk.",
        "keywords": ["registro", "notas", "matricula", "certificados"]
    },
    {
        "placeId": "lostAndFoundOfficeA",
        "name": "Oficina de Objetos Perdidos (JaguarFind)",
        "category": CampusCategory.ADMINISTRATIVE,
        "parentBuildingId": "buildingA",
        "floorLevel": 1,
        "isAccessible": True,
        "locationNotes": "First floor, reception desk.",
        "keywords": ["objetos perdidos", "lost and found", "perdido", "custodia"]
    },
    {
        "placeId": "atmMachinesA",
        "name": "Cajeros Automáticos (BAC y LAFISE)",
        "category": CampusCategory.ADMINISTRATIVE,
        "parentBuildingId": "buildingA",
        "floorLevel": 1,
        "isAccessible": True,
        "latitude": 12.108560,
        "longitude": -86.256574,
        "locationNotes": "Outside Building A, western facade.",
        "keywords": ["cajero", "cajeros", "atm", "bac", "lafise", "dinero", "efectivo"]
    },
    {
        "placeId": "admissionsMarketingA",
        "name": "Dirección de Mercadeo y Admisión (Edificio A)",
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
        "placeId": "collectionsOfficeA",
        "name": "Cartera y Cobro / Dirección Financiera (Edificio A)",
        "category": CampusCategory.ADMINISTRATIVE,
        "parentBuildingId": "buildingA",
        "floorLevel": 1,
        "isAccessible": True,
        "latitude": 12.108543,
        "longitude": -86.256496,
        "locationNotes": "Edificio A, Piso 1, atención financiera.",
        "keywords": ["cartera y cobro", "direccion financiera", "finanzas", "cobro"]
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
        "placeId": "adminDirectorateA",
        "name": "Dirección Administrativa y Logística Académica (A-201)",
        "category": CampusCategory.ADMINISTRATIVE,
        "parentBuildingId": "buildingA",
        "floorLevel": 2,
        "isAccessible": False,
        "latitude": 12.108543,
        "longitude": -86.256609,
        "locationNotes": "Edificio A, Piso 2.",
        "keywords": ["a201", "a-201", "a 201", "direccion administrativa", "logistica academica"]
    },
    {
        "placeId": "ticDirectorateA",
        "name": "Dirección de Tecnología de la Información y Comunicación - TIC (A-203)",
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
        "name": "Mercadeo y Publicidad (A-204)",
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
        "placeId": "hrTalentA",
        "name": "Dirección de Gestión del Talento / Recursos Humanos (A-205)",
        "category": CampusCategory.ADMINISTRATIVE,
        "parentBuildingId": "buildingA",
        "floorLevel": 2,
        "isAccessible": False,
        "latitude": 12.108416,
        "longitude": -86.256709,
        "locationNotes": "Edificio A, Piso 2.",
        "keywords": ["a205", "a-205", "a 205", "direccion de gestion del talento", "recursos humanos", "rrhh"]
    },
    {
        "placeId": "dpaAudiovisualA",
        "name": "Dirección de Producción Audiovisual - DPA (Estudio A-301, Ciclograma, Sonido y Radio)",
        "category": CampusCategory.CLASSROOM,
        "parentBuildingId": "buildingA",
        "floorLevel": 3,
        "isAccessible": False,
        "latitude": 12.108418,
        "longitude": -86.256706,
        "locationNotes": "Edificio A, Piso 3: DPA, Set de grabación ciclograma, estudio de sonido, oficinas auxiliares DPA, control máster y set de radio.",
        "keywords": ["dpa", "a301", "a-301", "a 301", "produccion audiovisual", "set de grabacion ciclograma", "ciclograma", "estudio de sonido", "oficinas auxiliares dpa", "control master", "set de radio"]
    },

    # -------------------------------------------------------------------------
    # BUILDING B: Main Classrooms & Facilities
    # -------------------------------------------------------------------------
    {
        "placeId": "pharmacyB",
        "name": "Módulo Comercial 1 (Farmacia)",
        "category": CampusCategory.ADMINISTRATIVE,
        "parentBuildingId": "buildingB",
        "floorLevel": 1,
        "isAccessible": True,
        "locationNotes": "First floor entrance.",
        "keywords": ["farmacia", "medicamentos", "modulo comercial 1"]
    },
    {
        "placeId": "classroomB101", "name": "Aula B-101", "category": CampusCategory.CLASSROOM,
        "parentBuildingId": "buildingB", "floorLevel": 1, "isAccessible": True,
        "latitude": 12.108563, "longitude": -86.256783,
        "locationNotes": "Edificio B, Piso 1, pasillo este junto a Farmacia.", "keywords": ["b101", "b-101", "b 101", "aula b101"]
    },
    {
        "placeId": "classroomB102", "name": "Aula B-102", "category": CampusCategory.CLASSROOM,
        "parentBuildingId": "buildingB", "floorLevel": 1, "isAccessible": True,
        "latitude": 12.108574, "longitude": -86.256820,
        "locationNotes": "Edificio B, Piso 1, pasillo este.", "keywords": ["b102", "b-102", "b 102", "aula b102"]
    },
    {
        "placeId": "classroomB103", "name": "Aula B-103", "category": CampusCategory.CLASSROOM,
        "parentBuildingId": "buildingB", "floorLevel": 1, "isAccessible": True,
        "latitude": 12.108585, "longitude": -86.256858,
        "locationNotes": "Edificio B, Piso 1, pasillo central.", "keywords": ["b103", "b-103", "b 103", "aula b103"]
    },
    {
        "placeId": "classroomB104", "name": "Aula B-104", "category": CampusCategory.CLASSROOM,
        "parentBuildingId": "buildingB", "floorLevel": 1, "isAccessible": True,
        "latitude": 12.108585, "longitude": -86.256858,
        "locationNotes": "Edificio B, Piso 1, pasillo central.", "keywords": ["b104", "b-104", "b 104", "aula b104"]
    },
    {
        "placeId": "classroomB105", "name": "Aula B-105", "category": CampusCategory.CLASSROOM,
        "parentBuildingId": "buildingB", "floorLevel": 1, "isAccessible": True,
        "latitude": 12.108568, "longitude": -86.256991,
        "locationNotes": "Edificio B, Piso 1, pasillo central.", "keywords": ["b105", "b-105", "b 105", "aula b105"]
    },
    {
        "placeId": "classroomB106", "name": "Aula B-106", "category": CampusCategory.CLASSROOM,
        "parentBuildingId": "buildingB", "floorLevel": 1, "isAccessible": True,
        "latitude": 12.108568, "longitude": -86.256991,
        "locationNotes": "Edificio B, Piso 1, pasillo central.", "keywords": ["b106", "b-106", "b 106", "aula b106"]
    },
    {
        "placeId": "classroomB107", "name": "Aula B-107", "category": CampusCategory.CLASSROOM,
        "parentBuildingId": "buildingB", "floorLevel": 1, "isAccessible": True,
        "latitude": 12.108610, "longitude": -86.257099,
        "locationNotes": "Edificio B, Piso 1, pasillo oeste.", "keywords": ["b107", "b-107", "b 107", "aula b107"]
    },
    {
        "placeId": "classroomB108", "name": "Aula B-108", "category": CampusCategory.CLASSROOM,
        "parentBuildingId": "buildingB", "floorLevel": 1, "isAccessible": True,
        "latitude": 12.108575, "longitude": -86.257225,
        "locationNotes": "Edificio B, Piso 1, pasillo oeste.", "keywords": ["b108", "b-108", "b 108", "aula b108"]
    },
    {
        "placeId": "classroomB109", "name": "Aula B-109", "category": CampusCategory.CLASSROOM,
        "parentBuildingId": "buildingB", "floorLevel": 1, "isAccessible": True,
        "latitude": 12.108575, "longitude": -86.257225,
        "locationNotes": "Edificio B, Piso 1, extremo oeste del pasillo.", "keywords": ["b109", "b-109", "b 109", "aula b109"]
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
        "locationNotes": "First floor central corridor next to restrooms.",
        "keywords": ["bebedero", "agua", "tomar agua", "water fountain", "bebedero b"]
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
        "locationNotes": "Ground floor central hallway.",
        "keywords": ["bano hombres b", "sanitarios b", "bano"]
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
        "locationNotes": "Ground floor central hallway.",
        "keywords": ["bano mujeres b", "sanitarios b", "bano"]
    },
    {
        "placeId": "photocopyShopB",
        "name": "Fotocopias Jaguar Shop",
        "category": CampusCategory.ADMINISTRATIVE,
        "parentBuildingId": "buildingB",
        "floorLevel": 1,
        "isAccessible": True,
        "latitude": 12.108590,
        "longitude": -86.257332,
        "locationNotes": "End of ground floor hallway.",
        "keywords": ["fotocopias", "impresiones", "copias", "jaguar shop b"]
    },
    # Building B Second Floor (B201 - B210)
    {
        "placeId": "classroomB201", "name": "Aula B-201", "category": CampusCategory.CLASSROOM,
        "parentBuildingId": "buildingB", "floorLevel": 2, "isAccessible": False,
        "latitude": 12.108556, "longitude": -86.256730,
        "locationNotes": "Edificio B, Piso 2, extremo este.", "keywords": ["b201", "b-201", "b 201", "aula b201"]
    },
    {
        "placeId": "classroomB202", "name": "Aula B-202", "category": CampusCategory.CLASSROOM,
        "parentBuildingId": "buildingB", "floorLevel": 2, "isAccessible": False,
        "latitude": 12.108527, "longitude": -86.256795,
        "locationNotes": "Edificio B, Piso 2, pasillo este.", "keywords": ["b202", "b-202", "b 202", "aula b202"]
    },
    {
        "placeId": "classroomB203", "name": "Aula B-203", "category": CampusCategory.CLASSROOM,
        "parentBuildingId": "buildingB", "floorLevel": 2, "isAccessible": False,
        "latitude": 12.108527, "longitude": -86.256795,
        "locationNotes": "Edificio B, Piso 2, pasillo este.", "keywords": ["b203", "b-203", "b 203", "aula b203"]
    },
    {
        "placeId": "classroomB204", "name": "Aula B-204", "category": CampusCategory.CLASSROOM,
        "parentBuildingId": "buildingB", "floorLevel": 2, "isAccessible": False,
        "latitude": 12.108552, "longitude": -86.256826,
        "locationNotes": "Edificio B, Piso 2, pasillo central.", "keywords": ["b204", "b-204", "b 204", "aula b204"]
    },
    {
        "placeId": "classroomB205", "name": "Aula B-205", "category": CampusCategory.CLASSROOM,
        "parentBuildingId": "buildingB", "floorLevel": 2, "isAccessible": False,
        "latitude": 12.108552, "longitude": -86.256826,
        "locationNotes": "Edificio B, Piso 2, pasillo central.", "keywords": ["b205", "b-205", "b 205", "aula b205"]
    },
    {
        "placeId": "classroomB206", "name": "Aula B-206", "category": CampusCategory.CLASSROOM,
        "parentBuildingId": "buildingB", "floorLevel": 2, "isAccessible": False,
        "latitude": 12.108558, "longitude": -86.256985,
        "locationNotes": "Edificio B, Piso 2, pasillo central.", "keywords": ["b206", "b-206", "b 206", "aula b206"]
    },
    {
        "placeId": "classroomB207", "name": "Aula B-207", "category": CampusCategory.CLASSROOM,
        "parentBuildingId": "buildingB", "floorLevel": 2, "isAccessible": False,
        "latitude": 12.108507, "longitude": -86.257117,
        "locationNotes": "Edificio B, Piso 2, pasillo oeste.", "keywords": ["b207", "b-207", "b 207", "aula b207"]
    },
    {
        "placeId": "classroomB208", "name": "Aula B-208", "category": CampusCategory.CLASSROOM,
        "parentBuildingId": "buildingB", "floorLevel": 2, "isAccessible": False,
        "latitude": 12.108507, "longitude": -86.257117,
        "locationNotes": "Edificio B, Piso 2, pasillo oeste.", "keywords": ["b208", "b-208", "b 208", "aula b208"]
    },
    {
        "placeId": "classroomB209", "name": "Aula B-209", "category": CampusCategory.CLASSROOM,
        "parentBuildingId": "buildingB", "floorLevel": 2, "isAccessible": False,
        "latitude": 12.108525, "longitude": -86.257271,
        "locationNotes": "Edificio B, Piso 2, extremo oeste junto a las escaleras.", "keywords": ["b209", "b-209", "b 209", "aula b209"]
    },
    {
        "placeId": "classroomB210", "name": "Aula B-210", "category": CampusCategory.CLASSROOM,
        "parentBuildingId": "buildingB", "floorLevel": 2, "isAccessible": False,
        "latitude": 12.108525, "longitude": -86.257271,
        "locationNotes": "Edificio B, Piso 2, extremo oeste junto a las escaleras.", "keywords": ["b210", "b-210", "b 210", "aula b210"]
    },
    {
        "placeId": "drinkingFountainBetweenBC",
        "name": "Bebedero de Agua (Entre Edificio B y C)",
        "category": CampusCategory.DRINKING_FOUNTAIN,
        "parentBuildingId": "buildingB",
        "floorLevel": 1,
        "isAccessible": True,
        "locationNotes": "Outdoor walkway connecting Building B and Building C.",
        "keywords": ["bebedero entre b y c", "agua b c", "bebedero exterior"]
    },

    # -------------------------------------------------------------------------
    # BUILDING C: Classrooms, Computer Labs, Cashier & Treasury (Floors 1, 2, 3)
    # -------------------------------------------------------------------------
    # Floor 1
    {
        "placeId": "auditoriumC101",
        "name": "Auditorio C-101",
        "category": CampusCategory.AUDITORIUM,
        "parentBuildingId": "buildingC",
        "floorLevel": 1,
        "isAccessible": True,
        "latitude": 12.108528,
        "longitude": -86.256743,
        "locationNotes": "Planta baja, ala este cerca de las escaleras izquierda.",
        "keywords": ["auditorio c101", "auditorio c", "c101", "c-101"]
    },
    {
        "placeId": "classroomC102",
        "name": "Aula C-102",
        "category": CampusCategory.CLASSROOM,
        "parentBuildingId": "buildingC",
        "floorLevel": 1,
        "isAccessible": True,
        "latitude": 12.108549,
        "longitude": -86.256848,
        "locationNotes": "Planta baja, pasillo central este.",
        "keywords": ["c102", "c-102", "aula c102"]
    },
    {
        "placeId": "classroomC103",
        "name": "Aula C-103",
        "category": CampusCategory.CLASSROOM,
        "parentBuildingId": "buildingC",
        "floorLevel": 1,
        "isAccessible": True,
        "latitude": 12.108527,
        "longitude": -86.256908,
        "locationNotes": "Planta baja, pasillo central.",
        "keywords": ["c103", "c-103", "aula c103"]
    },
    {
        "placeId": "classroomC104",
        "name": "Aula C-104",
        "category": CampusCategory.CLASSROOM,
        "parentBuildingId": "buildingC",
        "floorLevel": 1,
        "isAccessible": True,
        "latitude": 12.108583,
        "longitude": -86.256918,
        "locationNotes": "Planta baja, pasillo central.",
        "keywords": ["c104", "c-104", "aula c104"]
    },
    {
        "placeId": "drinkingFountainC1",
        "name": "Bebedero de Agua (Edificio C - Piso 1)",
        "category": CampusCategory.DRINKING_FOUNTAIN,
        "parentBuildingId": "buildingC",
        "floorLevel": 1,
        "isAccessible": True,
        "latitude": 12.108527,
        "longitude": -86.256908,
        "locationNotes": "Planta baja, junto al Aula C-103.",
        "keywords": ["bebedero c", "agua c", "bebedero c1"]
    },
    {
        "placeId": "treasuryC105",
        "name": "Tesorería UAM (C-105)",
        "category": CampusCategory.ADMINISTRATIVE,
        "parentBuildingId": "buildingC",
        "floorLevel": 1,
        "isAccessible": True,
        "latitude": 12.108557,
        "longitude": -86.257120,
        "locationNotes": "Planta baja, oficina de tesorería institucional.",
        "keywords": ["tesoreria", "c105", "c-105", "finanzas", "tesoreria uam"]
    },
    {
        "placeId": "cashierUamC",
        "name": "Caja UAM (Atención Financiera)",
        "category": CampusCategory.ADMINISTRATIVE,
        "parentBuildingId": "buildingC",
        "floorLevel": 1,
        "isAccessible": True,
        "latitude": 12.108446,
        "longitude": -86.257021,
        "locationNotes": "Planta baja, vestíbulo central frente a rampa accesible.",
        "keywords": ["caja", "caja uam", "pagos", "aranceles", "colegiatura", "cashier"]
    },
    {
        "placeId": "mapUamC_F1",
        "name": "Mapa UAM (Entrada Edificio C)",
        "category": CampusCategory.ADMINISTRATIVE,
        "parentBuildingId": "buildingC",
        "floorLevel": 1,
        "isAccessible": True,
        "latitude": 12.108446,
        "longitude": -86.257021,
        "locationNotes": "Planta baja, entrada y directorio.",
        "keywords": ["mapa", "mapa uam", "directorio edificio c"]
    },
    {
        "placeId": "rampC_F1",
        "name": "Rampa Accesible Edificio C",
        "category": CampusCategory.ACCESSIBLE_RAMP,
        "parentBuildingId": "buildingC",
        "floorLevel": 1,
        "isAccessible": True,
        "latitude": 12.108394,
        "longitude": -86.256997,
        "locationNotes": "Acceso accesible exterior frente al vestíbulo de Caja.",
        "keywords": ["rampa", "rampla", "rampa c", "rampa accesible edificio c"]
    },
    {
        "placeId": "classroomC106",
        "name": "Aula C-106",
        "category": CampusCategory.CLASSROOM,
        "parentBuildingId": "buildingC",
        "floorLevel": 1,
        "isAccessible": True,
        "latitude": 12.108522,
        "longitude": -86.257194,
        "locationNotes": "Planta baja, pasillo oeste.",
        "keywords": ["c106", "c-106", "aula c106"]
    },
    {
        "placeId": "macLabC107",
        "name": "Laboratorio MAC (C-107)",
        "category": CampusCategory.CLASSROOM,
        "parentBuildingId": "buildingC",
        "floorLevel": 1,
        "isAccessible": True,
        "latitude": 12.108540,
        "longitude": -86.257206,
        "locationNotes": "Planta baja, ala oeste de cómputo.",
        "keywords": ["mac 107", "lab mac", "computadoras apple", "c107", "c-107"]
    },
    {
        "placeId": "erasmusLabC108",
        "name": "Laboratorio ACAI-Erasmus+ (C-108)",
        "category": CampusCategory.CLASSROOM,
        "parentBuildingId": "buildingC",
        "floorLevel": 1,
        "isAccessible": True,
        "latitude": 12.108531,
        "longitude": -86.257233,
        "locationNotes": "Planta baja, ala oeste de cómputo.",
        "keywords": ["erasmus", "acai", "c108", "c-108", "lab computacion acai"]
    },
    {
        "placeId": "auditoriumC109",
        "name": "Auditorio C-109",
        "category": CampusCategory.AUDITORIUM,
        "parentBuildingId": "buildingC",
        "floorLevel": 1,
        "isAccessible": True,
        "latitude": 12.108581,
        "longitude": -86.257279,
        "locationNotes": "Planta baja, extremo oeste junto a escaleras derecha.",
        "keywords": ["auditorio c109", "auditorio 109", "c109", "c-109"]
    },

    # Floor 2
    {
        "placeId": "computerLabC201",
        "name": "Laboratorio de Cómputo (C-201)",
        "category": CampusCategory.CLASSROOM,
        "parentBuildingId": "buildingC",
        "floorLevel": 2,
        "isAccessible": False,
        "latitude": 12.108453,
        "longitude": -86.256760,
        "locationNotes": "Segundo piso, ala este de laboratorios.",
        "keywords": ["c201", "c-201", "lab computo 201", "laboratorio de computacion"]
    },
    {
        "placeId": "computerLabC202",
        "name": "Laboratorio de Cómputo (C-202)",
        "category": CampusCategory.CLASSROOM,
        "parentBuildingId": "buildingC",
        "floorLevel": 2,
        "isAccessible": False,
        "latitude": 12.108415,
        "longitude": -86.256742,
        "locationNotes": "Segundo piso, junto a escaleras izquierda.",
        "keywords": ["c202", "c-202", "lab computo 202", "laboratorio de computacion"]
    },
    {
        "placeId": "macLabC203",
        "name": "Laboratorio MAC (C-203)",
        "category": CampusCategory.CLASSROOM,
        "parentBuildingId": "buildingC",
        "floorLevel": 2,
        "isAccessible": False,
        "latitude": 12.108528,
        "longitude": -86.256800,
        "locationNotes": "Segundo piso, laboratorio de diseño y MAC.",
        "keywords": ["mac 203", "c203", "c-203", "lab mac 203", "laboratorio mac c203"]
    },
    {
        "placeId": "computerLabC204",
        "name": "Laboratorio de Cómputo (C-204)",
        "category": CampusCategory.CLASSROOM,
        "parentBuildingId": "buildingC",
        "floorLevel": 2,
        "isAccessible": False,
        "latitude": 12.108510,
        "longitude": -86.256951,
        "locationNotes": "Segundo piso, pasillo central.",
        "keywords": ["c204", "c-204", "lab computo 204", "laboratorio de computacion"]
    },
    {
        "placeId": "drinkingFountainC2",
        "name": "Bebedero de Agua (Edificio C - Piso 2)",
        "category": CampusCategory.DRINKING_FOUNTAIN,
        "parentBuildingId": "buildingC",
        "floorLevel": 2,
        "isAccessible": False,
        "latitude": 12.108510,
        "longitude": -86.256951,
        "locationNotes": "Segundo piso, junto al Lab C-204.",
        "keywords": ["bebedero c2", "agua c2", "bebedero piso 2"]
    },
    {
        "placeId": "computerLabC205",
        "name": "Laboratorio de Cómputo (C-205)",
        "category": CampusCategory.CLASSROOM,
        "parentBuildingId": "buildingC",
        "floorLevel": 2,
        "isAccessible": False,
        "latitude": 12.108433,
        "longitude": -86.257043,
        "locationNotes": "Segundo piso, pasillo central.",
        "keywords": ["c205", "c-205", "lab computo 205", "laboratorio de computacion"]
    },
    {
        "placeId": "warehouseC206",
        "name": "Bodega de Logística Académica (C-206)",
        "category": CampusCategory.ADMINISTRATIVE,
        "parentBuildingId": "buildingC",
        "floorLevel": 2,
        "isAccessible": False,
        "latitude": 12.108435,
        "longitude": -86.257044,
        "locationNotes": "Segundo piso, almacén y logística.",
        "keywords": ["c206", "c-206", "bodega", "logistica academica"]
    },
    {
        "placeId": "restroomsMenC2",
        "name": "Servicios Sanitarios Hombres (Edificio C - Piso 2)",
        "category": CampusCategory.RESTROOM,
        "parentBuildingId": "buildingC",
        "floorLevel": 2,
        "isAccessible": False,
        "latitude": 12.108423,
        "longitude": -86.257051,
        "locationNotes": "Segundo piso, bloque central.",
        "keywords": ["baños hombres c", "banos hombres c", "sanitarios hombres c"]
    },
    {
        "placeId": "restroomsWomenC2",
        "name": "Servicios Sanitarios Mujeres (Edificio C - Piso 2)",
        "category": CampusCategory.RESTROOM,
        "parentBuildingId": "buildingC",
        "floorLevel": 2,
        "isAccessible": False,
        "latitude": 12.108423,
        "longitude": -86.257051,
        "locationNotes": "Segundo piso, bloque central.",
        "keywords": ["baños mujeres c", "banos mujeres c", "sanitarios mujeres c"]
    },
    {
        "placeId": "classroomC209",
        "name": "Aula C-209",
        "category": CampusCategory.CLASSROOM,
        "parentBuildingId": "buildingC",
        "floorLevel": 2,
        "isAccessible": False,
        "latitude": 12.108496,
        "longitude": -86.257203,
        "locationNotes": "Segundo piso, pasillo oeste.",
        "keywords": ["c209", "c-209", "aula c209"]
    },
    {
        "placeId": "classroomC210",
        "name": "Aula C-210",
        "category": CampusCategory.CLASSROOM,
        "parentBuildingId": "buildingC",
        "floorLevel": 2,
        "isAccessible": False,
        "latitude": 12.108491,
        "longitude": -86.257192,
        "locationNotes": "Segundo piso, pasillo oeste.",
        "keywords": ["c210", "c-210", "aula c210"]
    },
    {
        "placeId": "classroomC211",
        "name": "Aula C-211",
        "category": CampusCategory.CLASSROOM,
        "parentBuildingId": "buildingC",
        "floorLevel": 2,
        "isAccessible": False,
        "latitude": 12.108500,
        "longitude": -86.257267,
        "locationNotes": "Segundo piso, extremo oeste junto a escaleras derecha.",
        "keywords": ["c211", "c-211", "aula c211"]
    },

    # Floor 3
    {
        "placeId": "studioA301",
        "name": "Estudio Audiovisual A-301 (Piso 3)",
        "category": CampusCategory.CLASSROOM,
        "parentBuildingId": "buildingC",
        "floorLevel": 3,
        "isAccessible": False,
        "latitude": 12.108418,
        "longitude": -86.256706,
        "locationNotes": "Tercer piso, extremo este sobre conexión A y C.",
        "keywords": ["a301", "a-301", "estudio audiovisual", "audio visual"]
    },
    {
        "placeId": "classroomC301",
        "name": "Aula C-301",
        "category": CampusCategory.CLASSROOM,
        "parentBuildingId": "buildingC",
        "floorLevel": 3,
        "isAccessible": False,
        "latitude": 12.108406,
        "longitude": -86.256819,
        "locationNotes": "Tercer piso, pasillo este.",
        "keywords": ["c301", "c-301", "aula c301"]
    },
    {
        "placeId": "classroomC302",
        "name": "Aula C-302",
        "category": CampusCategory.CLASSROOM,
        "parentBuildingId": "buildingC",
        "floorLevel": 3,
        "isAccessible": False,
        "latitude": 12.108418,
        "longitude": -86.256821,
        "locationNotes": "Tercer piso, pasillo este.",
        "keywords": ["c302", "c-302", "aula c302"]
    },
    {
        "placeId": "classroomC303",
        "name": "Aula C-303",
        "category": CampusCategory.CLASSROOM,
        "parentBuildingId": "buildingC",
        "floorLevel": 3,
        "isAccessible": False,
        "latitude": 12.108434,
        "longitude": -86.256861,
        "locationNotes": "Tercer piso, pasillo central este.",
        "keywords": ["c303", "c-303", "aula c303"]
    },
    {
        "placeId": "classroomC304",
        "name": "Aula C-304",
        "category": CampusCategory.CLASSROOM,
        "parentBuildingId": "buildingC",
        "floorLevel": 3,
        "isAccessible": False,
        "latitude": 12.108415,
        "longitude": -86.257020,
        "locationNotes": "Tercer piso, pasillo central.",
        "keywords": ["c304", "c-304", "c 304", "aula c304"]
    },
    {
        "placeId": "classroomC305",
        "name": "Aula C-305",
        "category": CampusCategory.CLASSROOM,
        "parentBuildingId": "buildingC",
        "floorLevel": 3,
        "isAccessible": False,
        "latitude": 12.108408,
        "longitude": -86.257028,
        "locationNotes": "Tercer piso, pasillo central entre C-304 y Coordinación de Compras.",
        "keywords": ["c305", "c-305", "c 305", "aula c305"]
    },
    {
        "placeId": "procurementCoordC306",
        "name": "Coordinación de Compras (C-306)",
        "category": CampusCategory.ADMINISTRATIVE,
        "parentBuildingId": "buildingC",
        "floorLevel": 3,
        "isAccessible": False,
        "latitude": 12.108402,
        "longitude": -86.257035,
        "locationNotes": "Tercer piso, departamento administrativo de compras.",
        "keywords": ["compras", "c306", "c-306", "coordinacion de compras"]
    },
    {
        "placeId": "classroomC307",
        "name": "Aula C-307",
        "category": CampusCategory.CLASSROOM,
        "parentBuildingId": "buildingC",
        "floorLevel": 3,
        "isAccessible": False,
        "latitude": 12.108395,
        "longitude": -86.257064,
        "locationNotes": "Tercer piso, pasillo central oeste.",
        "keywords": ["c307", "c-307", "aula c307"]
    },
    {
        "placeId": "classroomC308",
        "name": "Aula C-308",
        "category": CampusCategory.CLASSROOM,
        "parentBuildingId": "buildingC",
        "floorLevel": 3,
        "isAccessible": False,
        "latitude": 12.108397,
        "longitude": -86.257083,
        "locationNotes": "Tercer piso, pasillo central oeste.",
        "keywords": ["c308", "c-308", "aula c308"]
    },
    {
        "placeId": "classroomC309",
        "name": "Aula C-309",
        "category": CampusCategory.CLASSROOM,
        "parentBuildingId": "buildingC",
        "floorLevel": 3,
        "isAccessible": False,
        "latitude": 12.108420,
        "longitude": -86.257240,
        "locationNotes": "Tercer piso, pasillo oeste.",
        "keywords": ["c309", "c-309", "aula c309"]
    },
    {
        "placeId": "classroomC310",
        "name": "Aula C-310",
        "category": CampusCategory.CLASSROOM,
        "parentBuildingId": "buildingC",
        "floorLevel": 3,
        "isAccessible": False,
        "latitude": 12.108376,
        "longitude": -86.257292,
        "locationNotes": "Tercer piso, extremo oeste junto a escaleras derecha.",
        "keywords": ["c310", "c-310", "aula c310"]
    },

    # -------------------------------------------------------------------------
    # BUILDING D: Digital Dentistry
    # -------------------------------------------------------------------------
    {
        "placeId": "camCamLabD",
        "name": "Laboratorio de Odontología Digital CAM-CAM",
        "category": CampusCategory.DENTAL_LAB,
        "parentBuildingId": "buildingD",
        "floorLevel": 1,
        "isAccessible": True,
        "latitude": 12.108046,
        "longitude": -86.256819,
        "locationNotes": "Edificio D, Planta Única, laboratorio odontológico este.",
        "keywords": ["cam cam", "odontologia digital", "cad cam", "lab d"]
    },
    {
        "placeId": "classroomD102",
        "name": "Aula D-102",
        "category": CampusCategory.CLASSROOM,
        "parentBuildingId": "buildingD",
        "floorLevel": 1,
        "isAccessible": True,
        "latitude": 12.108029,
        "longitude": -86.256911,
        "locationNotes": "Edificio D, Planta Única, aula central sur.",
        "keywords": ["d102", "d 102", "aula d102", "salon d102", "aula d"]
    },
    {
        "placeId": "customerServiceD",
        "name": "Oficina de Servicio al Cliente",
        "category": CampusCategory.ADMINISTRATIVE,
        "parentBuildingId": "buildingD",
        "floorLevel": 1,
        "isAccessible": True,
        "latitude": 12.108128,
        "longitude": -86.256945,
        "locationNotes": "Edificio D, Planta Única, área de atención en lobby.",
        "keywords": ["servicio al cliente", "atencion d", "oficina d", "servicio d"]
    },
    {
        "placeId": "meetingRoomD",
        "name": "Sala de Reunión (Edificio D)",
        "category": CampusCategory.ADMINISTRATIVE,
        "parentBuildingId": "buildingD",
        "floorLevel": 1,
        "isAccessible": True,
        "latitude": 12.108128,
        "longitude": -86.256945,
        "locationNotes": "Edificio D, Planta Única, sala de reuniones en lobby.",
        "keywords": ["sala de reunion", "sala de reuniones", "reunion d", "sala d"]
    },
    {
        "placeId": "uamMapD",
        "name": "Mapa UAM (Entrada Edificio D)",
        "category": CampusCategory.ADMINISTRATIVE,
        "parentBuildingId": "buildingD",
        "floorLevel": 1,
        "isAccessible": True,
        "latitude": 12.108128,
        "longitude": -86.256945,
        "locationNotes": "Edificio D, Entrada exterior, panel y directorio del Mapa UAM.",
        "keywords": ["mapa uam", "mapa d", "directorio d", "entrada d"]
    },

    # -------------------------------------------------------------------------
    # BUILDING E: Medical Sciences & Clinics
    # -------------------------------------------------------------------------
    {
        "placeId": "facultyMedicineE",
        "name": "Facultad de Ciencias Médicas",
        "category": CampusCategory.FACULTY,
        "parentBuildingId": "buildingE",
        "floorLevel": 1,
        "isAccessible": True,
        "locationNotes": "Ground floor deanery office.",
        "keywords": ["facultad de medicina", "ciencias medicas", "decanatura medicina"]
    },
    {
        "placeId": "medicalClinicsE",
        "name": "Clínicas Médicas UAM",
        "category": CampusCategory.MEDICAL_LAB,
        "parentBuildingId": "buildingE",
        "floorLevel": 1,
        "isAccessible": True,
        "locationNotes": "Ground floor clinical sector.",
        "keywords": ["clinicas medicas", "consulta medica", "medicina"]
    },
    {
        "placeId": "cardiologyCenterE",
        "name": "Centro de Cardiología",
        "category": CampusCategory.MEDICAL_LAB,
        "parentBuildingId": "buildingE",
        "floorLevel": 1,
        "isAccessible": True,
        "locationNotes": "Ground floor specialized center.",
        "keywords": ["cardiologia", "centro de cardiologia", "corazon"]
    },
    {
        "placeId": "accessibleRestroomE",
        "name": "Servicios Sanitarios Mixtos Inclusivos",
        "category": CampusCategory.RESTROOM,
        "parentBuildingId": "buildingE",
        "floorLevel": 1,
        "isAccessible": True,
        "locationNotes": "Ground floor next to general restrooms.",
        "keywords": ["bano discapacitados", "bano accesible", "bano silla de ruedas"]
    },
    {
        "placeId": "studentLifeOfficeE",
        "name": "Dirección de Vida Estudiantil (DVE)",
        "category": CampusCategory.ADMINISTRATIVE,
        "parentBuildingId": "buildingE",
        "floorLevel": 1,
        "isAccessible": True,
        "locationNotes": "West annex.",
        "keywords": ["vida estudiantil", "dve", "asuntos estudiantiles"]
    },
    {
        "placeId": "innovationOfficeE",
        "name": "Dirección de Innovación y Emprendimientos (DIE)",
        "category": CampusCategory.ADMINISTRATIVE,
        "parentBuildingId": "buildingE",
        "floorLevel": 1,
        "isAccessible": True,
        "locationNotes": "North annex.",
        "keywords": ["die", "innovacion", "emprendimiento"]
    },
    {
        "placeId": "medicalSimulatorsE2",
        "name": "Laboratorio Simuladores de Habilidades Medicina",
        "category": CampusCategory.MEDICAL_LAB,
        "parentBuildingId": "buildingE",
        "floorLevel": 2,
        "isAccessible": False,
        "latitude": 12.108874,
        "longitude": -86.257213,
        "locationNotes": "Second floor medical skills ward (E-201).",
        "keywords": ["e201", "e-201", "simuladores", "simuladores medicina", "laboratorio simuladores de medicina", "lab habilidades"]
    },
    {
        "placeId": "psychologyOfficeE",
        "name": "Oficina de Psicología (Edificio E)",
        "category": CampusCategory.ADMINISTRATIVE,
        "parentBuildingId": "buildingE",
        "floorLevel": 2,
        "isAccessible": False,
        "latitude": 12.109180,
        "longitude": -86.257158,
        "locationNotes": "Edificio E, atención psicológica.",
        "keywords": ["oficina psicologia", "oficina de psicologia", "psicologia", "psicologa"]
    },
    {
        "placeId": "clinicalMedicineLabE",
        "name": "Laboratorio Clínico de Medicina (Edificio E)",
        "category": CampusCategory.MEDICAL_LAB,
        "parentBuildingId": "buildingE",
        "floorLevel": 2,
        "isAccessible": False,
        "latitude": 12.109286,
        "longitude": -86.257194,
        "locationNotes": "Edificio E, laboratorio clínico.",
        "keywords": ["laboratorio clinico de medicina", "laboratorio clinico", "lab clinico"]
    },

    # -------------------------------------------------------------------------
    # BUILDING F: Business, Economics & Marketing
    # -------------------------------------------------------------------------
    {
        "placeId": "facultyBusinessF",
        "name": "Facultad de Ciencias Administrativas y Económicas (FCAE)",
        "category": CampusCategory.FACULTY,
        "parentBuildingId": "buildingF",
        "floorLevel": 1,
        "isAccessible": True,
        "locationNotes": "Ground floor.",
        "keywords": ["fcae", "administracion", "economia", "facultad de administracion"]
    },
    {
        "placeId": "facultyMarketingF",
        "name": "Facultad de Marketing, Diseño y Comunicación (FMDCC)",
        "category": CampusCategory.FACULTY,
        "parentBuildingId": "buildingF",
        "floorLevel": 1,
        "isAccessible": True,
        "locationNotes": "Ground floor.",
        "keywords": ["fmdcc", "marketing", "diseno", "comunicacion"]
    },
    {
        "placeId": "postgraduateDirectorateF",
        "name": "Dirección de Posgrados y Educación Continua",
        "category": CampusCategory.ADMINISTRATIVE,
        "parentBuildingId": "buildingF",
        "floorLevel": 1,
        "isAccessible": True,
        "latitude": 12.108939,
        "longitude": -86.257347,
        "locationNotes": "Ground floor.",
        "keywords": ["posgrados", "maestrias", "educacion continua"]
    },
    {
        "placeId": "teachersLoungeF",
        "name": "Salón de Profesores (Edificio F)",
        "category": CampusCategory.FACULTY,
        "parentBuildingId": "buildingF",
        "floorLevel": 1,
        "isAccessible": True,
        "latitude": 12.108908,
        "longitude": -86.257390,
        "locationNotes": "Edificio F, Planta Baja.",
        "keywords": ["salon de profesores", "profesores f"]
    },

    # -------------------------------------------------------------------------
    # BUILDING G: Law School & Central Auditorium
    # -------------------------------------------------------------------------
    {
        "placeId": "facultyLawG",
        "name": "Facultad de Ciencias Jurídicas y Relaciones Internacionales",
        "category": CampusCategory.FACULTY,
        "parentBuildingId": "buildingG",
        "floorLevel": 1,
        "isAccessible": True,
        "locationNotes": "First floor.",
        "keywords": ["derecho", "relaciones internacionales", "juridicas", "fcjhri"]
    },
    {
        "placeId": "languageCenterG",
        "name": "Language Center UAM",
        "category": CampusCategory.CLASSROOM,
        "parentBuildingId": "buildingG",
        "floorLevel": 1,
        "isAccessible": True,
        "locationNotes": "First floor wing.",
        "keywords": ["language center", "ingles", "idiomas"]
    },
    {
        "placeId": "auditoriumCentralG",
        "name": "Auditorio Central / Auditorio Rubén Darío",
        "category": CampusCategory.AUDITORIUM,
        "parentBuildingId": "buildingG",
        "floorLevel": 2,
        "isAccessible": True, # Elevator / ramp access available
        "locationNotes": "Second floor main auditorium hall.",
        "keywords": ["auditorio central", "ruben dario", "auditorio g", "graduaciones"]
    },
    {
        "placeId": "accessibleRestroomG",
        "name": "Servicios Sanitarios Mixtos Inclusivos (Edificio G)",
        "category": CampusCategory.RESTROOM,
        "parentBuildingId": "buildingG",
        "floorLevel": 1,
        "isAccessible": True,
        "latitude": 12.108652,
        "longitude": -86.257520,
        "locationNotes": "First floor near entrance.",
        "keywords": ["bano accesible g", "bano silla de ruedas g", "banos mixtos", "banos para personas con discapacidades mixtos"]
    },
    {
        "placeId": "auditoriumFcjhriG",
        "name": "Auditorio FCJHRI (Edificio G)",
        "category": CampusCategory.AUDITORIUM,
        "parentBuildingId": "buildingG",
        "floorLevel": 1,
        "isAccessible": True,
        "latitude": 12.108630,
        "longitude": -86.257479,
        "locationNotes": "Edificio G, Piso 1, Facultad de Ciencias Jurídicas.",
        "keywords": ["auditorio fcjhri", "fcjhri", "auditorio derecho"]
    },
    {
        "placeId": "mediationCenterG",
        "name": "Centro de Mediación y Arbitraje (Edificio G)",
        "category": CampusCategory.ADMINISTRATIVE,
        "parentBuildingId": "buildingG",
        "floorLevel": 1,
        "isAccessible": True,
        "latitude": 12.108630,
        "longitude": -86.257479,
        "locationNotes": "Edificio G, Piso 1.",
        "keywords": ["centro de mediacion y arbitraje", "centro de mediacion", "arbitraje", "mediacion"]
    },
    {
        "placeId": "uamCollegeG",
        "name": "UAM College & Relaciones Internacionales (Edificio G)",
        "category": CampusCategory.FACULTY,
        "parentBuildingId": "buildingG",
        "floorLevel": 1,
        "isAccessible": True,
        "latitude": 12.108779,
        "longitude": -86.257498,
        "locationNotes": "Edificio G, Piso 1.",
        "keywords": ["uam college", "direccion de relaciones internacionales e internacionalizacion", "relaciones internacionales", "internacionalizacion"]
    },

    # -------------------------------------------------------------------------
    # BUILDING H: Medical Laboratories (H101 - H107, H201 - H207)
    # -------------------------------------------------------------------------
    {
        "placeId": "medicalLabH101", "name": "Laboratorio de Medicina H-101",
        "category": CampusCategory.MEDICAL_LAB, "parentBuildingId": "buildingH", "floorLevel": 1,
        "isAccessible": True, "latitude": 12.108272, "longitude": -86.257569,
        "locationNotes": "Edificio H, Piso 1.", "keywords": ["h101", "h-101", "h 101", "lab med h101"]
    },
    {
        "placeId": "medicalLabH102", "name": "Laboratorio de Medicina H-102",
        "category": CampusCategory.MEDICAL_LAB, "parentBuildingId": "buildingH", "floorLevel": 1,
        "isAccessible": True, "latitude": 12.108265, "longitude": -86.257549,
        "locationNotes": "Edificio H, Piso 1.", "keywords": ["h102", "h-102", "h 102", "lab med h102", "i108", "i-108"]
    },
    {
        "placeId": "medicalLabH103", "name": "Laboratorio de Medicina H-103",
        "category": CampusCategory.MEDICAL_LAB, "parentBuildingId": "buildingH", "floorLevel": 1,
        "isAccessible": True, "latitude": 12.108265, "longitude": -86.257549,
        "locationNotes": "Edificio H, Piso 1.", "keywords": ["h103", "h-103", "h 103", "lab med h103"]
    },
    {
        "placeId": "medicalLabH104", "name": "Laboratorio de Medicina H-104 (Coordinación de Gestión de Calidad)",
        "category": CampusCategory.MEDICAL_LAB, "parentBuildingId": "buildingH", "floorLevel": 1,
        "isAccessible": True, "latitude": 12.108263, "longitude": -86.257695,
        "locationNotes": "Edificio H, Piso 1.", "keywords": ["h104", "h-104", "h 104", "lab med h104", "coordinacion de gestion de calidad", "gestion de calidad"]
    },
    {
        "placeId": "medicalLabH105", "name": "Laboratorio de Medicina H-105",
        "category": CampusCategory.MEDICAL_LAB, "parentBuildingId": "buildingH", "floorLevel": 1,
        "isAccessible": True, "latitude": 12.108200, "longitude": -86.257812,
        "locationNotes": "Edificio H, Piso 1.", "keywords": ["h105", "h-105", "h 105", "lab med h105"]
    },
    {
        "placeId": "medicalLabH106", "name": "Laboratorio de Medicina H-106",
        "category": CampusCategory.MEDICAL_LAB, "parentBuildingId": "buildingH", "floorLevel": 1,
        "isAccessible": True, "latitude": 12.108156, "longitude": -86.257708,
        "locationNotes": "Edificio H, Piso 1.", "keywords": ["h106", "h-106", "h 106", "lab med h106"]
    },
    {
        "placeId": "medicalLabH107", "name": "Laboratorio de Medicina H-107",
        "category": CampusCategory.MEDICAL_LAB, "parentBuildingId": "buildingH", "floorLevel": 1,
        "isAccessible": True, "latitude": 12.108156, "longitude": -86.257708,
        "locationNotes": "Edificio H, Piso 1.", "keywords": ["h107", "h-107", "h 107", "lab med h107"]
    },
    {
        "placeId": "labSupervisionOfficeH", "name": "Oficina de Supervisión de Laboratorios de Medicina",
        "category": CampusCategory.MEDICAL_LAB, "parentBuildingId": "buildingH", "floorLevel": 2,
        "isAccessible": False, "latitude": 12.108304, "longitude": -86.257660,
        "locationNotes": "Edificio H, Supervisión de Laboratorios y acceso Necroteca.",
        "keywords": ["oficina de supervision de laboratorios de medicina", "supervision laboratorios", "necroteca"]
    },
    {
        "placeId": "medicalLabH201", "name": "Laboratorio de Medicina H-201",
        "category": CampusCategory.MEDICAL_LAB, "parentBuildingId": "buildingH", "floorLevel": 2,
        "isAccessible": False, "latitude": 12.108236, "longitude": -86.257552,
        "locationNotes": "Edificio H, Piso 2.", "keywords": ["h201", "h-201", "h 201", "lab med h201"]
    },
    {
        "placeId": "medicalLabH202", "name": "Laboratorio de Medicina H-202",
        "category": CampusCategory.MEDICAL_LAB, "parentBuildingId": "buildingH", "floorLevel": 2,
        "isAccessible": False, "latitude": 12.108231, "longitude": -86.257608,
        "locationNotes": "Edificio H, Piso 2.", "keywords": ["h202", "h-202", "h 202", "lab med h202"]
    },
    {
        "placeId": "medicalLabH203", "name": "Laboratorio de Medicina H-203",
        "category": CampusCategory.MEDICAL_LAB, "parentBuildingId": "buildingH", "floorLevel": 2,
        "isAccessible": False, "latitude": 12.108270, "longitude": -86.257560,
        "locationNotes": "Edificio H, Piso 2.", "keywords": ["h203", "h-203", "h 203", "lab med h203"]
    },
    {
        "placeId": "medicalLabH204", "name": "Laboratorio de Medicina H-204",
        "category": CampusCategory.MEDICAL_LAB, "parentBuildingId": "buildingH", "floorLevel": 2,
        "isAccessible": False, "latitude": 12.108270, "longitude": -86.257560,
        "locationNotes": "Edificio H, Piso 2.", "keywords": ["h204", "h-204", "h 204", "lab med h204"]
    },
    {
        "placeId": "medicalLabH205", "name": "Laboratorio de Medicina H-205",
        "category": CampusCategory.MEDICAL_LAB, "parentBuildingId": "buildingH", "floorLevel": 2,
        "isAccessible": False, "latitude": 12.108211, "longitude": -86.257727,
        "locationNotes": "Edificio H, Piso 2.", "keywords": ["h205", "h-205", "h 205", "lab med h205"]
    },
    {
        "placeId": "medicalLabH206", "name": "Laboratorio de Medicina H-206",
        "category": CampusCategory.MEDICAL_LAB, "parentBuildingId": "buildingH", "floorLevel": 2,
        "isAccessible": False, "latitude": 12.108211, "longitude": -86.257727,
        "locationNotes": "Edificio H, Piso 2.", "keywords": ["h206", "h-206", "h 206", "lab med h206"]
    },
    {
        "placeId": "medicalLabH207", "name": "Laboratorio de Medicina H-207",
        "category": CampusCategory.MEDICAL_LAB, "parentBuildingId": "buildingH", "floorLevel": 2,
        "isAccessible": False, "latitude": 12.108211, "longitude": -86.257727,
        "locationNotes": "Edificio H, Piso 2.", "keywords": ["h207", "h-207", "h 207", "lab med h207"]
    },

    # -------------------------------------------------------------------------
    # BUILDING I: Rectorate & Central Library
    # -------------------------------------------------------------------------
    {
        "placeId": "centralLibraryI",
        "name": "Biblioteca Central Pablo Antonio Cuadra",
        "category": CampusCategory.ADMINISTRATIVE,
        "parentBuildingId": "buildingI",
        "floorLevel": 1,
        "isAccessible": True,
        "locationNotes": "Main entrance wing.",
        "keywords": ["biblioteca", "libros", "estudiar", "cubiculos biblioteca", "library"]
    },
    {
        "placeId": "rectorateOfficeI",
        "name": "Rectoría UAM",
        "category": CampusCategory.ADMINISTRATIVE,
        "parentBuildingId": "buildingI",
        "floorLevel": 1,
        "isAccessible": True,
        "locationNotes": "Executive wing.",
        "keywords": ["rectoria", "rector", "vicepresidencia", "secretaria general"]
    },

    # -------------------------------------------------------------------------
    # BUILDING J: Pre-Clinical Dentistry Labs
    # -------------------------------------------------------------------------
    {
        "placeId": "dentalLabJ101",
        "name": "Laboratorio de Odontología J-101",
        "category": CampusCategory.DENTAL_LAB,
        "parentBuildingId": "buildingJ",
        "floorLevel": 1,
        "isAccessible": True,
        "latitude": 12.108126,
        "longitude": -86.256780,
        "locationNotes": "Edificio J, Planta Única, laboratorio norte.",
        "keywords": ["j101", "j 101", "lab odonto j", "lab j101", "simulacion dental"]
    },
    {
        "placeId": "dentalLabJ102",
        "name": "Laboratorio de Odontología J-102",
        "category": CampusCategory.DENTAL_LAB,
        "parentBuildingId": "buildingJ",
        "floorLevel": 1,
        "isAccessible": True,
        "latitude": 12.108094,
        "longitude": -86.256756,
        "locationNotes": "Edificio J, Planta Única, laboratorio sureste.",
        "keywords": ["j102", "j 102", "lab odonto j102", "lab j102"]
    },
    {
        "placeId": "restroomsWomenJ",
        "name": "Servicios Sanitarios Mujeres (Edificio J)",
        "category": CampusCategory.RESTROOM,
        "parentBuildingId": "buildingJ",
        "floorLevel": 1,
        "isAccessible": True,
        "latitude": 12.108070,
        "longitude": -86.256815,
        "locationNotes": "Edificio J, Planta Única, pasillo oeste.",
        "keywords": ["baño mujeres j", "baños mujeres j", "sanitarios mujeres j", "baños j"]
    },
    {
        "placeId": "restroomsMenJ",
        "name": "Servicios Sanitarios Hombres (Edificio J)",
        "category": CampusCategory.RESTROOM,
        "parentBuildingId": "buildingJ",
        "floorLevel": 1,
        "isAccessible": True,
        "latitude": 12.108030,
        "longitude": -86.256830,
        "locationNotes": "Edificio J, Planta Única, pasillo suroeste.",
        "keywords": ["baño hombres j", "baños hombres j", "sanitarios hombres j", "baño j"]
    },
    {
        "placeId": "entranceJ",
        "name": "Entrada Principal Edificio J",
        "category": CampusCategory.DENTAL_LAB,
        "parentBuildingId": "buildingJ",
        "floorLevel": 1,
        "isAccessible": True,
        "latitude": 12.108126,
        "longitude": -86.256780,
        "locationNotes": "Edificio J, Acceso principal exterior.",
        "keywords": ["entrada j", "acceso j", "edificio j"]
    },

    # -------------------------------------------------------------------------
    # BUILDING K: Dining, Cafeteria & Food Court
    # -------------------------------------------------------------------------
    {
        "placeId": "centralCafeteriaK",
        "name": "Cafeteria Central & Jaguar Corner",
        "category": CampusCategory.FOOD_AREA,
        "parentBuildingId": "buildingK",
        "floorLevel": 1,
        "isAccessible": True,
        "locationNotes": "Ground floor central food court.",
        "keywords": ["cafeteria", "almuerzo", "jaguar corner", "comida", "food court", "comer"]
    },
    {
        "placeId": "foodKiosksK",
        "name": "Kioskos Comerciales & Terrazas K",
        "category": CampusCategory.FOOD_AREA,
        "parentBuildingId": "buildingK",
        "floorLevel": 1,
        "isAccessible": True,
        "locationNotes": "Terrace area.",
        "keywords": ["kioskos", "kiosko 1", "kiosko 2", "terrazas"]
    },

    # -------------------------------------------------------------------------
    # BUILDING L: Culture, Music & Locker Rooms
    # -------------------------------------------------------------------------
    {
        "placeId": "cultureHallL",
        "name": "Salón de Cultura (Edificio L)",
        "category": CampusCategory.CLASSROOM,
        "parentBuildingId": "buildingL",
        "floorLevel": 1,
        "isAccessible": True,
        "latitude": 12.109123,
        "longitude": -86.258504,
        "locationNotes": "Edificio L, Planta Baja.",
        "keywords": ["salon de cultura", "cultura", "edificio l"]
    },
    {
        "placeId": "musicClassroomL",
        "name": "Aula de Música (Edificio L)",
        "category": CampusCategory.CLASSROOM,
        "parentBuildingId": "buildingL",
        "floorLevel": 1,
        "isAccessible": True,
        "latitude": 12.109120,
        "longitude": -86.258513,
        "locationNotes": "Edificio L, Planta Baja.",
        "keywords": ["aula de musica", "musica", "area de musica"]
    },
    {
        "placeId": "showersTeamsL",
        "name": "Duchas Home y Visitantes (Edificio L)",
        "category": CampusCategory.SPORTS,
        "parentBuildingId": "buildingL",
        "floorLevel": 1,
        "isAccessible": True,
        "latitude": 12.108952,
        "longitude": -86.258551,
        "locationNotes": "Edificio L, vestidores y duchas de equipos.",
        "keywords": ["duchas", "duchas home", "duchas visitantes", "vestidores l"]
    },

    # -------------------------------------------------------------------------
    # BUILDING M: Graduate Studies, Auditoriums & Classrooms (M101-M102, M201-M304)
    # -------------------------------------------------------------------------
    {
        "placeId": "auditoriumM101",
        "name": "Auditorio M-101",
        "category": CampusCategory.AUDITORIUM,
        "parentBuildingId": "buildingM",
        "floorLevel": 1,
        "isAccessible": True,
        "latitude": 12.108452,
        "longitude": -86.257566,
        "locationNotes": "Edificio M, Piso 1, ala norte.",
        "keywords": ["m101", "m-101", "m 101", "auditorio m101"]
    },
    {
        "placeId": "auditoriumM102",
        "name": "Auditorio M-102",
        "category": CampusCategory.AUDITORIUM,
        "parentBuildingId": "buildingM",
        "floorLevel": 1,
        "isAccessible": True,
        "latitude": 12.108439,
        "longitude": -86.257594,
        "locationNotes": "Edificio M, Piso 1, ala norte.",
        "keywords": ["m102", "m-102", "m 102", "auditorio m102"]
    },
    {
        "placeId": "environmentalDirectorateM",
        "name": "Dirección de Gestión Ambiental y Energética (Edificio M)",
        "category": CampusCategory.ADMINISTRATIVE,
        "parentBuildingId": "buildingM",
        "floorLevel": 1,
        "isAccessible": True,
        "latitude": 12.108331,
        "longitude": -86.257559,
        "locationNotes": "Edificio M, Piso 1, ala sur.",
        "keywords": ["direccion de gestion ambiental y energetica", "gestion ambiental", "energetica"]
    },
    {
        "placeId": "researchExtensionM",
        "name": "Dirección de Investigación y Extensión Universitaria (Edificio M)",
        "category": CampusCategory.ADMINISTRATIVE,
        "parentBuildingId": "buildingM",
        "floorLevel": 1,
        "isAccessible": True,
        "latitude": 12.108331,
        "longitude": -86.257559,
        "locationNotes": "Edificio M, Piso 1, ala sur.",
        "keywords": ["direccion investigacion y extension universitaria", "investigacion", "extension universitaria"]
    },
    {
        "placeId": "drinkingFountainM1",
        "name": "Bebedero de Agua (Edificio M)",
        "category": CampusCategory.DRINKING_FOUNTAIN,
        "parentBuildingId": "buildingM",
        "floorLevel": 1,
        "isAccessible": True,
        "latitude": 12.108426,
        "longitude": -86.257560,
        "locationNotes": "Ground floor corridor near restrooms.",
        "keywords": ["bebedero m", "agua m"]
    },
    {
        "placeId": "classroomM201", "name": "Aula M-201", "category": CampusCategory.CLASSROOM,
        "parentBuildingId": "buildingM", "floorLevel": 2, "isAccessible": False,
        "latitude": 12.108402, "longitude": -86.257582,
        "locationNotes": "Edificio M, Piso 2, ala norte.", "keywords": ["m201", "m-201", "m 201", "aula m201"]
    },
    {
        "placeId": "classroomM202", "name": "Aula M-202", "category": CampusCategory.CLASSROOM,
        "parentBuildingId": "buildingM", "floorLevel": 2, "isAccessible": False,
        "latitude": 12.108402, "longitude": -86.257582,
        "locationNotes": "Edificio M, Piso 2, ala norte.", "keywords": ["m202", "m-202", "m 202", "aula m202"]
    },
    {
        "placeId": "classroomM203", "name": "Aula M-203", "category": CampusCategory.CLASSROOM,
        "parentBuildingId": "buildingM", "floorLevel": 2, "isAccessible": False,
        "latitude": 12.108437, "longitude": -86.257556,
        "locationNotes": "Edificio M, Piso 2, ala sur.", "keywords": ["m203", "m-203", "m 203", "aula m203"]
    },
    {
        "placeId": "classroomM204", "name": "Aula M-204", "category": CampusCategory.CLASSROOM,
        "parentBuildingId": "buildingM", "floorLevel": 2, "isAccessible": False,
        "latitude": 12.108437, "longitude": -86.257556,
        "locationNotes": "Edificio M, Piso 2, ala sur.", "keywords": ["m204", "m-204", "m 204", "aula m204"]
    },
    {
        "placeId": "classroomM301", "name": "Aula M-301", "category": CampusCategory.CLASSROOM,
        "parentBuildingId": "buildingM", "floorLevel": 3, "isAccessible": False,
        "latitude": 12.108493, "longitude": -86.257603,
        "locationNotes": "Edificio M, Piso 3, ala norte.", "keywords": ["m301", "m-301", "m 301", "aula m301"]
    },
    {
        "placeId": "classroomM302", "name": "Aula M-302", "category": CampusCategory.CLASSROOM,
        "parentBuildingId": "buildingM", "floorLevel": 3, "isAccessible": False,
        "latitude": 12.108493, "longitude": -86.257603,
        "locationNotes": "Edificio M, Piso 3, ala norte.", "keywords": ["m302", "m-302", "m 302", "aula m302"]
    },
    {
        "placeId": "classroomM303", "name": "Aula M-303", "category": CampusCategory.CLASSROOM,
        "parentBuildingId": "buildingM", "floorLevel": 3, "isAccessible": False,
        "latitude": 12.108450, "longitude": -86.257575,
        "locationNotes": "Edificio M, Piso 3, ala sur.", "keywords": ["m303", "m-303", "m 303", "aula m303"]
    },
    {
        "placeId": "classroomM304", "name": "Aula M-304", "category": CampusCategory.CLASSROOM,
        "parentBuildingId": "buildingM", "floorLevel": 3, "isAccessible": False,
        "latitude": 12.108450, "longitude": -86.257575,
        "locationNotes": "Edificio M, Piso 3, ala sur.", "keywords": ["m304", "m-304", "m 304", "aula m304"]
    },

    # -------------------------------------------------------------------------
    # BUILDING N: Dental Clinics (Gateway Point)
    # -------------------------------------------------------------------------
    {
        "placeId": "dentistryReceptionN",
        "name": "Recepción de Clínicas Odontológicas UAM",
        "category": CampusCategory.DENTAL_LAB,
        "parentBuildingId": "buildingN",
        "floorLevel": 1,
        "isAccessible": True,
        "locationNotes": "Main public entrance counter.",
        "keywords": ["clinicas odontologicas", "recepcion dental", "caja dental", "odontologia", "dientes"]
    },
    {
        "placeId": "facultyDentistryN",
        "name": "Facultad de Odontología (FODO)",
        "category": CampusCategory.FACULTY,
        "parentBuildingId": "buildingN",
        "floorLevel": 2,
        "isAccessible": False,
        "locationNotes": "Second floor deanery.",
        "keywords": ["fodo", "facultad de odontologia", "decanatura odonto"]
    },

    # -------------------------------------------------------------------------
    # BUILDING O: Engineering & Architecture (FIA) - Floors 1 & 2
    # -------------------------------------------------------------------------
    {
        "placeId": "facultyEngineeringO",
        "name": "Facultad de Ingeniería y Arquitectura (O-101)",
        "category": CampusCategory.FACULTY,
        "parentBuildingId": "buildingO",
        "floorLevel": 1,
        "isAccessible": True,
        "locationNotes": "Planta baja, Decanatura FIA.",
        "latitude": 12.107664,
        "longitude": -86.257761,
        "keywords": ["fia", "ingenieria", "arquitectura", "facultad de ingenieria", "decanatura fia", "o-101", "o101"]
    },
    {
        "placeId": "soilMechanicsLabO",
        "name": "Laboratorio de Mecánica de Suelos (O-102)",
        "category": CampusCategory.FACULTY,
        "parentBuildingId": "buildingO",
        "floorLevel": 1,
        "isAccessible": True,
        "locationNotes": "Planta baja, ala de laboratorios pesados.",
        "latitude": 12.107535,
        "longitude": -86.257643,
        "keywords": ["suelos", "mecanica de suelos", "laboratorio civil", "o-102", "o102"]
    },
    {
        "placeId": "exhibitionAreaO",
        "name": "Área de Exhibición (Edificio O)",
        "category": CampusCategory.FACULTY,
        "parentBuildingId": "buildingO",
        "floorLevel": 1,
        "isAccessible": True,
        "locationNotes": "Planta baja, área central de exhibición de proyectos.",
        "latitude": 12.107518,
        "longitude": -86.257615,
        "keywords": ["exhibicion", "area de exhibicion", "exposicion"]
    },
    {
        "placeId": "materialsLabO",
        "name": "Laboratorio de Resistencia de Materiales (O-104)",
        "category": CampusCategory.FACULTY,
        "parentBuildingId": "buildingO",
        "floorLevel": 1,
        "isAccessible": True,
        "locationNotes": "Planta baja, laboratorio de ensaye de materiales.",
        "latitude": 12.107502,
        "longitude": -86.257586,
        "keywords": ["materiales", "resistencia de materiales", "lab materiales", "o-104", "o104"]
    },
    {
        "placeId": "mixingAreaO",
        "name": "Área de Mezclado (Lab Materiales)",
        "category": CampusCategory.FACULTY,
        "parentBuildingId": "buildingO",
        "floorLevel": 1,
        "isAccessible": True,
        "locationNotes": "Planta baja, área anexa a materiales.",
        "latitude": 12.107490,
        "longitude": -86.257570,
        "keywords": ["mezclado", "area de mezclado"]
    },
    {
        "placeId": "curingAreaO",
        "name": "Área de Curado (Lab Materiales)",
        "category": CampusCategory.FACULTY,
        "parentBuildingId": "buildingO",
        "floorLevel": 1,
        "isAccessible": True,
        "locationNotes": "Planta baja, área de curado de probetas de concreto.",
        "latitude": 12.107485,
        "longitude": -86.257560,
        "keywords": ["curado", "area de curado", "curado de probetas"]
    },
    {
        "placeId": "labTechniciansO",
        "name": "Oficina de Técnicos de Laboratorio",
        "category": CampusCategory.ADMINISTRATIVE,
        "parentBuildingId": "buildingO",
        "floorLevel": 1,
        "isAccessible": True,
        "locationNotes": "Planta baja, oficina de soporte técnico de laboratorios.",
        "latitude": 12.107510,
        "longitude": -86.257575,
        "keywords": ["tecnicos", "tecnicos de lab", "oficina tecnicos"]
    },
    {
        "placeId": "fluidMechanicsLabO",
        "name": "Laboratorio de Mecánica de Fluidos",
        "category": CampusCategory.FACULTY,
        "parentBuildingId": "buildingO",
        "floorLevel": 1,
        "isAccessible": True,
        "locationNotes": "Planta baja, laboratorio hidráulica y fluidos.",
        "latitude": 12.107515,
        "longitude": -86.257550,
        "keywords": ["fluidos", "mecanica de fluidos", "lab fluidos"]
    },
    {
        "placeId": "disasterRiskCoordO",
        "name": "Coordinación de Gestión Integral de Riesgos de Desastres (O-105)",
        "category": CampusCategory.ADMINISTRATIVE,
        "parentBuildingId": "buildingO",
        "floorLevel": 1,
        "isAccessible": True,
        "locationNotes": "Planta baja, oficina de gestión de riesgos.",
        "latitude": 12.107545,
        "longitude": -86.257437,
        "keywords": ["riesgos", "gestion de riesgos", "desastres", "o-105", "o105"]
    },
    {
        "placeId": "mapUamO",
        "name": "Mapa UAM (Entrada Edificio O)",
        "category": CampusCategory.ADMINISTRATIVE,
        "parentBuildingId": "buildingO",
        "floorLevel": 1,
        "isAccessible": True,
        "locationNotes": "Entrada principal y directorio del Edificio O.",
        "latitude": 12.107478,
        "longitude": -86.257555,
        "keywords": ["mapa", "mapa uam", "directorio edificio o", "directorio"]
    },
    {
        "placeId": "restroomsMenO",
        "name": "Servicios Sanitarios Hombres (Anexo FIA)",
        "category": CampusCategory.RESTROOM,
        "parentBuildingId": "buildingO",
        "floorLevel": 1,
        "isAccessible": True,
        "locationNotes": "Anexo norte FIA.",
        "latitude": 12.108151,
        "longitude": -86.257888,
        "keywords": ["baños hombres", "banos hombres", "sanitarios hombres fia", "wc hombres"]
    },
    {
        "placeId": "restroomsWomenO",
        "name": "Servicios Sanitarios Mujeres (Anexo FIA)",
        "category": CampusCategory.RESTROOM,
        "parentBuildingId": "buildingO",
        "floorLevel": 1,
        "isAccessible": True,
        "locationNotes": "Anexo norte FIA.",
        "latitude": 12.108151,
        "longitude": -86.257888,
        "keywords": ["baños mujeres", "banos mujeres", "sanitarios mujeres fia", "wc mujeres"]
    },
    {
        "placeId": "teachersLoungeO",
        "name": "Sala de Maestros FIA (Anexo Norte)",
        "category": CampusCategory.FACULTY,
        "parentBuildingId": "buildingO",
        "floorLevel": 1,
        "isAccessible": True,
        "locationNotes": "Anexo norte FIA.",
        "latitude": 12.108229,
        "longitude": -86.257948,
        "keywords": ["sala de maestros", "maestros fia", "profesores fia", "anexo norte"]
    },
    {
        "placeId": "rampParkingO",
        "name": "Rampa Accesible del Edificio O al Parqueo",
        "category": CampusCategory.ACCESSIBLE_RAMP,
        "parentBuildingId": "buildingO",
        "floorLevel": 1,
        "isAccessible": True,
        "locationNotes": "Conexión accesible entre Edificio O y acera de estacionamiento.",
        "latitude": 12.107612,
        "longitude": -86.257442,
        "keywords": ["rampa", "rampa o", "rampa parqueo o", "rampa accesible fia"]
    },
    {
        "placeId": "networksLabO",
        "name": "Laboratorio de Redes (O-201)",
        "category": CampusCategory.CLASSROOM,
        "parentBuildingId": "buildingO",
        "floorLevel": 2,
        "isAccessible": False,
        "locationNotes": "Segundo piso, laboratorio de redes y conectividad.",
        "latitude": 12.107520,
        "longitude": -86.257586,
        "keywords": ["redes", "lab redes", "o-201", "o201"]
    },
    {
        "placeId": "networksCenterO",
        "name": "Centro de Redes (Edificio O)",
        "category": CampusCategory.ADMINISTRATIVE,
        "parentBuildingId": "buildingO",
        "floorLevel": 2,
        "isAccessible": False,
        "locationNotes": "Segundo piso, infraestructura de redes.",
        "latitude": 12.107550,
        "longitude": -86.257575,
        "keywords": ["centro de redes", "redes uam"]
    },
    {
        "placeId": "ciarLabO",
        "name": "Centro de Inteligencia Artificial y Robótica (CIAR)",
        "category": CampusCategory.FACULTY,
        "parentBuildingId": "buildingO",
        "floorLevel": 2,
        "isAccessible": False,
        "locationNotes": "Segundo piso, centro tecnológico de IA y Robótica.",
        "latitude": 12.107599,
        "longitude": -86.257561,
        "keywords": ["ciar", "inteligencia artificial", "centro de inteligencia artificial"]
    },
    {
        "placeId": "roboticsAreaO",
        "name": "Área de Robótica (CIAR)",
        "category": CampusCategory.FACULTY,
        "parentBuildingId": "buildingO",
        "floorLevel": 2,
        "isAccessible": False,
        "locationNotes": "Segundo piso, área de hardware y prototipado robótico.",
        "latitude": 12.107585,
        "longitude": -86.257567,
        "keywords": ["robotica", "lab robotica", "area de robotica"]
    },
    {
        "placeId": "drinkingFountainO_F2",
        "name": "Bebedero de Agua (Edificio O - Piso 2)",
        "category": CampusCategory.DRINKING_FOUNTAIN,
        "parentBuildingId": "buildingO",
        "floorLevel": 2,
        "isAccessible": False,
        "locationNotes": "Segundo piso, junto a robótica.",
        "latitude": 12.107585,
        "longitude": -86.257567,
        "keywords": ["bebedero", "bebedero o", "agua piso 2"]
    },
    {
        "placeId": "tutoringRoomO",
        "name": "Sala de Tutoría FIA",
        "category": CampusCategory.CLASSROOM,
        "parentBuildingId": "buildingO",
        "floorLevel": 2,
        "isAccessible": False,
        "locationNotes": "Segundo piso, asesorías académicas FIA.",
        "latitude": 12.107632,
        "longitude": -86.257548,
        "keywords": ["tutoria", "sala de tutoria", "tutorias fia"]
    },
    {
        "placeId": "classroomO202",
        "name": "Aula O-202",
        "category": CampusCategory.CLASSROOM,
        "parentBuildingId": "buildingO",
        "floorLevel": 2,
        "isAccessible": False,
        "locationNotes": "Segundo piso, aula teórica O-202.",
        "latitude": 12.107741,
        "longitude": -86.257507,
        "keywords": ["o-202", "o202", "aula o202"]
    },

    # -------------------------------------------------------------------------
    # BUILDING P: Copernicus Observatory, Classrooms & Indoor Facilities
    # -------------------------------------------------------------------------
    {
        "placeId": "copernicusObservatoryP",
        "name": "Observatorio Astronómico Copérnico",
        "category": CampusCategory.CLASSROOM,
        "parentBuildingId": "buildingP",
        "floorLevel": 5,
        "isAccessible": False,
        "latitude": 12.107461,
        "longitude": -86.256743,
        "locationNotes": "Fifth floor dome / rooftop.",
        "keywords": ["copernico", "observatorio", "telescopio", "estacion meteorologica", "piso 5", "p501"]
    },
    {
        "placeId": "classroomP401",
        "name": "Salón P-401 (Anexo Superior)",
        "category": CampusCategory.CLASSROOM,
        "parentBuildingId": "buildingP",
        "floorLevel": 4,
        "isAccessible": False,
        "latitude": 12.107461,
        "longitude": -86.256743,
        "locationNotes": "Edificio P, Piso 4 (Anexo Superior).",
        "keywords": ["p401", "p 401", "salon 401", "aula p401", "anexo p401"]
    },
    # --- Floor 1 ---
    {
        "placeId": "classroomP101", "name": "Salón P-101", "category": CampusCategory.CLASSROOM,
        "parentBuildingId": "buildingP", "floorLevel": 1, "isAccessible": True,
        "latitude": 12.107460, "longitude": -86.256743,
        "locationNotes": "Edificio P, Planta Baja, pasillo este.", "keywords": ["p101", "p 101", "salon 101", "aula p101"]
    },
    {
        "placeId": "drinkingFountainP1", "name": "Bebedero de Agua (Edificio P - Piso 1)", "category": CampusCategory.DRINKING_FOUNTAIN,
        "parentBuildingId": "buildingP", "floorLevel": 1, "isAccessible": True,
        "latitude": 12.107460, "longitude": -86.256743,
        "locationNotes": "Edificio P, Planta Baja, junto a Salón P-101.", "keywords": ["bebedero p", "bebedero p1", "agua p1"]
    },
    {
        "placeId": "classroomP102", "name": "Salón P-102", "category": CampusCategory.CLASSROOM,
        "parentBuildingId": "buildingP", "floorLevel": 1, "isAccessible": True,
        "latitude": 12.107431, "longitude": -86.256783,
        "locationNotes": "Edificio P, Planta Baja.", "keywords": ["p102", "p 102", "salon 102", "aula p102"]
    },
    {
        "placeId": "classroomP103", "name": "Salón P-103", "category": CampusCategory.CLASSROOM,
        "parentBuildingId": "buildingP", "floorLevel": 1, "isAccessible": True,
        "latitude": 12.107439, "longitude": -86.256947,
        "locationNotes": "Edificio P, Planta Baja.", "keywords": ["p103", "p 103", "salon 103", "aula p103"]
    },
    {
        "placeId": "classroomP104", "name": "Salón P-104", "category": CampusCategory.CLASSROOM,
        "parentBuildingId": "buildingP", "floorLevel": 1, "isAccessible": True,
        "latitude": 12.107455, "longitude": -86.256981,
        "locationNotes": "Edificio P, Planta Baja.", "keywords": ["p104", "p 104", "salon 104", "aula p104"]
    },
    {
        "placeId": "classroomP105", "name": "Salón P-105", "category": CampusCategory.CLASSROOM,
        "parentBuildingId": "buildingP", "floorLevel": 1, "isAccessible": True,
        "latitude": 12.107453, "longitude": -86.257149,
        "locationNotes": "Edificio P, Planta Baja central.", "keywords": ["p105", "p 105", "salon 105", "aula p105"]
    },
    {
        "placeId": "classroomP106", "name": "Salón P-106", "category": CampusCategory.CLASSROOM,
        "parentBuildingId": "buildingP", "floorLevel": 1, "isAccessible": True,
        "latitude": 12.107467, "longitude": -86.257202,
        "locationNotes": "Edificio P, Planta Baja.", "keywords": ["p106", "p 106", "salon 106", "aula p106"]
    },
    {
        "placeId": "classroomP107", "name": "Salón P-107", "category": CampusCategory.CLASSROOM,
        "parentBuildingId": "buildingP", "floorLevel": 1, "isAccessible": True,
        "latitude": 12.107450, "longitude": -86.257270,
        "locationNotes": "Edificio P, Planta Baja.", "keywords": ["p107", "p 107", "salon 107", "aula p107"]
    },
    {
        "placeId": "classroomP108", "name": "Salón P-108", "category": CampusCategory.CLASSROOM,
        "parentBuildingId": "buildingP", "floorLevel": 1, "isAccessible": True,
        "latitude": 12.107477, "longitude": -86.257206,
        "locationNotes": "Edificio P, Planta Baja oeste.", "keywords": ["p108", "p 108", "salon 108", "aula p108"]
    },
    {
        "placeId": "restroomsP1", "name": "Servicios Sanitarios (Edificio P - Piso 1)", "category": CampusCategory.RESTROOM,
        "parentBuildingId": "buildingP", "floorLevel": 1, "isAccessible": True,
        "latitude": 12.107441, "longitude": -86.257422,
        "locationNotes": "Edificio P, Planta Baja, extremo oeste.", "keywords": ["baños p", "baño p", "baños p1", "sanitarios p1"]
    },
    {
        "placeId": "rampParkingP", "name": "Rampa Accesible Estacionamiento hacia Edificio P", "category": CampusCategory.ACCESSIBLE_RAMP,
        "parentBuildingId": "buildingP", "floorLevel": 1, "isAccessible": True,
        "latitude": 12.106991, "longitude": -86.258233,
        "locationNotes": "Rampa desde el estacionamiento hacia el Edificio P, enfrente del Edificio O.", "keywords": ["rampa p", "rampa edificio p", "rampa estacionamiento p"]
    },
    # --- Floor 2 ---
    {
        "placeId": "classroomP201", "name": "Salón P-201", "category": CampusCategory.CLASSROOM,
        "parentBuildingId": "buildingP", "floorLevel": 2, "isAccessible": False,
        "latitude": 12.107484, "longitude": -86.256721,
        "locationNotes": "Edificio P, Piso 2 este.", "keywords": ["p201", "p 201", "salon 201", "aula p201"]
    },
    {
        "placeId": "drinkingFountainP2East", "name": "2do Bebedero de Agua (Edificio P - Piso 2 Este)", "category": CampusCategory.DRINKING_FOUNTAIN,
        "parentBuildingId": "buildingP", "floorLevel": 2, "isAccessible": False,
        "latitude": 12.107434, "longitude": -86.256781,
        "locationNotes": "Edificio P, Piso 2, pasillo este.", "keywords": ["bebedero p2", "agua p2", "bebedero p2 este"]
    },
    {
        "placeId": "classroomP202", "name": "Salón P-202", "category": CampusCategory.CLASSROOM,
        "parentBuildingId": "buildingP", "floorLevel": 2, "isAccessible": False,
        "latitude": 12.107428, "longitude": -86.256817,
        "locationNotes": "Edificio P, Piso 2.", "keywords": ["p202", "p 202", "salon 202", "aula p202"]
    },
    {
        "placeId": "classroomP203", "name": "Salón P-203", "category": CampusCategory.CLASSROOM,
        "parentBuildingId": "buildingP", "floorLevel": 2, "isAccessible": False,
        "latitude": 12.107447, "longitude": -86.256957,
        "locationNotes": "Edificio P, Piso 2.", "keywords": ["p203", "p 203", "salon 203", "aula p203"]
    },
    {
        "placeId": "classroomP204", "name": "Salón P-204", "category": CampusCategory.CLASSROOM,
        "parentBuildingId": "buildingP", "floorLevel": 2, "isAccessible": False,
        "latitude": 12.107434, "longitude": -86.257043,
        "locationNotes": "Edificio P, Piso 2 central.", "keywords": ["p204", "p 204", "salon 204", "aula p204"]
    },
    {
        "placeId": "classroomP205", "name": "Salón P-205", "category": CampusCategory.CLASSROOM,
        "parentBuildingId": "buildingP", "floorLevel": 2, "isAccessible": False,
        "latitude": 12.107492, "longitude": -86.257090,
        "locationNotes": "Edificio P, Piso 2 central.", "keywords": ["p205", "p 205", "salon 205", "aula p205"]
    },
    {
        "placeId": "classroomP206", "name": "Salón P-206", "category": CampusCategory.CLASSROOM,
        "parentBuildingId": "buildingP", "floorLevel": 2, "isAccessible": False,
        "latitude": 12.107413, "longitude": -86.257153,
        "locationNotes": "Edificio P, Piso 2.", "keywords": ["p206", "p 206", "salon 206", "aula p206"]
    },
    {
        "placeId": "classroomP207", "name": "Salón P-207", "category": CampusCategory.CLASSROOM,
        "parentBuildingId": "buildingP", "floorLevel": 2, "isAccessible": False,
        "latitude": 12.107427, "longitude": -86.257217,
        "locationNotes": "Edificio P, Piso 2.", "keywords": ["p207", "p 207", "salon 207", "aula p207"]
    },
    {
        "placeId": "classroomP208", "name": "Salón P-208", "category": CampusCategory.CLASSROOM,
        "parentBuildingId": "buildingP", "floorLevel": 2, "isAccessible": False,
        "latitude": 12.107402, "longitude": -86.257297,
        "locationNotes": "Edificio P, Piso 2 oeste.", "keywords": ["p208", "p 208", "salon 208", "aula p208"]
    },
    {
        "placeId": "drinkingFountainP2West", "name": "Bebedero de Agua (Edificio P - Piso 2 Oeste)", "category": CampusCategory.DRINKING_FOUNTAIN,
        "parentBuildingId": "buildingP", "floorLevel": 2, "isAccessible": False,
        "latitude": 12.107407, "longitude": -86.257298,
        "locationNotes": "Edificio P, Piso 2 junto a Salón P-208.", "keywords": ["bebedero p2 oeste", "bebedero p2"]
    },
    {
        "placeId": "restroomsP2", "name": "Servicios Sanitarios (Edificio P - Piso 2)", "category": CampusCategory.RESTROOM,
        "parentBuildingId": "buildingP", "floorLevel": 2, "isAccessible": False,
        "latitude": 12.107480, "longitude": -86.257337,
        "locationNotes": "Edificio P, Piso 2 oeste.", "keywords": ["baños p2", "sanitarios p2"]
    },
    # --- Floor 3 ---
    {
        "placeId": "classroomP301", "name": "Salón P-301", "category": CampusCategory.CLASSROOM,
        "parentBuildingId": "buildingP", "floorLevel": 3, "isAccessible": False,
        "latitude": 12.107461, "longitude": -86.256717,
        "locationNotes": "Edificio P, Piso 3 este.", "keywords": ["p301", "p 301", "salon 301", "aula p301"]
    },
    {
        "placeId": "drinkingFountainP3", "name": "1er Bebedero de Agua (Edificio P - Piso 3)", "category": CampusCategory.DRINKING_FOUNTAIN,
        "parentBuildingId": "buildingP", "floorLevel": 3, "isAccessible": False,
        "latitude": 12.107434, "longitude": -86.256751,
        "locationNotes": "Edificio P, Piso 3 este.", "keywords": ["bebedero p3", "agua p3"]
    },
    {
        "placeId": "classroomP301B", "name": "Salón P-301 (Acceso 2)", "category": CampusCategory.CLASSROOM,
        "parentBuildingId": "buildingP", "floorLevel": 3, "isAccessible": False,
        "latitude": 12.107462, "longitude": -86.256862,
        "locationNotes": "Edificio P, Piso 3.", "keywords": ["p301b", "p 301 2", "p301 segundo"]
    },
    {
        "placeId": "classroomP302", "name": "Salón P-302", "category": CampusCategory.CLASSROOM,
        "parentBuildingId": "buildingP", "floorLevel": 3, "isAccessible": False,
        "latitude": 12.107443, "longitude": -86.256934,
        "locationNotes": "Edificio P, Piso 3.", "keywords": ["p302", "p 302", "salon 302", "aula p302"]
    },
    {
        "placeId": "classroomP303", "name": "Salón P-303", "category": CampusCategory.CLASSROOM,
        "parentBuildingId": "buildingP", "floorLevel": 3, "isAccessible": False,
        "latitude": 12.107442, "longitude": -86.256936,
        "locationNotes": "Edificio P, Piso 3.", "keywords": ["p303", "p 303", "salon 303", "aula p303"]
    },
    {
        "placeId": "classroomP304", "name": "Salón P-304", "category": CampusCategory.CLASSROOM,
        "parentBuildingId": "buildingP", "floorLevel": 3, "isAccessible": False,
        "latitude": 12.107443, "longitude": -86.256999,
        "locationNotes": "Edificio P, Piso 3.", "keywords": ["p304", "p 304", "salon 304", "aula p304"]
    },
    {
        "placeId": "classroomP305", "name": "Salón P-305", "category": CampusCategory.CLASSROOM,
        "parentBuildingId": "buildingP", "floorLevel": 3, "isAccessible": False,
        "latitude": 12.107454, "longitude": -86.257114,
        "locationNotes": "Edificio P, Piso 3 central.", "keywords": ["p305", "p 305", "salon 305", "aula p305"]
    },
    {
        "placeId": "classroomP306", "name": "Salón P-306", "category": CampusCategory.CLASSROOM,
        "parentBuildingId": "buildingP", "floorLevel": 3, "isAccessible": False,
        "latitude": 12.107461, "longitude": -86.257145,
        "locationNotes": "Edificio P, Piso 3.", "keywords": ["p306", "p 306", "salon 306", "aula p306"]
    },
    {
        "placeId": "classroomP306B", "name": "Salón P-306 (Acceso 2)", "category": CampusCategory.CLASSROOM,
        "parentBuildingId": "buildingP", "floorLevel": 3, "isAccessible": False,
        "latitude": 12.107435, "longitude": -86.257136,
        "locationNotes": "Edificio P, Piso 3.", "keywords": ["p306b", "p 306 2", "p306 segundo"]
    },
    {
        "placeId": "classroomP307", "name": "Salón P-307", "category": CampusCategory.CLASSROOM,
        "parentBuildingId": "buildingP", "floorLevel": 3, "isAccessible": False,
        "latitude": 12.107461, "longitude": -86.257145,
        "locationNotes": "Edificio P, Piso 3 oeste.", "keywords": ["p307", "p-307", "p 307", "salon 307", "aula p307"]
    },
    {
        "placeId": "classroomP308", "name": "Salón P-308", "category": CampusCategory.CLASSROOM,
        "parentBuildingId": "buildingP", "floorLevel": 3, "isAccessible": False,
        "latitude": 12.107435, "longitude": -86.257136,
        "locationNotes": "Edificio P, Piso 3 oeste.", "keywords": ["p308", "p-308", "p 308", "salon 308", "aula p308"]
    },
    {
        "placeId": "weatherStationP", "name": "Estación de Meteorología (Edificio P)", "category": CampusCategory.CLASSROOM,
        "parentBuildingId": "buildingP", "floorLevel": 1, "isAccessible": True,
        "latitude": 12.107470, "longitude": -86.256753,
        "locationNotes": "Edificio P, Planta Baja, acceso este.", "keywords": ["estacion de meteorologia", "meteorologia", "clima"]
    },
    {
        "placeId": "restroomsP3", "name": "Servicios Sanitarios (Edificio P - Piso 3)", "category": CampusCategory.RESTROOM,
        "parentBuildingId": "buildingP", "floorLevel": 3, "isAccessible": False,
        "latitude": 12.107468, "longitude": -86.257189,
        "locationNotes": "Edificio P, Piso 3 oeste.", "keywords": ["baños p3", "sanitarios p3", "baño p3"]
    },

    # -------------------------------------------------------------------------
    # SPORTS COMPLEX & RECREATIONAL AREAS
    # -------------------------------------------------------------------------
    {
        "placeId": "jaguarGym",
        "name": "Gimnasio JAGUAR GYM",
        "category": CampusCategory.SPORTS,
        "parentBuildingId": "jaguarGym",
        "floorLevel": 1,
        "isAccessible": True,
        "locationNotes": "Jaguar Gym building, southeast of Jaguar Center.",
        "keywords": ["gimnasio", "gym", "pesas", "jaguar gym", "entrenar"]
    },
    {
        "placeId": "physiotherapyClinic",
        "name": "Fisioterapia / Physiotherapy",
        "category": CampusCategory.MEDICAL_LAB,
        "parentBuildingId": "physiotherapy",
        "floorLevel": 1,
        "isAccessible": True,
        "locationNotes": "Physiotherapy building, north of Jaguar Gym.",
        "keywords": ["fisioterapia", "physiotherapy", "fisio", "terapia fisica", "rehabilitacion", "clinica fisioterapia"]
    },
    {
        "placeId": "baseballStadium",
        "name": "Estadio de Béisbol (Jaguar Stadium)",
        "category": CampusCategory.SPORTS,
        "parentBuildingId": "sportsZone",
        "floorLevel": 1,
        "isAccessible": True,
        "locationNotes": "Northeast sports complex.",
        "keywords": ["estadio", "beisbol", "jaguar stadium", "campo beisbol"]
    },
    {
        "placeId": "soccerField",
        "name": "Cancha de Fútbol Campo UAM",
        "category": CampusCategory.SPORTS,
        "parentBuildingId": "sportsZone",
        "floorLevel": 1,
        "isAccessible": True,
        "locationNotes": "Northeast sports complex.",
        "keywords": ["cancha futbol", "futbol", "soccer", "partido"]
    },
    {
        "placeId": "multipurposeCourtJC",
        "name": "Cancha Multi-Usos y Volleyball Arena (Jaguar Center)",
        "category": CampusCategory.SPORTS,
        "parentBuildingId": "jaguarCenter",
        "floorLevel": 1,
        "isAccessible": True,
        "latitude": 12.109279,
        "longitude": -86.258881,
        "locationNotes": "Complejo Deportivo Jaguar Center.",
        "keywords": ["cancha multi usos", "cancha multiusos", "cancha de volleyball arena", "volleyball arena", "kiosko jaguar sport"]
    },
    {
        "placeId": "generalWarehouseSZ",
        "name": "Bodega General y Comedor de Colaboradores",
        "category": CampusCategory.ADMINISTRATIVE,
        "parentBuildingId": "sportsZone",
        "floorLevel": 1,
        "isAccessible": True,
        "latitude": 12.108164,
        "longitude": -86.258313,
        "locationNotes": "Zona de bodega general, contenedores, oficinas deportivas 1-3 y comedor de colaboradores.",
        "keywords": ["bodega general", "bodega general y contenedores", "oficinas deportivas", "oficinas de deportes", "comedor de colaboradores"]
    },
    {
        "placeId": "chilamatesDining",
        "name": "Plaza Chilamates (Kioskos & Fast Point)",
        "category": CampusCategory.FOOD_AREA,
        "parentBuildingId": "chilamatesPlaza",
        "floorLevel": 1,
        "isAccessible": True,
        "locationNotes": "Outdoor central plaza.",
        "keywords": ["chilamates", "fast point", "kiosko chilamates", "almuerzo aire libre"]
    },
    {
        "placeId": "jaguarJungleGarden",
        "name": "Jaguar Jungle (Jardín & Senderos Centrales)",
        "category": CampusCategory.FOOD_AREA,
        "parentBuildingId": "jaguarJungle",
        "floorLevel": 1,
        "isAccessible": True,
        "locationNotes": "Shaded green garden area with walkways connecting Building O, Mi Ranchito, Building H, and the main internal road.",
        "keywords": ["jaguar jungle", "jungle", "jungla", "jardin jaguar", "area verde", "sendero o h"]
    },
    {
        "placeId": "miRanchitoPavilion",
        "name": "Mi Ranchito (Ranchón Universitario)",
        "category": CampusCategory.FOOD_AREA,
        "parentBuildingId": "miRanchito",
        "floorLevel": 1,
        "isAccessible": True,
        "locationNotes": "Open-air rest and dining pavilion beside Jaguar Jungle, Building N, and Lab Digital FIA.",
        "keywords": ["mi ranchito", "ranchito", "ranchon", "ranch", "kiosko ranchon", "descanso"]
    },
    {
        "placeId": "labDigitalFiaRoom",
        "name": "Lab Digital FIA (Laboratorio Digital de Ingeniería)",
        "category": CampusCategory.FACULTY,
        "parentBuildingId": "labDigitalFia",
        "floorLevel": 1,
        "isAccessible": True,
        "locationNotes": "FIA Digital Laboratory located beside Building N, near Mi Ranchito and Área de Mesas.",
        "keywords": ["lab digital fia", "laboratorio digital fia", "lab fia", "digital fia", "digital laboratory fia"]
    },
    {
        "placeId": "areaDeMesasTerrace",
        "name": "Área de Mesas (Terraza Exterior de Estudio)",
        "category": CampusCategory.FOOD_AREA,
        "parentBuildingId": "areaDeMesas",
        "floorLevel": 1,
        "isAccessible": True,
        "locationNotes": "Shaded outdoor tables and study terrace between Lab Digital FIA, Central Parking, and Building C.",
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
        "locationNotes": "Main southern vehicle and pedestrian gate.",
        "keywords": ["parqueo principal", "estacionamiento", "caseta sur", "entrada principal", "porton sur"]
    },
    {
        "placeId": "thirdAccessRoad",
        "name": "Tercer Acceso / Third Access (Portón Copérnico)",
        "category": CampusCategory.PARKING_LOT,
        "parentBuildingId": "northGate",
        "floorLevel": 1,
        "isAccessible": True,
        "locationNotes": "Northwest vehicle & pedestrian access gate beside Weather Station and Building P (Copernicus).",
        "keywords": ["tercer acceso", "third access", "third access road", "acceso 3", "3er acceso", "entrada 3", "porton norte", "caseta norte", "acceso copernico"]
    },
    {
        "placeId": "secondAccessRoad",
        "name": "Segundo Acceso / Camino Estadio Jaguar (Second Access Road)",
        "category": CampusCategory.PARKING_LOT,
        "parentBuildingId": "northeastGate",
        "floorLevel": 1,
        "isAccessible": True,
        "locationNotes": "Northern vehicle & pedestrian road past Jaguar Baseball Stadium connecting Sports Parking and Building O.",
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
        "locationNotes": "Main entrance ramp with gentle slope.",
        "keywords": ["rampa a", "rampa edificio a", "acceso silla de ruedas a"]
    },
    {
        "placeId": "rampBuildingB",
        "name": "Rampa de Acceso Edificio B",
        "category": CampusCategory.ACCESSIBLE_RAMP,
        "parentBuildingId": "buildingB",
        "floorLevel": 1,
        "isAccessible": True,
        "locationNotes": "Western hallway entrance ramp.",
        "keywords": ["rampa b", "rampa edificio b", "acceso inclusivo b"]
    },
    {
        "placeId": "rampBuildingG",
        "name": "Rampa Auditorio Central Edificio G",
        "category": CampusCategory.ACCESSIBLE_RAMP,
        "parentBuildingId": "buildingG",
        "floorLevel": 1,
        "isAccessible": True,
        "locationNotes": "Direct access ramp to Building G ground lobby.",
        "keywords": ["rampa g", "rampa auditorio"]
    },
    {
        "placeId": "rampJaguarCenter",
        "name": "Rampa de Acceso Jaguar Center",
        "category": CampusCategory.ACCESSIBLE_RAMP,
        "parentBuildingId": "jaguarCenter",
        "floorLevel": 1,
        "isAccessible": True,
        "locationNotes": "Main entrance sports center ramp.",
        "keywords": ["rampa jaguar center", "rampa gimnasio"]
    }
]

def getPlacesByCategory(category: str):
    """Filters places by their specific CampusCategory string."""
    return [place for place in PLACES_CATALOG if place["category"] == category]

def getPlacesByBuilding(buildingId: str):
    """Retrieves all classrooms, labs or services located inside a specific building."""
    return [place for place in PLACES_CATALOG if place["parentBuildingId"] == buildingId]
