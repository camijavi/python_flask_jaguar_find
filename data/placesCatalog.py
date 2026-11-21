"""
placesCatalog.py
================================================================================
Comprehensive catalog of all campus rooms, labs, faculties, food areas, 
drinking fountains, restrooms, and parking spaces extracted from buildings.txt.
Linked hierarchically to parent buildings with floor level and accessibility.
================================================================================
"""

from data.campusCategories import CampusCategory

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
        "locationNotes": "Outside Building A, western facade.",
        "keywords": ["cajero", "atm", "bac", "lafise", "dinero", "efectivo"]
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
        "locationNotes": "Ground floor corridor, left side.", "keywords": ["b101", "b 101", "aula b101"]
    },
    {
        "placeId": "classroomB102", "name": "Aula B-102", "category": CampusCategory.CLASSROOM,
        "parentBuildingId": "buildingB", "floorLevel": 1, "isAccessible": True,
        "locationNotes": "Ground floor corridor, left side.", "keywords": ["b102", "b 102", "aula b102"]
    },
    {
        "placeId": "classroomB103", "name": "Aula B-103", "category": CampusCategory.CLASSROOM,
        "parentBuildingId": "buildingB", "floorLevel": 1, "isAccessible": True,
        "locationNotes": "Ground floor corridor, central area.", "keywords": ["b103", "b 103", "aula b103"]
    },
    {
        "placeId": "classroomB104", "name": "Aula B-104", "category": CampusCategory.CLASSROOM,
        "parentBuildingId": "buildingB", "floorLevel": 1, "isAccessible": True,
        "locationNotes": "Ground floor corridor.", "keywords": ["b104", "b 104", "aula b104"]
    },
    {
        "placeId": "classroomB105", "name": "Aula B-105", "category": CampusCategory.CLASSROOM,
        "parentBuildingId": "buildingB", "floorLevel": 1, "isAccessible": True,
        "locationNotes": "Ground floor corridor.", "keywords": ["b105", "b 105", "aula b105"]
    },
    {
        "placeId": "classroomB106", "name": "Aula B-106", "category": CampusCategory.CLASSROOM,
        "parentBuildingId": "buildingB", "floorLevel": 1, "isAccessible": True,
        "locationNotes": "Ground floor corridor, right side.", "keywords": ["b106", "b 106", "aula b106"]
    },
    {
        "placeId": "classroomB107", "name": "Aula B-107", "category": CampusCategory.CLASSROOM,
        "parentBuildingId": "buildingB", "floorLevel": 1, "isAccessible": True,
        "locationNotes": "Ground floor corridor.", "keywords": ["b107", "b 107"]
    },
    {
        "placeId": "classroomB108", "name": "Aula B-108", "category": CampusCategory.CLASSROOM,
        "parentBuildingId": "buildingB", "floorLevel": 1, "isAccessible": True,
        "locationNotes": "Ground floor corridor.", "keywords": ["b108", "b 108"]
    },
    {
        "placeId": "classroomB109", "name": "Aula B-109", "category": CampusCategory.CLASSROOM,
        "parentBuildingId": "buildingB", "floorLevel": 1, "isAccessible": True,
        "locationNotes": "Ground floor corridor end.", "keywords": ["b109", "b 109"]
    },
    {
        "placeId": "drinkingFountainB1",
        "name": "Bebedero de Agua (Edificio B)",
        "category": CampusCategory.DRINKING_FOUNTAIN,
        "parentBuildingId": "buildingB",
        "floorLevel": 1,
        "isAccessible": True,
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
        "locationNotes": "End of ground floor hallway.",
        "keywords": ["fotocopias", "impresiones", "copias", "jaguar shop b"]
    },
    # Building B Second Floor
    {
        "placeId": "classroomB201", "name": "Aula B-201", "category": CampusCategory.CLASSROOM,
        "parentBuildingId": "buildingB", "floorLevel": 2, "isAccessible": False,
        "locationNotes": "Second floor corridor, left side.", "keywords": ["b201", "b 201"]
    },
    {
        "placeId": "classroomB202", "name": "Aula B-202", "category": CampusCategory.CLASSROOM,
        "parentBuildingId": "buildingB", "floorLevel": 2, "isAccessible": False,
        "locationNotes": "Second floor corridor.", "keywords": ["b202", "b 202"]
    },
    {
        "placeId": "classroomB203", "name": "Aula B-203", "category": CampusCategory.CLASSROOM,
        "parentBuildingId": "buildingB", "floorLevel": 2, "isAccessible": False,
        "locationNotes": "Second floor corridor.", "keywords": ["b203", "b 203"]
    },
    {
        "placeId": "classroomB204", "name": "Aula B-204", "category": CampusCategory.CLASSROOM,
        "parentBuildingId": "buildingB", "floorLevel": 2, "isAccessible": False,
        "locationNotes": "Second floor corridor.", "keywords": ["b204", "b 204"]
    },
    {
        "placeId": "classroomB205", "name": "Aula B-205", "category": CampusCategory.CLASSROOM,
        "parentBuildingId": "buildingB", "floorLevel": 2, "isAccessible": False,
        "locationNotes": "Second floor corridor.", "keywords": ["b205", "b 205"]
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
    # BUILDING C: Computer Labs, Cashier & Classrooms
    # -------------------------------------------------------------------------
    {
        "placeId": "auditoriumC101",
        "name": "Auditorio C-101",
        "category": CampusCategory.AUDITORIUM,
        "parentBuildingId": "buildingC",
        "floorLevel": 1,
        "isAccessible": True,
        "locationNotes": "Ground floor near main entrance.",
        "keywords": ["auditorio c101", "auditorio c", "c101"]
    },
    {
        "placeId": "cashierUamC",
        "name": "Caja Central UAM / Tesorería",
        "category": CampusCategory.ADMINISTRATIVE,
        "parentBuildingId": "buildingC",
        "floorLevel": 1,
        "isAccessible": True,
        "locationNotes": "Ground floor central lobby.",
        "keywords": ["caja", "tesoreria", "pagar", "aranceles", "colegiatura", "cashier"]
    },
    {
        "placeId": "macLabC107",
        "name": "Laboratorio MAC (C-107)",
        "category": CampusCategory.CLASSROOM,
        "parentBuildingId": "buildingC",
        "floorLevel": 1,
        "isAccessible": True,
        "locationNotes": "Ground floor computer labs wing.",
        "keywords": ["mac 107", "lab mac", "computadoras apple", "c107"]
    },
    {
        "placeId": "erasmusLabC108",
        "name": "Laboratorio Acai-Erasmus+ (C-108)",
        "category": CampusCategory.CLASSROOM,
        "parentBuildingId": "buildingC",
        "floorLevel": 1,
        "isAccessible": True,
        "locationNotes": "Ground floor computer labs wing.",
        "keywords": ["erasmus", "acai", "c108", "lab computacion"]
    },
    {
        "placeId": "macLabC203",
        "name": "Laboratorio MAC (C-203)",
        "category": CampusCategory.CLASSROOM,
        "parentBuildingId": "buildingC",
        "floorLevel": 2,
        "isAccessible": False,
        "locationNotes": "Second floor lab wing.",
        "keywords": ["mac 203", "lab mac 2", "c203"]
    },
    {
        "placeId": "computerLabC201",
        "name": "Laboratorio de Cómputo (C-201)",
        "category": CampusCategory.CLASSROOM,
        "parentBuildingId": "buildingC",
        "floorLevel": 2,
        "isAccessible": False,
        "locationNotes": "Second floor.",
        "keywords": ["c201", "lab computo"]
    },
    {
        "placeId": "drinkingFountainC1",
        "name": "Bebedero de Agua (Edificio C)",
        "category": CampusCategory.DRINKING_FOUNTAIN,
        "parentBuildingId": "buildingC",
        "floorLevel": 1,
        "isAccessible": True,
        "locationNotes": "Ground floor next to cashier.",
        "keywords": ["bebedero c", "agua c", "bebedero caja"]
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
        "locationNotes": "Second floor medical skills ward.",
        "keywords": ["simuladores", "simuladores medicina", "lab habilidades"]
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
        "locationNotes": "Ground floor.",
        "keywords": ["posgrados", "maestrias", "educacion continua"]
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
        "name": "Servicios Sanitarios Mixtos Inclusivos",
        "category": CampusCategory.RESTROOM,
        "parentBuildingId": "buildingG",
        "floorLevel": 1,
        "isAccessible": True,
        "locationNotes": "First floor near entrance.",
        "keywords": ["bano accesible g", "bano silla de ruedas g"]
    },

    # -------------------------------------------------------------------------
    # BUILDING H: Medical Laboratories
    # -------------------------------------------------------------------------
    {
        "placeId": "medicalLabH101", "name": "Laboratorio de Medicina H-101",
        "category": CampusCategory.MEDICAL_LAB, "parentBuildingId": "buildingH", "floorLevel": 1,
        "isAccessible": True, "locationNotes": "Ground floor.", "keywords": ["h101", "lab med h101"]
    },
    {
        "placeId": "medicalLabH102", "name": "Laboratorio de Medicina H-102",
        "category": CampusCategory.MEDICAL_LAB, "parentBuildingId": "buildingH", "floorLevel": 1,
        "isAccessible": True, "locationNotes": "Ground floor.", "keywords": ["h102", "lab med h102"]
    },
    {
        "placeId": "medicalLabH201", "name": "Laboratorio de Medicina H-201",
        "category": CampusCategory.MEDICAL_LAB, "parentBuildingId": "buildingH", "floorLevel": 2,
        "isAccessible": False, "locationNotes": "Second floor.", "keywords": ["h201", "lab med h201"]
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
    # BUILDING M: Graduate Studies & Classrooms
    # -------------------------------------------------------------------------
    {
        "placeId": "auditoriumM101",
        "name": "Auditorio M-101",
        "category": CampusCategory.AUDITORIUM,
        "parentBuildingId": "buildingM",
        "floorLevel": 1,
        "isAccessible": True,
        "locationNotes": "Ground floor.",
        "keywords": ["m101", "auditorio m101"]
    },
    {
        "placeId": "drinkingFountainM1",
        "name": "Bebedero de Agua (Edificio M)",
        "category": CampusCategory.DRINKING_FOUNTAIN,
        "parentBuildingId": "buildingM",
        "floorLevel": 1,
        "isAccessible": True,
        "locationNotes": "Ground floor corridor near restrooms.",
        "keywords": ["bebedero m", "agua m"]
    },
    {
        "placeId": "classroomM201", "name": "Aula M-201", "category": CampusCategory.CLASSROOM,
        "parentBuildingId": "buildingM", "floorLevel": 2, "isAccessible": False,
        "locationNotes": "Second floor.", "keywords": ["m201", "aula m"]
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
        "locationNotes": "Fifth floor dome / rooftop.",
        "keywords": ["copernico", "observatorio", "telescopio", "estacion meteorologica", "piso 5"]
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
        "parentBuildingId": "jaguarCenter",
        "floorLevel": 1,
        "isAccessible": True,
        "locationNotes": "Jaguar Center ground level.",
        "keywords": ["gimnasio", "gym", "pesas", "jaguar gym", "entrenar"]
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
        "placeId": "chilamatesDining",
        "name": "Plaza Chilamates (Kioskos & Fast Point)",
        "category": CampusCategory.FOOD_AREA,
        "parentBuildingId": "chilamatesPlaza",
        "floorLevel": 1,
        "isAccessible": True,
        "locationNotes": "Outdoor central plaza.",
        "keywords": ["chilamates", "fast point", "kiosko chilamates", "almuerzo aire libre"]
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
