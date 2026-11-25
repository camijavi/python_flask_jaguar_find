"""
campusLocalization.py
================================================================================
AUTHORITATIVE BILINGUAL (EN / ES) LOCALIZATION FOR CAMPUS PLACES & SUBGRAPHS
================================================================================
Provides complete, idiomatic English and Spanish translations for:
  1. All entries in PLACES_CATALOG (display names + location notes)
  2. All indoor nodes across the 18 BuildingSubgraph child graphs
  3. All 18 BuildingSubgraph names and descriptions

Used by placeSearchService.py, navigationService.py, gpsMatcher.py,
buildingSubgraph.py, and mapController.py so that switching the UI language
between Spanish ('spa') and English ('eng') dynamically localizes every
autocomplete option, selected input label, GPS room picker, building detail,
and turn-by-turn indoor/outdoor navigation step while keeping bilingual search
fully functional in both languages.
================================================================================
"""

from typing import Dict, List, Optional, Tuple
from backend.i18n import normalize_language


# =============================================================================
# 1. BUILDING SUBGRAPH METADATA TRANSLATIONS (18 BUILDINGS / ZONES)
# =============================================================================
SUBGRAPH_TRANSLATIONS: Dict[str, Dict[str, str]] = {
    "buildingA": {
        "name_spa": "Edificio A (Atención al Estudiante, Administración & DPA)",
        "name_eng": "Building A (Student Services, Administration & DPA)",
        "desc_spa": "Edificio A: Contabilidad (A101), CAE, Admisión, Registro Académico, Cartera y Cobro, Finanzas, Objetos Perdidos, Cajeros, TIC (A203), RRHH (A205) y DPA (A301).",
        "desc_eng": "Building A: Accounting (A101), CAE, Admissions, Academic Records, Collections, Finance, Lost & Found, ATMs, IT/TIC (A203), HR (A205), and DPA (A301).",
    },
    "buildingB": {
        "name_spa": "Edificio B (Aulas B101-B210 & Farmacia)",
        "name_eng": "Building B (Classrooms B101-B210 & Pharmacy)",
        "desc_spa": "Edificio B: Módulo Comercial 1 (Farmacia), Aulas B101-B109 (Piso 1), B201-B210 (Piso 2), sanitarios, bebederos y fotocopias.",
        "desc_eng": "Building B: Commercial Module 1 (Pharmacy), Classrooms B101-B109 (Floor 1), B201-B210 (Floor 2), restrooms, drinking fountains, and photocopy shop.",
    },
    "buildingC": {
        "name_spa": "Edificio C (Laboratorios de Computación & Tesorería)",
        "name_eng": "Building C (Computer Labs & Treasury)",
        "desc_spa": "Edificio C: Auditorios C101 y C109, Aulas C102-C106, Caja UAM / Tesorería C105, Lab MAC C107, Lab ACAI-Erasmus+ C108, Labs C201-C205, Bodega C206, Aulas C209-C211 y C301-C310.",
        "desc_eng": "Building C: Auditoriums C101 & C109, Classrooms C102-C106, UAM Cashier / Treasury C105, MAC Lab C107, ACAI-Erasmus+ Lab C108, Labs C201-C205, Storage C206, Classrooms C209-C211 and C301-C310.",
    },
    "buildingD": {
        "name_spa": "Edificio D (Odontología Digital)",
        "name_eng": "Building D (Digital Dentistry)",
        "desc_spa": "Edificio D: Aula D102, Laboratorio de Odontología Digital CAM-CAM, Oficina de Servicio al Cliente y Sala de Reunión.",
        "desc_eng": "Building D: Classroom D102, CAM-CAM Digital Dentistry Lab, Customer Service Office, and Meeting Room.",
    },
    "buildingE": {
        "name_spa": "Edificio E (Facultad de Medicina & Clínicas Médicas)",
        "name_eng": "Building E (Faculty of Medicine & Medical Clinics)",
        "desc_spa": "Edificio E: Clínicas Médicas, Sanitarios, Cardiología, Facultad de Ciencias Médicas, Vida Estudiantil (DVE), DIE, Bancas, Simuladores E201, Psicología y Laboratorio Clínico.",
        "desc_eng": "Building E: Medical Clinics, Restrooms, Cardiology, Faculty of Medical Sciences, Student Life (DVE), DIE, Benches, Simulators E201, Psychology, and Clinical Lab.",
    },
    "buildingF": {
        "name_spa": "Edificio F (FCAE, FMDCC & Posgrados)",
        "name_eng": "Building F (FCAE, FMDCC & Postgraduate Programs)",
        "desc_spa": "Edificio F: Salón de Profesores, Dirección de Posgrados y Educación Continua, FCAE y FMDCC.",
        "desc_eng": "Building F: Faculty Lounge, Postgraduate & Continuing Education Directorate, FCAE, and FMDCC.",
    },
    "buildingG": {
        "name_spa": "Edificio G (Derecho FCJHRI, Language Center & Auditorio Central)",
        "name_eng": "Building G (Law FCJHRI, Language Center & Central Auditorium)",
        "desc_spa": "Edificio G: FCJHRI, Auditorio FCJHRI, Centro de Mediación y Arbitraje, Language Center, UAM College, Relaciones Internacionales, Baños Mixtos/Inclusivos y Auditorio Central Rubén Darío.",
        "desc_eng": "Building G: FCJHRI, FCJHRI Auditorium, Mediation & Arbitration Center, Language Center, UAM College, International Relations, Mixed/Inclusive Restrooms, and Rubén Darío Central Auditorium.",
    },
    "buildingH": {
        "name_spa": "Edificio H (Laboratorios de Medicina)",
        "name_eng": "Building H (Medical Laboratories)",
        "desc_spa": "Edificio H: Baños, Laboratorios de Medicina H101-H107, Coordinación de Gestión de Calidad, Supervisión de Laboratorios (Piso 1) y Laboratorios H201-H207 (Piso 2).",
        "desc_eng": "Building H: Restrooms, Medical Labs H101-H107, Quality Management Coordination, Lab Supervision (Floor 1), and Medical Labs H201-H207 (Floor 2).",
    },
    "buildingI": {
        "name_spa": "Edificio I (Rectoría & Biblioteca Pablo Antonio Cuadra)",
        "name_eng": "Building I (Rectorate & Pablo Antonio Cuadra Library)",
        "desc_spa": "Edificio I: Vicepresidencia, Sala de Reunión Directores, Dirección Académica, Rectoría, Gerencia General, Secretaría General, Biblioteca Pablo Antonio Cuadra, Baños Biblioteca y Relaciones Públicas.",
        "desc_eng": "Building I: Vice Presidency, Directors' Meeting Room, Academic Directorate, Rectorate, General Management, General Secretariat, Pablo Antonio Cuadra Library, Library Restrooms, and Public Relations.",
    },
    "buildingJ": {
        "name_spa": "Edificio J (Laboratorios de Odontología)",
        "name_eng": "Building J (Dental Laboratories)",
        "desc_spa": "Edificio J: Laboratorios de Odontología J101 y J102, Baños Hombres y Mujeres y Mapa UAM.",
        "desc_eng": "Building J: Dental Labs J101 & J102, Men's & Women's Restrooms, and UAM Map.",
    },
    "buildingK": {
        "name_spa": "Edificio K (Cafetería Central, Jaguar Shop & Terrazas)",
        "name_eng": "Building K (Central Cafeteria, Jaguar Shop & Terraces)",
        "desc_spa": "Edificio K: Baños Hombres/Mujeres, Área de Mesas, Terrazas, Jaguar Shop, Módulos Comerciales (Food Court), Kiosko 1 (P1), Kioskos 1 y 2 y Área de Mesas (P2).",
        "desc_eng": "Building K: Men's & Women's Restrooms, Seating Area, Terraces, Jaguar Shop, Commercial Modules (Food Court), Kiosk 1 (F1), Kiosks 1 & 2, and Seating Area (F2).",
    },
    "buildingL": {
        "name_spa": "Edificio L (Cultura, Música & Vestidores)",
        "name_eng": "Building L (Culture, Music & Locker Rooms)",
        "desc_spa": "Edificio L: Duchas Visitantes, Duchas Home, Salón de Cultura, Aula de Música, Baños Hombres y Baños Mujeres.",
        "desc_eng": "Building L: Visiting Team Showers, Home Team Showers, Culture Hall, Music Classroom, Men's Restrooms, and Women's Restrooms.",
    },
    "buildingM": {
        "name_spa": "Edificio M (Auditorios M101-M102, Aulas M201-M304 & Posgrados)",
        "name_eng": "Building M (Auditoriums M101-M102, Classrooms M201-M304 & Graduate Studies)",
        "desc_spa": "Edificio M: Auditorios M101 y M102, Dirección de Gestión Ambiental y Energética, Dirección de Investigación y Extensión Universitaria, Aula, Sanitarios, Bebedero, Aulas M201-M204 y M301-M304.",
        "desc_eng": "Building M: Auditoriums M101 & M102, Environmental & Energy Management Directorate, Research & University Extension Directorate, Classroom, Restrooms, Drinking Fountain, Classrooms M201-M204 and M301-M304.",
    },
    "buildingN": {
        "name_spa": "Edificio N (Clínicas Odontológicas & FODO)",
        "name_eng": "Building N (Dental Clinics & FODO)",
        "desc_spa": "Edificio N: Recepción de Clínicas Odontológicas (Quirófanos 1-2, Clínicas A/B/E y Post-Grado C-D, Radiología 1-3, Tomografía, Esterilización, Lab Fabricación Digital, Oficina IDEA), Sanitarios H/M y Facultad de Odontología (FODO Piso 2).",
        "desc_eng": "Building N: Dental Clinics Reception (Operating Rooms 1-2, Clinics A/B/E & Postgraduate C-D, Radiology 1-3, Tomography, Sterilization, Digital Fabrication Lab, IDEA Office), Men's/Women's Restrooms, and Faculty of Dentistry (FODO Floor 2).",
    },
    "buildingO": {
        "name_spa": "Edificio O (Facultad de Ingeniería y Arquitectura)",
        "name_eng": "Building O (Faculty of Engineering & Architecture)",
        "desc_spa": "Edificio O: Facultad de Ingeniería y Arquitectura (O101), Laboratorios Suelos (O102), Materiales (O104) y Fluidos, Riesgos (O105), Anexo Norte, Lab Redes O201, Aula O202, Sala de Tutoría, CIAR y Centro de Redes.",
        "desc_eng": "Building O: Faculty of Engineering & Architecture (O101), Soils (O102), Materials (O104) & Fluids Labs, Disaster Risk Coordination (O105), North Annex, Networks Lab O201, Classroom O202, Tutoring Room, CIAR, and Networks Center.",
    },
    "buildingP": {
        "name_spa": "Edificio P (Copérnico)",
        "name_eng": "Building P (Copernicus)",
        "desc_spa": "Edificio Copérnico (P): Estación de Meteorología, Aulas P101-P108, P201-P208, P301-P308, Aula P401 y Observatorio Copérnico (P501).",
        "desc_eng": "Building P (Copernicus): Weather Station, Classrooms P101-P108, P201-P208, P301-P308, Classroom P401, and Copernicus Observatory (P501).",
    },
    "jaguarCenter": {
        "name_spa": "Complejo Deportivo Jaguar Center",
        "name_eng": "Jaguar Center Sports Complex",
        "desc_spa": "Complejo Jaguar Center: Salón de Artes Marciales, Salón de Usos Múltiples - DVE, Cancha Multi-Usos, Cancha de Volleyball Arena, Kiosko Jaguar Sport, Clínica Fisioterapia, Gimnasio JAGUAR GYM, Psicología Deportiva, Bodega General y Comedor de Colaboradores.",
        "desc_eng": "Jaguar Center Sports Complex: Martial Arts Hall, Multipurpose Hall - DVE, Multipurpose Court, Beach Volleyball Court, Jaguar Sport Kiosk, Physiotherapy Clinic, Jaguar Gym, Sports Psychology, General Warehouse, and Staff Dining Hall.",
    },
    "sportsZone": {
        "name_spa": "Campos Deportivos (Estadio Jaguar & Cancha de Fútbol)",
        "name_eng": "Sports Fields (Jaguar Stadium & Soccer Field)",
        "desc_spa": "Campos Deportivos: Estadio de Baseball (Jaguar Stadium), Cancha de Fútbol, Baños Hombres y Mujeres, Kiosko Jaguarcito, Oficinas de Deportes y Bodega de Deportes.",
        "desc_eng": "Sports Fields: Baseball Stadium (Jaguar Stadium), Soccer Field, Men's & Women's Restrooms, Jaguarcito Kiosk, Sports Offices, and Sports Equipment Storage.",
    },
}


# =============================================================================
# 2. PLACES_CATALOG LOCALIZATION (ALL 217 CATALOG ENTRIES — NAME & NOTES)
# =============================================================================
PLACE_TRANSLATIONS: Dict[str, Dict[str, str]] = {
    # --- BUILDING A ---
    "accountingOfficeA": {
        "name_eng": "Accounting & Finance",
        "notes_spa": "Piso 1, pasillo izquierdo cerca del CAE.",
        "notes_eng": "Floor 1, left hallway near CAE.",
    },
    "studentCareCenterA": {
        "name_eng": "Student Care Center (CAE)",
        "notes_spa": "Piso 1, vestíbulo central.",
        "notes_eng": "Floor 1, central lobby.",
    },
    "academicRecordsA": {
        "name_eng": "Academic Records",
        "notes_spa": "Piso 1, mostrador principal de atención.",
        "notes_eng": "Floor 1, main service desk.",
    },
    "lostAndFoundOfficeA": {
        "name_eng": "Lost & Found Office (JaguarFind)",
        "notes_spa": "Piso 1, recepción principal.",
        "notes_eng": "Floor 1, main reception desk.",
    },
    "atmMachinesA": {
        "name_eng": "ATMs (BAC & LAFISE)",
        "notes_spa": "Exterior del Edificio A, fachada oeste.",
        "notes_eng": "Outside Building A, western facade.",
    },
    "admissionsMarketingA": {
        "name_eng": "Admissions & Marketing Directorate (Building A)",
        "notes_spa": "Edificio A, Piso 1, zona CAE.",
        "notes_eng": "Building A, Floor 1, CAE area.",
    },
    "collectionsOfficeA": {
        "name_eng": "Collections / Finance Directorate (Building A)",
        "notes_spa": "Edificio A, Piso 1, atención financiera.",
        "notes_eng": "Building A, Floor 1, financial services.",
    },
    "academicDirectorateA": {
        "name_eng": "Academic Directorate (Building A)",
        "notes_spa": "Edificio A, Piso 1.",
        "notes_eng": "Building A, Floor 1.",
    },
    "adminDirectorateA": {
        "name_eng": "Administrative & Academic Logistics Directorate (A-201)",
        "notes_spa": "Edificio A, Piso 2.",
        "notes_eng": "Building A, Floor 2.",
    },
    "ticDirectorateA": {
        "name_eng": "Information & Communications Technology Directorate - IT/TIC (A-203)",
        "notes_spa": "Edificio A, Piso 2.",
        "notes_eng": "Building A, Floor 2.",
    },
    "marketingAdvertisingA": {
        "name_eng": "Marketing & Advertising (A-204)",
        "notes_spa": "Edificio A, Piso 2.",
        "notes_eng": "Building A, Floor 2.",
    },
    "hrTalentA": {
        "name_eng": "Talent Management / Human Resources Directorate (A-205)",
        "notes_spa": "Edificio A, Piso 2.",
        "notes_eng": "Building A, Floor 2.",
    },
    "dpaAudiovisualA": {
        "name_eng": "Audiovisual Production Directorate - DPA (Studio A-301, Cyclorama, Sound & Radio)",
        "notes_spa": "Edificio A, Piso 3: DPA, Set de grabación ciclograma, estudio de sonido, oficinas auxiliares DPA, control máster y set de radio.",
        "notes_eng": "Building A, Floor 3: DPA, Cyclorama recording set, sound studio, DPA auxiliary offices, master control, and radio set.",
    },

    # --- BUILDING B ---
    "pharmacyB": {
        "name_eng": "Commercial Module 1 (Pharmacy)",
        "notes_spa": "Entrada del primer piso.",
        "notes_eng": "Floor 1 entrance.",
    },
    "classroomB101": {
        "name_eng": "Classroom B-101",
        "notes_spa": "Edificio B, Piso 1, pasillo este junto a Farmacia.",
        "notes_eng": "Building B, Floor 1, east hallway next to Pharmacy.",
    },
    "classroomB102": {
        "name_eng": "Classroom B-102",
        "notes_spa": "Edificio B, Piso 1, pasillo este.",
        "notes_eng": "Building B, Floor 1, east hallway.",
    },
    "classroomB103": {
        "name_eng": "Classroom B-103",
        "notes_spa": "Edificio B, Piso 1, pasillo central.",
        "notes_eng": "Building B, Floor 1, central hallway.",
    },
    "classroomB104": {
        "name_eng": "Classroom B-104",
        "notes_spa": "Edificio B, Piso 1, pasillo central.",
        "notes_eng": "Building B, Floor 1, central hallway.",
    },
    "classroomB105": {
        "name_eng": "Classroom B-105",
        "notes_spa": "Edificio B, Piso 1, pasillo central.",
        "notes_eng": "Building B, Floor 1, central hallway.",
    },
    "classroomB106": {
        "name_eng": "Classroom B-106",
        "notes_spa": "Edificio B, Piso 1, pasillo central.",
        "notes_eng": "Building B, Floor 1, central hallway.",
    },
    "classroomB107": {
        "name_eng": "Classroom B-107",
        "notes_spa": "Edificio B, Piso 1, pasillo oeste.",
        "notes_eng": "Building B, Floor 1, west hallway.",
    },
    "classroomB108": {
        "name_eng": "Classroom B-108",
        "notes_spa": "Edificio B, Piso 1, pasillo oeste.",
        "notes_eng": "Building B, Floor 1, west hallway.",
    },
    "classroomB109": {
        "name_eng": "Classroom B-109",
        "notes_spa": "Edificio B, Piso 1, extremo oeste del pasillo.",
        "notes_eng": "Building B, Floor 1, west end of hallway.",
    },
    "drinkingFountainB1": {
        "name_eng": "Drinking Fountain (Building B)",
        "notes_spa": "Primer piso, pasillo central junto a los sanitarios.",
        "notes_eng": "Floor 1, central corridor next to restrooms.",
    },
    "restroomsMenB1": {
        "name_eng": "Men's Restrooms (Building B)",
        "notes_spa": "Planta baja, pasillo central.",
        "notes_eng": "Ground floor, central hallway.",
    },
    "restroomsWomenB1": {
        "name_eng": "Women's Restrooms (Building B)",
        "notes_spa": "Planta baja, pasillo central.",
        "notes_eng": "Ground floor, central hallway.",
    },
    "photocopyShopB": {
        "name_eng": "Jaguar Shop Photocopies",
        "notes_spa": "Al final del pasillo de planta baja.",
        "notes_eng": "End of ground floor hallway.",
    },
    "classroomB201": {
        "name_eng": "Classroom B-201",
        "notes_spa": "Edificio B, Piso 2, extremo este.",
        "notes_eng": "Building B, Floor 2, east end.",
    },
    "classroomB202": {
        "name_eng": "Classroom B-202",
        "notes_spa": "Edificio B, Piso 2, pasillo este.",
        "notes_eng": "Building B, Floor 2, east hallway.",
    },
    "classroomB203": {
        "name_eng": "Classroom B-203",
        "notes_spa": "Edificio B, Piso 2, pasillo este.",
        "notes_eng": "Building B, Floor 2, east hallway.",
    },
    "classroomB204": {
        "name_eng": "Classroom B-204",
        "notes_spa": "Edificio B, Piso 2, pasillo central.",
        "notes_eng": "Building B, Floor 2, central hallway.",
    },
    "classroomB205": {
        "name_eng": "Classroom B-205",
        "notes_spa": "Edificio B, Piso 2, pasillo central.",
        "notes_eng": "Building B, Floor 2, central hallway.",
    },
    "classroomB206": {
        "name_eng": "Classroom B-206",
        "notes_spa": "Edificio B, Piso 2, pasillo central.",
        "notes_eng": "Building B, Floor 2, central hallway.",
    },
    "classroomB207": {
        "name_eng": "Classroom B-207",
        "notes_spa": "Edificio B, Piso 2, pasillo oeste.",
        "notes_eng": "Building B, Floor 2, west hallway.",
    },
    "classroomB208": {
        "name_eng": "Classroom B-208",
        "notes_spa": "Edificio B, Piso 2, pasillo oeste.",
        "notes_eng": "Building B, Floor 2, west hallway.",
    },
    "classroomB209": {
        "name_eng": "Classroom B-209",
        "notes_spa": "Edificio B, Piso 2, extremo oeste junto a las escaleras.",
        "notes_eng": "Building B, Floor 2, west end next to the stairs.",
    },
    "classroomB210": {
        "name_eng": "Classroom B-210",
        "notes_spa": "Edificio B, Piso 2, extremo oeste junto a las escaleras.",
        "notes_eng": "Building B, Floor 2, west end next to the stairs.",
    },
    "drinkingFountainBetweenBC": {
        "name_eng": "Drinking Fountain (Between Building B & C)",
        "notes_spa": "Pasillo exterior que conecta el Edificio B y el Edificio C.",
        "notes_eng": "Outdoor walkway connecting Building B and Building C.",
    },

    # --- BUILDING C ---
    "auditoriumC101": {
        "name_eng": "Auditorium C-101",
        "notes_spa": "Planta baja, ala este cerca de las escaleras izquierda.",
        "notes_eng": "Ground floor, east wing near left stairs.",
    },
    "classroomC102": {
        "name_eng": "Classroom C-102",
        "notes_spa": "Planta baja, pasillo central este.",
        "notes_eng": "Ground floor, east-central hallway.",
    },
    "classroomC103": {
        "name_eng": "Classroom C-103",
        "notes_spa": "Planta baja, pasillo central.",
        "notes_eng": "Ground floor, central hallway.",
    },
    "classroomC104": {
        "name_eng": "Classroom C-104",
        "notes_spa": "Planta baja, pasillo central.",
        "notes_eng": "Ground floor, central hallway.",
    },
    "drinkingFountainC1": {
        "name_eng": "Drinking Fountain (Building C - Floor 1)",
        "notes_spa": "Planta baja, junto al Aula C-103.",
        "notes_eng": "Ground floor, next to Classroom C-103.",
    },
    "treasuryC105": {
        "name_eng": "UAM Treasury (C-105)",
        "notes_spa": "Planta baja, oficina de tesorería institucional.",
        "notes_eng": "Ground floor, institutional treasury office.",
    },
    "cashierUamC": {
        "name_eng": "UAM Cashier (Financial Services)",
        "notes_spa": "Planta baja, vestíbulo central frente a rampa accesible.",
        "notes_eng": "Ground floor, central lobby across from accessible ramp.",
    },
    "mapUamC_F1": {
        "name_eng": "UAM Map (Building C Entrance)",
        "notes_spa": "Planta baja, entrada y directorio.",
        "notes_eng": "Ground floor, entrance and directory.",
    },
    "rampC_F1": {
        "name_eng": "Building C Accessible Ramp",
        "notes_spa": "Acceso accesible exterior frente al vestíbulo de Caja.",
        "notes_eng": "Outdoor accessible ramp in front of Cashier lobby.",
    },
    "classroomC106": {
        "name_eng": "Classroom C-106",
        "notes_spa": "Planta baja, pasillo oeste.",
        "notes_eng": "Ground floor, west hallway.",
    },
    "macLabC107": {
        "name_eng": "MAC Lab (C-107)",
        "notes_spa": "Planta baja, ala oeste de cómputo.",
        "notes_eng": "Ground floor, west computing wing.",
    },
    "erasmusLabC108": {
        "name_eng": "ACAI-Erasmus+ Lab (C-108)",
        "notes_spa": "Planta baja, ala oeste de cómputo.",
        "notes_eng": "Ground floor, west computing wing.",
    },
    "auditoriumC109": {
        "name_eng": "Auditorium C-109",
        "notes_spa": "Planta baja, extremo oeste junto a escaleras derecha.",
        "notes_eng": "Ground floor, west end next to right stairs.",
    },
    "computerLabC201": {
        "name_eng": "Computer Lab (C-201)",
        "notes_spa": "Segundo piso, ala este de laboratorios.",
        "notes_eng": "Floor 2, east labs wing.",
    },
    "computerLabC202": {
        "name_eng": "Computer Lab (C-202)",
        "notes_spa": "Segundo piso, junto a escaleras izquierda.",
        "notes_eng": "Floor 2, next to left stairs.",
    },
    "macLabC203": {
        "name_eng": "MAC Lab (C-203)",
        "notes_spa": "Segundo piso, laboratorio de diseño y MAC.",
        "notes_eng": "Floor 2, design and MAC laboratory.",
    },
    "computerLabC204": {
        "name_eng": "Computer Lab (C-204)",
        "notes_spa": "Segundo piso, pasillo central.",
        "notes_eng": "Floor 2, central hallway.",
    },
    "drinkingFountainC2": {
        "name_eng": "Drinking Fountain (Building C - Floor 2)",
        "notes_spa": "Segundo piso, junto al Lab C-204.",
        "notes_eng": "Floor 2, next to Lab C-204.",
    },
    "computerLabC205": {
        "name_eng": "Computer Lab (C-205)",
        "notes_spa": "Segundo piso, pasillo central.",
        "notes_eng": "Floor 2, central hallway.",
    },
    "warehouseC206": {
        "name_eng": "Academic Logistics Storage (C-206)",
        "notes_spa": "Segundo piso, almacén y logística.",
        "notes_eng": "Floor 2, storage and logistics.",
    },
    "restroomsMenC2": {
        "name_eng": "Men's Restrooms (Building C - Floor 2)",
        "notes_spa": "Segundo piso, bloque central.",
        "notes_eng": "Floor 2, central block.",
    },
    "restroomsWomenC2": {
        "name_eng": "Women's Restrooms (Building C - Floor 2)",
        "notes_spa": "Segundo piso, bloque central.",
        "notes_eng": "Floor 2, central block.",
    },
    "classroomC209": {
        "name_eng": "Classroom C-209",
        "notes_spa": "Segundo piso, pasillo oeste.",
        "notes_eng": "Floor 2, west hallway.",
    },
    "classroomC210": {
        "name_eng": "Classroom C-210",
        "notes_spa": "Segundo piso, pasillo oeste.",
        "notes_eng": "Floor 2, west hallway.",
    },
    "classroomC211": {
        "name_eng": "Classroom C-211",
        "notes_spa": "Segundo piso, extremo oeste junto a escaleras derecha.",
        "notes_eng": "Floor 2, west end next to right stairs.",
    },
    "studioA301": {
        "name_eng": "Audiovisual Studio A-301 (Floor 3)",
        "notes_spa": "Tercer piso, extremo este sobre conexión A y C.",
        "notes_eng": "Floor 3, east end above Building A & C connection.",
    },
    "classroomC301": {
        "name_eng": "Classroom C-301",
        "notes_spa": "Tercer piso, pasillo este.",
        "notes_eng": "Floor 3, east hallway.",
    },
    "classroomC302": {
        "name_eng": "Classroom C-302",
        "notes_spa": "Tercer piso, pasillo este.",
        "notes_eng": "Floor 3, east hallway.",
    },
    "classroomC303": {
        "name_eng": "Classroom C-303",
        "notes_spa": "Tercer piso, pasillo central este.",
        "notes_eng": "Floor 3, east-central hallway.",
    },
    "classroomC304": {
        "name_eng": "Classroom C-304",
        "notes_spa": "Tercer piso, pasillo central.",
        "notes_eng": "Floor 3, central hallway.",
    },
    "classroomC305": {
        "name_eng": "Classroom C-305",
        "notes_spa": "Tercer piso, pasillo central entre C-304 y Coordinación de Compras.",
        "notes_eng": "Floor 3, central hallway between C-304 and Procurement Coordination.",
    },
    "procurementCoordC306": {
        "name_eng": "Procurement Coordination (C-306)",
        "notes_spa": "Tercer piso, departamento administrativo de compras.",
        "notes_eng": "Floor 3, administrative procurement office.",
    },
    "classroomC307": {
        "name_eng": "Classroom C-307",
        "notes_spa": "Tercer piso, pasillo central oeste.",
        "notes_eng": "Floor 3, west-central hallway.",
    },
    "classroomC308": {
        "name_eng": "Classroom C-308",
        "notes_spa": "Tercer piso, pasillo central oeste.",
        "notes_eng": "Floor 3, west-central hallway.",
    },
    "classroomC309": {
        "name_eng": "Classroom C-309",
        "notes_spa": "Tercer piso, pasillo oeste.",
        "notes_eng": "Floor 3, west hallway.",
    },
    "classroomC310": {
        "name_eng": "Classroom C-310",
        "notes_spa": "Tercer piso, extremo oeste junto a escaleras derecha.",
        "notes_eng": "Floor 3, west end next to right stairs.",
    },

    # --- BUILDING D ---
    "camCamLabD": {
        "name_eng": "CAM-CAM Digital Dentistry Lab",
        "notes_spa": "Edificio D, Planta Única, laboratorio odontológico este.",
        "notes_eng": "Building D, Floor 1, east dental laboratory.",
    },
    "classroomD102": {
        "name_eng": "Classroom D-102",
        "notes_spa": "Edificio D, Planta Única, aula central sur.",
        "notes_eng": "Building D, Floor 1, south-central classroom.",
    },
    "customerServiceD": {
        "name_eng": "Customer Service Office",
        "notes_spa": "Edificio D, Planta Única, área de atención en lobby.",
        "notes_eng": "Building D, Floor 1, lobby service desk.",
    },
    "meetingRoomD": {
        "name_eng": "Meeting Room (Building D)",
        "notes_spa": "Edificio D, Planta Única, sala de reuniones en lobby.",
        "notes_eng": "Building D, Floor 1, lobby meeting room.",
    },
    "uamMapD": {
        "name_eng": "UAM Map (Building D Entrance)",
        "notes_spa": "Edificio D, Entrada exterior, panel y directorio del Mapa UAM.",
        "notes_eng": "Building D, outdoor entrance, UAM map and directory panel.",
    },

    # --- BUILDING E ---
    "facultyMedicineE": {
        "name_eng": "Faculty of Medical Sciences",
        "notes_spa": "Planta baja, oficina de decanatura.",
        "notes_eng": "Ground floor, deanery office.",
    },
    "medicalClinicsE": {
        "name_eng": "UAM Medical Clinics",
        "notes_spa": "Planta baja, sector clínico.",
        "notes_eng": "Ground floor, clinical sector.",
    },
    "cardiologyCenterE": {
        "name_eng": "Cardiology Center",
        "notes_spa": "Planta baja, centro especializado.",
        "notes_eng": "Ground floor, specialized center.",
    },
    "accessibleRestroomE": {
        "name_eng": "Inclusive Accessible Restrooms (Building E)",
        "notes_spa": "Planta baja, junto a los sanitarios generales.",
        "notes_eng": "Ground floor, next to general restrooms.",
    },
    "studentLifeOfficeE": {
        "name_eng": "Student Life Directorate (DVE)",
        "notes_spa": "Anexo oeste.",
        "notes_eng": "West annex.",
    },
    "innovationOfficeE": {
        "name_eng": "Innovation & Entrepreneurship Directorate (DIE)",
        "notes_spa": "Anexo norte.",
        "notes_eng": "North annex.",
    },
    "medicalSimulatorsE2": {
        "name_eng": "Medical Clinical Skills Simulators Lab",
        "notes_spa": "Segundo piso, sala de habilidades clínicas (E-201).",
        "notes_eng": "Floor 2, medical skills ward (E-201).",
    },
    "psychologyOfficeE": {
        "name_eng": "Psychology Office (Building E)",
        "notes_spa": "Edificio E, atención psicológica.",
        "notes_eng": "Building E, psychological care office.",
    },
    "clinicalMedicineLabE": {
        "name_eng": "Clinical Medicine Lab (Building E)",
        "notes_spa": "Edificio E, laboratorio clínico.",
        "notes_eng": "Building E, clinical laboratory.",
    },

    # --- BUILDING F ---
    "facultyBusinessF": {
        "name_eng": "Faculty of Administrative & Economic Sciences (FCAE)",
        "notes_spa": "Planta baja.",
        "notes_eng": "Ground floor.",
    },
    "facultyMarketingF": {
        "name_eng": "Faculty of Marketing, Design & Communication (FMDCC)",
        "notes_spa": "Planta baja.",
        "notes_eng": "Ground floor.",
    },
    "postgraduateDirectorateF": {
        "name_eng": "Postgraduate & Continuing Education Directorate",
        "notes_spa": "Planta baja.",
        "notes_eng": "Ground floor.",
    },
    "teachersLoungeF": {
        "name_eng": "Faculty Lounge (Building F)",
        "notes_spa": "Edificio F, Planta Baja.",
        "notes_eng": "Building F, Ground floor.",
    },

    # --- BUILDING G ---
    "facultyLawG": {
        "name_eng": "Faculty of Legal Sciences & International Relations",
        "notes_spa": "Piso 1.",
        "notes_eng": "Floor 1.",
    },
    "languageCenterG": {
        "name_eng": "UAM Language Center",
        "notes_spa": "Ala del primer piso.",
        "notes_eng": "Floor 1 wing.",
    },
    "auditoriumCentralG": {
        "name_eng": "Central Auditorium / Rubén Darío Auditorium",
        "notes_spa": "Segundo piso, salón principal del auditorio.",
        "notes_eng": "Floor 2, main auditorium hall.",
    },
    "accessibleRestroomG": {
        "name_eng": "Inclusive Accessible Restrooms (Building G)",
        "notes_spa": "Piso 1, cerca de la entrada.",
        "notes_eng": "Floor 1, near entrance.",
    },
    "auditoriumFcjhriG": {
        "name_eng": "FCJHRI Auditorium (Building G)",
        "notes_spa": "Edificio G, Piso 1, Facultad de Ciencias Jurídicas.",
        "notes_eng": "Building G, Floor 1, Faculty of Legal Sciences.",
    },
    "mediationCenterG": {
        "name_eng": "Mediation & Arbitration Center (Building G)",
        "notes_spa": "Edificio G, Piso 1.",
        "notes_eng": "Building G, Floor 1.",
    },
    "uamCollegeG": {
        "name_eng": "UAM College & International Relations (Building G)",
        "notes_spa": "Edificio G, Piso 1.",
        "notes_eng": "Building G, Floor 1.",
    },

    # --- BUILDING H ---
    "medicalLabH101": {
        "name_eng": "Medical Lab H-101",
        "notes_spa": "Edificio H, Piso 1.",
        "notes_eng": "Building H, Floor 1.",
    },
    "medicalLabH102": {
        "name_eng": "Medical Lab H-102",
        "notes_spa": "Edificio H, Piso 1.",
        "notes_eng": "Building H, Floor 1.",
    },
    "medicalLabH103": {
        "name_eng": "Medical Lab H-103",
        "notes_spa": "Edificio H, Piso 1.",
        "notes_eng": "Building H, Floor 1.",
    },
    "medicalLabH104": {
        "name_eng": "Medical Lab H-104 (Quality Management Coordination)",
        "notes_spa": "Edificio H, Piso 1.",
        "notes_eng": "Building H, Floor 1.",
    },
    "medicalLabH105": {
        "name_eng": "Medical Lab H-105",
        "notes_spa": "Edificio H, Piso 1.",
        "notes_eng": "Building H, Floor 1.",
    },
    "medicalLabH106": {
        "name_eng": "Medical Lab H-106",
        "notes_spa": "Edificio H, Piso 1.",
        "notes_eng": "Building H, Floor 1.",
    },
    "medicalLabH107": {
        "name_eng": "Medical Lab H-107",
        "notes_spa": "Edificio H, Piso 1.",
        "notes_eng": "Building H, Floor 1.",
    },
    "labSupervisionOfficeH": {
        "name_eng": "Medical Labs Supervision Office",
        "notes_spa": "Edificio H, Supervisión de Laboratorios y acceso Necroteca.",
        "notes_eng": "Building H, Lab Supervision Office and Anatomy Lab access.",
    },
    "medicalLabH201": {
        "name_eng": "Medical Lab H-201",
        "notes_spa": "Edificio H, Piso 2.",
        "notes_eng": "Building H, Floor 2.",
    },
    "medicalLabH202": {
        "name_eng": "Medical Lab H-202",
        "notes_spa": "Edificio H, Piso 2.",
        "notes_eng": "Building H, Floor 2.",
    },
    "medicalLabH203": {
        "name_eng": "Medical Lab H-203",
        "notes_spa": "Edificio H, Piso 2.",
        "notes_eng": "Building H, Floor 2.",
    },
    "medicalLabH204": {
        "name_eng": "Medical Lab H-204",
        "notes_spa": "Edificio H, Piso 2.",
        "notes_eng": "Building H, Floor 2.",
    },
    "medicalLabH205": {
        "name_eng": "Medical Lab H-205",
        "notes_spa": "Edificio H, Piso 2.",
        "notes_eng": "Building H, Floor 2.",
    },
    "medicalLabH206": {
        "name_eng": "Medical Lab H-206",
        "notes_spa": "Edificio H, Piso 2.",
        "notes_eng": "Building H, Floor 2.",
    },
    "medicalLabH207": {
        "name_eng": "Medical Lab H-207",
        "notes_spa": "Edificio H, Piso 2.",
        "notes_eng": "Building H, Floor 2.",
    },

    # --- BUILDING I ---
    "centralLibraryI": {
        "name_eng": "Pablo Antonio Cuadra Central Library",
        "notes_spa": "Ala de entrada principal.",
        "notes_eng": "Main entrance wing.",
    },
    "rectorateOfficeI": {
        "name_eng": "UAM Rectorate",
        "notes_spa": "Ala ejecutiva.",
        "notes_eng": "Executive wing.",
    },

    # --- BUILDING J ---
    "dentalLabJ101": {
        "name_eng": "Dental Lab J-101",
        "notes_spa": "Edificio J, Planta Única, laboratorio norte.",
        "notes_eng": "Building J, Floor 1, north laboratory.",
    },
    "dentalLabJ102": {
        "name_eng": "Dental Lab J-102",
        "notes_spa": "Edificio J, Planta Única, laboratorio sureste.",
        "notes_eng": "Building J, Floor 1, southeast laboratory.",
    },
    "restroomsWomenJ": {
        "name_eng": "Women's Restrooms (Building J)",
        "notes_spa": "Edificio J, Planta Única, pasillo oeste.",
        "notes_eng": "Building J, Floor 1, west hallway.",
    },
    "restroomsMenJ": {
        "name_eng": "Men's Restrooms (Building J)",
        "notes_spa": "Edificio J, Planta Única, pasillo suroeste.",
        "notes_eng": "Building J, Floor 1, southwest hallway.",
    },
    "entranceJ": {
        "name_eng": "Building J Main Entrance",
        "notes_spa": "Edificio J, Acceso principal exterior.",
        "notes_eng": "Building J, main outdoor access.",
    },

    # --- BUILDING K ---
    "centralCafeteriaK": {
        "name_eng": "Central Cafeteria & Jaguar Corner",
        "notes_spa": "Planta baja, plaza central de comidas.",
        "notes_eng": "Ground floor, central food court.",
    },
    "foodKiosksK": {
        "name_eng": "Commercial Kiosks & Terraces K",
        "notes_spa": "Área de terrazas.",
        "notes_eng": "Terrace area.",
    },

    # --- BUILDING L ---
    "cultureHallL": {
        "name_eng": "Culture Hall (Building L)",
        "notes_spa": "Edificio L, Planta Baja.",
        "notes_eng": "Building L, Ground floor.",
    },
    "musicClassroomL": {
        "name_eng": "Music Classroom (Building L)",
        "notes_spa": "Edificio L, Planta Baja.",
        "notes_eng": "Building L, Ground floor.",
    },
    "showersTeamsL": {
        "name_eng": "Home & Visiting Team Showers (Building L)",
        "notes_spa": "Edificio L, vestidores y duchas de equipos.",
        "notes_eng": "Building L, team locker rooms and showers.",
    },

    # --- BUILDING M ---
    "auditoriumM101": {
        "name_eng": "Auditorium M-101",
        "notes_spa": "Edificio M, Piso 1, ala norte.",
        "notes_eng": "Building M, Floor 1, north wing.",
    },
    "auditoriumM102": {
        "name_eng": "Auditorium M-102",
        "notes_spa": "Edificio M, Piso 1, ala norte.",
        "notes_eng": "Building M, Floor 1, north wing.",
    },
    "environmentalDirectorateM": {
        "name_eng": "Environmental & Energy Management Directorate (Building M)",
        "notes_spa": "Edificio M, Piso 1, ala sur.",
        "notes_eng": "Building M, Floor 1, south wing.",
    },
    "researchExtensionM": {
        "name_eng": "Research & University Extension Directorate (Building M)",
        "notes_spa": "Edificio M, Piso 1, ala sur.",
        "notes_eng": "Building M, Floor 1, south wing.",
    },
    "drinkingFountainM1": {
        "name_eng": "Drinking Fountain (Building M)",
        "notes_spa": "Planta baja, pasillo cerca de los sanitarios.",
        "notes_eng": "Ground floor corridor near restrooms.",
    },
    "classroomM201": {
        "name_eng": "Classroom M-201",
        "notes_spa": "Edificio M, Piso 2, ala norte.",
        "notes_eng": "Building M, Floor 2, north wing.",
    },
    "classroomM202": {
        "name_eng": "Classroom M-202",
        "notes_spa": "Edificio M, Piso 2, ala norte.",
        "notes_eng": "Building M, Floor 2, north wing.",
    },
    "classroomM203": {
        "name_eng": "Classroom M-203",
        "notes_spa": "Edificio M, Piso 2, ala sur.",
        "notes_eng": "Building M, Floor 2, south wing.",
    },
    "classroomM204": {
        "name_eng": "Classroom M-204",
        "notes_spa": "Edificio M, Piso 2, ala sur.",
        "notes_eng": "Building M, Floor 2, south wing.",
    },
    "classroomM301": {
        "name_eng": "Classroom M-301",
        "notes_spa": "Edificio M, Piso 3, ala norte.",
        "notes_eng": "Building M, Floor 3, north wing.",
    },
    "classroomM302": {
        "name_eng": "Classroom M-302",
        "notes_spa": "Edificio M, Piso 3, ala norte.",
        "notes_eng": "Building M, Floor 3, north wing.",
    },
    "classroomM303": {
        "name_eng": "Classroom M-303",
        "notes_spa": "Edificio M, Piso 3, ala sur.",
        "notes_eng": "Building M, Floor 3, south wing.",
    },
    "classroomM304": {
        "name_eng": "Classroom M-304",
        "notes_spa": "Edificio M, Piso 3, ala sur.",
        "notes_eng": "Building M, Floor 3, south wing.",
    },

    # --- BUILDING N ---
    "dentistryReceptionN": {
        "name_eng": "UAM Dental Clinics Reception",
        "notes_spa": "Mostrador de entrada pública principal.",
        "notes_eng": "Main public entrance counter.",
    },
    "facultyDentistryN": {
        "name_eng": "Faculty of Dentistry (FODO)",
        "notes_spa": "Decanatura del segundo piso.",
        "notes_eng": "Floor 2 deanery.",
    },

    # --- BUILDING O ---
    "facultyEngineeringO": {
        "name_eng": "Faculty of Engineering & Architecture (O-101)",
        "notes_spa": "Planta baja, Decanatura FIA.",
        "notes_eng": "Ground floor, FIA Deanery.",
    },
    "soilMechanicsLabO": {
        "name_eng": "Soil Mechanics Lab (O-102)",
        "notes_spa": "Planta baja, ala de laboratorios pesados.",
        "notes_eng": "Ground floor, heavy labs wing.",
    },
    "exhibitionAreaO": {
        "name_eng": "Exhibition Area (Building O)",
        "notes_spa": "Planta baja, área central de exhibición de proyectos.",
        "notes_eng": "Ground floor, central project exhibition area.",
    },
    "materialsLabO": {
        "name_eng": "Materials Testing Lab (O-104)",
        "notes_spa": "Planta baja, laboratorio de ensaye de materiales.",
        "notes_eng": "Ground floor, materials testing laboratory.",
    },
    "mixingAreaO": {
        "name_eng": "Mixing Area (Materials Lab)",
        "notes_spa": "Planta baja, área anexa a materiales.",
        "notes_eng": "Ground floor, area adjacent to Materials Lab.",
    },
    "curingAreaO": {
        "name_eng": "Curing Area (Materials Lab)",
        "notes_spa": "Planta baja, área de curado de probetas de concreto.",
        "notes_eng": "Ground floor, concrete specimen curing area.",
    },
    "labTechniciansO": {
        "name_eng": "Lab Technicians Office",
        "notes_spa": "Planta baja, oficina de soporte técnico de laboratorios.",
        "notes_eng": "Ground floor, laboratory technical support office.",
    },
    "fluidMechanicsLabO": {
        "name_eng": "Fluid Mechanics Lab",
        "notes_spa": "Planta baja, laboratorio de hidráulica y fluidos.",
        "notes_eng": "Ground floor, hydraulics and fluids laboratory.",
    },
    "disasterRiskCoordO": {
        "name_eng": "Comprehensive Disaster Risk Management Coordination (O-105)",
        "notes_spa": "Planta baja, oficina de gestión de riesgos.",
        "notes_eng": "Ground floor, disaster risk management office.",
    },
    "mapUamO": {
        "name_eng": "UAM Map (Building O Entrance)",
        "notes_spa": "Entrada principal y directorio del Edificio O.",
        "notes_eng": "Building O main entrance and directory.",
    },
    "restroomsMenO": {
        "name_eng": "Men's Restrooms (FIA Annex)",
        "notes_spa": "Anexo norte FIA.",
        "notes_eng": "FIA north annex.",
    },
    "restroomsWomenO": {
        "name_eng": "Women's Restrooms (FIA Annex)",
        "notes_spa": "Anexo norte FIA.",
        "notes_eng": "FIA north annex.",
    },
    "teachersLoungeO": {
        "name_eng": "FIA Faculty Lounge (North Annex)",
        "notes_spa": "Anexo norte FIA.",
        "notes_eng": "FIA north annex.",
    },
    "rampParkingO": {
        "name_eng": "Building O Accessible Ramp to Parking",
        "notes_spa": "Conexión accesible entre Edificio O y acera de estacionamiento.",
        "notes_eng": "Accessible connection between Building O and parking sidewalk.",
    },
    "networksLabO": {
        "name_eng": "Networks Lab (O-201)",
        "notes_spa": "Segundo piso, laboratorio de redes y conectividad.",
        "notes_eng": "Floor 2, networking and connectivity laboratory.",
    },
    "networksCenterO": {
        "name_eng": "Networks Center (Building O)",
        "notes_spa": "Segundo piso, infraestructura de redes.",
        "notes_eng": "Floor 2, network infrastructure center.",
    },
    "ciarLabO": {
        "name_eng": "Artificial Intelligence & Robotics Center (CIAR)",
        "notes_spa": "Segundo piso, centro tecnológico de IA y Robótica.",
        "notes_eng": "Floor 2, AI & Robotics technology center.",
    },
    "roboticsAreaO": {
        "name_eng": "Robotics Area (CIAR)",
        "notes_spa": "Segundo piso, área de hardware y prototipado robótico.",
        "notes_eng": "Floor 2, robotics hardware and prototyping area.",
    },
    "drinkingFountainO_F2": {
        "name_eng": "Drinking Fountain (Building O - Floor 2)",
        "notes_spa": "Segundo piso, junto a robótica.",
        "notes_eng": "Floor 2, next to Robotics Area.",
    },
    "tutoringRoomO": {
        "name_eng": "FIA Tutoring Room",
        "notes_spa": "Segundo piso, asesorías académicas FIA.",
        "notes_eng": "Floor 2, FIA academic tutoring room.",
    },
    "classroomO202": {
        "name_eng": "Classroom O-202",
        "notes_spa": "Segundo piso, aula teórica O-202.",
        "notes_eng": "Floor 2, lecture classroom O-202.",
    },

    # --- BUILDING P ---
    "copernicusObservatoryP": {
        "name_eng": "Copernicus Astronomical Observatory",
        "notes_spa": "Quinto piso, cúpula y azotea.",
        "notes_eng": "Floor 5, dome / rooftop.",
    },
    "classroomP401": {
        "name_eng": "Hall P-401 (Upper Annex)",
        "notes_spa": "Edificio P, Piso 4 (Anexo Superior).",
        "notes_eng": "Building P, Floor 4 (Upper Annex).",
    },
    "classroomP101": {
        "name_eng": "Classroom P-101",
        "notes_spa": "Edificio P, Planta Baja, pasillo este.",
        "notes_eng": "Building P, Ground floor, east hallway.",
    },
    "drinkingFountainP1": {
        "name_eng": "Drinking Fountain (Building P - Floor 1)",
        "notes_spa": "Edificio P, Planta Baja, junto a Salón P-101.",
        "notes_eng": "Building P, Ground floor, next to Classroom P-101.",
    },
    "classroomP102": {
        "name_eng": "Classroom P-102",
        "notes_spa": "Edificio P, Planta Baja.",
        "notes_eng": "Building P, Ground floor.",
    },
    "classroomP103": {
        "name_eng": "Classroom P-103",
        "notes_spa": "Edificio P, Planta Baja.",
        "notes_eng": "Building P, Ground floor.",
    },
    "classroomP104": {
        "name_eng": "Classroom P-104",
        "notes_spa": "Edificio P, Planta Baja.",
        "notes_eng": "Building P, Ground floor.",
    },
    "classroomP105": {
        "name_eng": "Classroom P-105",
        "notes_spa": "Edificio P, Planta Baja central.",
        "notes_eng": "Building P, Ground floor, central hallway.",
    },
    "classroomP106": {
        "name_eng": "Classroom P-106",
        "notes_spa": "Edificio P, Planta Baja.",
        "notes_eng": "Building P, Ground floor.",
    },
    "classroomP107": {
        "name_eng": "Classroom P-107",
        "notes_spa": "Edificio P, Planta Baja.",
        "notes_eng": "Building P, Ground floor.",
    },
    "classroomP108": {
        "name_eng": "Classroom P-108",
        "notes_spa": "Edificio P, Planta Baja oeste.",
        "notes_eng": "Building P, Ground floor, west hallway.",
    },
    "restroomsP1": {
        "name_eng": "Restrooms (Building P - Floor 1)",
        "notes_spa": "Edificio P, Planta Baja, extremo oeste.",
        "notes_eng": "Building P, Ground floor, west end.",
    },
    "rampParkingP": {
        "name_eng": "Accessible Ramp from Parking to Building P",
        "notes_spa": "Rampa desde el estacionamiento hacia el Edificio P, enfrente del Edificio O.",
        "notes_eng": "Ramp from the parking lot toward Building P, across from Building O.",
    },
    "classroomP201": {
        "name_eng": "Classroom P-201",
        "notes_spa": "Edificio P, Piso 2 este.",
        "notes_eng": "Building P, Floor 2, east hallway.",
    },
    "drinkingFountainP2East": {
        "name_eng": "2nd Drinking Fountain (Building P - Floor 2 East)",
        "notes_spa": "Edificio P, Piso 2, pasillo este.",
        "notes_eng": "Building P, Floor 2, east hallway.",
    },
    "classroomP202": {
        "name_eng": "Classroom P-202",
        "notes_spa": "Edificio P, Piso 2.",
        "notes_eng": "Building P, Floor 2.",
    },
    "classroomP203": {
        "name_eng": "Classroom P-203",
        "notes_spa": "Edificio P, Piso 2.",
        "notes_eng": "Building P, Floor 2.",
    },
    "classroomP204": {
        "name_eng": "Classroom P-204",
        "notes_spa": "Edificio P, Piso 2 central.",
        "notes_eng": "Building P, Floor 2, central hallway.",
    },
    "classroomP205": {
        "name_eng": "Classroom P-205",
        "notes_spa": "Edificio P, Piso 2 central.",
        "notes_eng": "Building P, Floor 2, central hallway.",
    },
    "classroomP206": {
        "name_eng": "Classroom P-206",
        "notes_spa": "Edificio P, Piso 2.",
        "notes_eng": "Building P, Floor 2.",
    },
    "classroomP207": {
        "name_eng": "Classroom P-207",
        "notes_spa": "Edificio P, Piso 2.",
        "notes_eng": "Building P, Floor 2.",
    },
    "classroomP208": {
        "name_eng": "Classroom P-208",
        "notes_spa": "Edificio P, Piso 2 oeste.",
        "notes_eng": "Building P, Floor 2, west hallway.",
    },
    "drinkingFountainP2West": {
        "name_eng": "Drinking Fountain (Building P - Floor 2 West)",
        "notes_spa": "Edificio P, Piso 2 junto a Salón P-208.",
        "notes_eng": "Building P, Floor 2, next to Classroom P-208.",
    },
    "restroomsP2": {
        "name_eng": "Restrooms (Building P - Floor 2)",
        "notes_spa": "Edificio P, Piso 2 oeste.",
        "notes_eng": "Building P, Floor 2, west end.",
    },
    "classroomP301": {
        "name_eng": "Classroom P-301",
        "notes_spa": "Edificio P, Piso 3 este.",
        "notes_eng": "Building P, Floor 3, east hallway.",
    },
    "drinkingFountainP3": {
        "name_eng": "1st Drinking Fountain (Building P - Floor 3)",
        "notes_spa": "Edificio P, Piso 3 este.",
        "notes_eng": "Building P, Floor 3, east hallway.",
    },
    "classroomP301B": {
        "name_eng": "Classroom P-301 (Access 2)",
        "notes_spa": "Edificio P, Piso 3.",
        "notes_eng": "Building P, Floor 3.",
    },
    "classroomP302": {
        "name_eng": "Classroom P-302",
        "notes_spa": "Edificio P, Piso 3.",
        "notes_eng": "Building P, Floor 3.",
    },
    "classroomP303": {
        "name_eng": "Classroom P-303",
        "notes_spa": "Edificio P, Piso 3.",
        "notes_eng": "Building P, Floor 3.",
    },
    "classroomP304": {
        "name_eng": "Classroom P-304",
        "notes_spa": "Edificio P, Piso 3.",
        "notes_eng": "Building P, Floor 3.",
    },
    "classroomP305": {
        "name_eng": "Classroom P-305",
        "notes_spa": "Edificio P, Piso 3 central.",
        "notes_eng": "Building P, Floor 3, central hallway.",
    },
    "classroomP306": {
        "name_eng": "Classroom P-306",
        "notes_spa": "Edificio P, Piso 3.",
        "notes_eng": "Building P, Floor 3.",
    },
    "classroomP306B": {
        "name_eng": "Classroom P-306 (Access 2)",
        "notes_spa": "Edificio P, Piso 3.",
        "notes_eng": "Building P, Floor 3.",
    },
    "classroomP307": {
        "name_eng": "Classroom P-307",
        "notes_spa": "Edificio P, Piso 3 oeste.",
        "notes_eng": "Building P, Floor 3, west hallway.",
    },
    "classroomP308": {
        "name_eng": "Classroom P-308",
        "notes_spa": "Edificio P, Piso 3 oeste.",
        "notes_eng": "Building P, Floor 3, west hallway.",
    },
    "weatherStationP": {
        "name_eng": "Weather Station (Building P)",
        "notes_spa": "Edificio P, Planta Baja, acceso este.",
        "notes_eng": "Building P, Ground floor, east entrance.",
    },
    "restroomsP3": {
        "name_eng": "Restrooms (Building P - Floor 3)",
        "notes_spa": "Edificio P, Piso 3 oeste.",
        "notes_eng": "Building P, Floor 3, west end.",
    },

    # --- SPORTS, OUTDOOR, GATES & RAMPS ---
    "jaguarGym": {
        "name_eng": "Jaguar Gym",
        "notes_spa": "Edificio Jaguar Gym, al sureste de Jaguar Center.",
        "notes_eng": "Jaguar Gym building, southeast of Jaguar Center.",
    },
    "physiotherapyClinic": {
        "name_eng": "Physiotherapy Clinic",
        "notes_spa": "Edificio de Fisioterapia, al norte de Jaguar Gym.",
        "notes_eng": "Physiotherapy building, north of Jaguar Gym.",
    },
    "baseballStadium": {
        "name_eng": "Baseball Stadium (Jaguar Stadium)",
        "notes_spa": "Complejo deportivo noreste.",
        "notes_eng": "Northeast sports complex.",
    },
    "soccerField": {
        "name_eng": "UAM Campus Soccer Field",
        "notes_spa": "Complejo deportivo noreste.",
        "notes_eng": "Northeast sports complex.",
    },
    "multipurposeCourtJC": {
        "name_eng": "Multipurpose & Beach Volleyball Court (Jaguar Center)",
        "notes_spa": "Complejo Deportivo Jaguar Center.",
        "notes_eng": "Jaguar Center Sports Complex.",
    },
    "generalWarehouseSZ": {
        "name_eng": "General Warehouse & Staff Dining Hall",
        "notes_spa": "Zona de bodega general, contenedores, oficinas deportivas 1-3 y comedor de colaboradores.",
        "notes_eng": "General warehouse, containers, Sports Offices 1-3, and staff dining hall.",
    },
    "chilamatesDining": {
        "name_eng": "Chilamates Plaza (Kiosks & Fast Point)",
        "notes_spa": "Plaza central exterior.",
        "notes_eng": "Outdoor central plaza.",
    },
    "jaguarJungleGarden": {
        "name_eng": "Jaguar Jungle (Nature Garden & Central Paths)",
        "notes_spa": "Área verde sombreada con senderos que conectan Edificio O, Mi Ranchito, Edificio H y la vía interna principal.",
        "notes_eng": "Shaded green garden area with walkways connecting Building O, Mi Ranchito, Building H, and the main internal road.",
    },
    "miRanchitoPavilion": {
        "name_eng": "Mi Ranchito (Campus Rest Pavilion)",
        "notes_spa": "Pabellón abierto de descanso y comedor junto a Jaguar Jungle, Edificio N y Lab Digital FIA.",
        "notes_eng": "Open-air rest and dining pavilion beside Jaguar Jungle, Building N, and FIA Digital Lab.",
    },
    "labDigitalFiaRoom": {
        "name_eng": "FIA Digital Lab (Engineering Digital Laboratory)",
        "notes_spa": "Laboratorio Digital FIA ubicado junto al Edificio N, cerca de Mi Ranchito y Área de Mesas.",
        "notes_eng": "FIA Digital Laboratory located beside Building N, near Mi Ranchito and Outdoor Tables Area.",
    },
    "areaDeMesasTerrace": {
        "name_eng": "Outdoor Tables Area (Study Terrace)",
        "notes_spa": "Mesas exteriores sombreadas y terraza de estudio entre Lab Digital FIA, Parqueo Central y Edificio C.",
        "notes_eng": "Shaded outdoor tables and study terrace between FIA Digital Lab, Central Parking, and Building C.",
    },
    "mainParkingSouth": {
        "name_eng": "Main Parking & South Gatehouse",
        "notes_spa": "Acceso vehicular y peatonal principal sur.",
        "notes_eng": "Main southern vehicle and pedestrian gate.",
    },
    "thirdAccessRoad": {
        "name_eng": "Third Access (Copernicus Gate)",
        "notes_spa": "Acceso vehicular y peatonal noroeste junto a Estación de Meteorología y Edificio P (Copérnico).",
        "notes_eng": "Northwest vehicle & pedestrian access gate beside Weather Station and Building P (Copernicus).",
    },
    "secondAccessRoad": {
        "name_eng": "Second Access (Jaguar Stadium Road)",
        "notes_spa": "Vía vehicular y peatonal norte frente al Estadio de Béisbol Jaguar hacia Parqueo Deportes y Edificio O.",
        "notes_eng": "Northern vehicle & pedestrian road past Jaguar Baseball Stadium connecting Sports Parking and Building O.",
    },
    "rampBuildingA": {
        "name_eng": "Building A Access Ramp",
        "notes_spa": "Rampa de entrada principal con pendiente suave.",
        "notes_eng": "Main entrance ramp with gentle slope.",
    },
    "rampBuildingB": {
        "name_eng": "Building B Access Ramp",
        "notes_spa": "Rampa de acceso en el pasillo oeste.",
        "notes_eng": "Western hallway entrance ramp.",
    },
    "rampBuildingG": {
        "name_eng": "Building G Central Auditorium Ramp",
        "notes_spa": "Rampa de acceso directo al vestíbulo de planta baja del Edificio G.",
        "notes_eng": "Direct access ramp to Building G ground lobby.",
    },
    "rampJaguarCenter": {
        "name_eng": "Jaguar Center Access Ramp",
        "notes_spa": "Rampa principal de acceso al complejo deportivo.",
        "notes_eng": "Main entrance sports center ramp.",
    },

    # --- SUPPLEMENTARY BUILDING A-P & SPORTS CATALOG ENTRIES ---
    "financialDirectorateA": {
        "name_eng": "Finance Directorate",
        "notes_spa": "Edificio A, Piso 1.",
        "notes_eng": "Building A, Floor 1.",
    },
    "academicLogisticsA": {
        "name_eng": "Academic Logistics",
        "notes_spa": "Edificio A, Piso 2.",
        "notes_eng": "Building A, Floor 2.",
    },
    "talentDirectorateA": {
        "name_eng": "Talent Management Directorate",
        "notes_spa": "Edificio A, Piso 2.",
        "notes_eng": "Building A, Floor 2.",
    },
    "cycloramaSetA": {
        "name_eng": "Cyclorama Recording Set",
        "notes_spa": "Edificio A, Piso 3 (DPA).",
        "notes_eng": "Building A, Floor 3 (DPA).",
    },
    "soundStudioA": {
        "name_eng": "Sound Studio",
        "notes_spa": "Edificio A, Piso 3 (DPA).",
        "notes_eng": "Building A, Floor 3 (DPA).",
    },
    "dpaAuxOfficesA": {
        "name_eng": "DPA Auxiliary Offices",
        "notes_spa": "Edificio A, Piso 3 (DPA).",
        "notes_eng": "Building A, Floor 3 (DPA).",
    },
    "masterControlA": {
        "name_eng": "Master Control",
        "notes_spa": "Edificio A, Piso 3 (DPA).",
        "notes_eng": "Building A, Floor 3 (DPA).",
    },
    "radioSetA": {
        "name_eng": "Radio Set",
        "notes_spa": "Edificio A, Piso 3 (DPA).",
        "notes_eng": "Building A, Floor 3 (DPA).",
    },
    "restroomsMenE": {
        "name_eng": "Men's Restrooms (Building E)",
        "notes_spa": "Edificio E, Piso 1.",
        "notes_eng": "Building E, Floor 1.",
    },
    "restroomsWomenE": {
        "name_eng": "Women's Restrooms (Building E)",
        "notes_spa": "Edificio E, Piso 1.",
        "notes_eng": "Building E, Floor 1.",
    },
    "benchesE": {
        "name_eng": "Seating Benches (Building E)",
        "notes_spa": "Edificio E, Piso 1, área de descanso.",
        "notes_eng": "Building E, Floor 1, seating area.",
    },
    "medicalSimulatorsWardE2": {
        "name_eng": "Medical Simulators Lab (Pediatrics, Neonatology & Control Rooms)",
        "notes_spa": "Edificio E, Piso 2, Pediatría, Neonatología, Salas de Control 1 y 2, Cuidados Médicos.",
        "notes_eng": "Building E, Floor 2, Pediatrics, Neonatology, Control Rooms 1 & 2, Medical Care.",
    },
    "intlRelationsG": {
        "name_eng": "International Relations & Internationalization Directorate",
        "notes_spa": "Edificio G, Piso 1.",
        "notes_eng": "Building G, Floor 1.",
    },
    "mixedRestroomG": {
        "name_eng": "All-Gender Restrooms (Building G)",
        "notes_spa": "Edificio G, Piso 1.",
        "notes_eng": "Building G, Floor 1.",
    },
    "restroomsMenH1": {
        "name_eng": "Men's Restrooms (Building H)",
        "notes_spa": "Edificio H, Piso 1.",
        "notes_eng": "Building H, Floor 1.",
    },
    "restroomsWomenH1": {
        "name_eng": "Women's Restrooms (Building H)",
        "notes_spa": "Edificio H, Piso 1.",
        "notes_eng": "Building H, Floor 1.",
    },
    "foodScienceLabH": {
        "name_eng": "Food Science Lab",
        "notes_spa": "Edificio H, Piso 1.",
        "notes_eng": "Building H, Floor 1.",
    },
    "vicePresidencyI": {
        "name_eng": "Vice Presidency & UAM Map",
        "notes_spa": "Edificio I, Piso 1.",
        "notes_eng": "Building I, Floor 1.",
    },
    "directorsMeetingRoomI": {
        "name_eng": "Directors' Meeting Room",
        "notes_spa": "Edificio I, Piso 1.",
        "notes_eng": "Building I, Floor 1.",
    },
    "academicDirectorateI": {
        "name_eng": "Academic Directorate (Building I)",
        "notes_spa": "Edificio I, Piso 1.",
        "notes_eng": "Building I, Floor 1.",
    },
    "generalManagementI": {
        "name_eng": "General Management",
        "notes_spa": "Edificio I, Piso 1.",
        "notes_eng": "Building I, Floor 1.",
    },
    "generalSecretariatI": {
        "name_eng": "General Secretariat",
        "notes_spa": "Edificio I, Piso 1.",
        "notes_eng": "Building I, Floor 1.",
    },
    "meetingRoomI": {
        "name_eng": "Office / Meeting Room (Building I)",
        "notes_spa": "Edificio I, Piso 1.",
        "notes_eng": "Building I, Floor 1.",
    },
    "restroomsLibraryMenI": {
        "name_eng": "Library Men's Restrooms",
        "notes_spa": "Edificio I, Biblioteca, izquierda hombres.",
        "notes_eng": "Building I, Library, men's on the left.",
    },
    "restroomsLibraryWomenI": {
        "name_eng": "Library Women's Restrooms",
        "notes_spa": "Edificio I, Biblioteca, derecha mujeres.",
        "notes_eng": "Building I, Library, women's on the right.",
    },
    "publicRelationsI": {
        "name_eng": "Public Relations Directorate",
        "notes_spa": "Edificio I, Piso 1.",
        "notes_eng": "Building I, Floor 1.",
    },
    "presidencyI": {
        "name_eng": "UAM Presidency",
        "notes_spa": "Edificio I, Piso 1.",
        "notes_eng": "Building I, Floor 1.",
    },
    "uamMapJ": {
        "name_eng": "UAM Map (Building J)",
        "notes_spa": "Edificio J, mapa físico de la universidad.",
        "notes_eng": "Building J, physical campus map directory.",
    },
    "restroomsMenK1": {
        "name_eng": "Men's Restrooms (Building K)",
        "notes_spa": "Edificio K, Piso 1.",
        "notes_eng": "Building K, Floor 1.",
    },
    "restroomsWomenK1": {
        "name_eng": "Women's Restrooms (Building K)",
        "notes_spa": "Edificio K, Piso 1.",
        "notes_eng": "Building K, Floor 1.",
    },
    "tablesAreaK1": {
        "name_eng": "Seating Area (Building K - Floor 1)",
        "notes_spa": "Edificio K, Piso 1.",
        "notes_eng": "Building K, Floor 1.",
    },
    "jaguarShopK": {
        "name_eng": "Jaguar Shop (Building K)",
        "notes_spa": "Edificio K, Piso 1.",
        "notes_eng": "Building K, Floor 1.",
    },
    "kiosk1K1": {
        "name_eng": "Kiosk 1 (Building K - Floor 1)",
        "notes_spa": "Edificio K, Piso 1.",
        "notes_eng": "Building K, Floor 1.",
    },
    "kiosk1K2": {
        "name_eng": "Kiosk 1 (Building K - Floor 2)",
        "notes_spa": "Edificio K, Piso 2.",
        "notes_eng": "Building K, Floor 2.",
    },
    "kiosk2K2": {
        "name_eng": "Kiosk 2 (Building K - Floor 2)",
        "notes_spa": "Edificio K, Piso 2.",
        "notes_eng": "Building K, Floor 2.",
    },
    "tablesAreaK2": {
        "name_eng": "Seating Area (Building K - Floor 2)",
        "notes_spa": "Edificio K, Piso 2.",
        "notes_eng": "Building K, Floor 2.",
    },
    "showersVisitorsL": {
        "name_eng": "Visiting Team Showers (Building L)",
        "notes_spa": "Edificio L, Planta Única (derecha).",
        "notes_eng": "Building L, Floor 1 (right side).",
    },
    "showersHomeL": {
        "name_eng": "Home Team Showers (Building L)",
        "notes_spa": "Edificio L, Planta Única (izquierda).",
        "notes_eng": "Building L, Floor 1 (left side).",
    },
    "restroomsMenL": {
        "name_eng": "Men's Restrooms (Building L)",
        "notes_spa": "Edificio L, Planta Única.",
        "notes_eng": "Building L, Floor 1.",
    },
    "restroomsWomenL": {
        "name_eng": "Women's Restrooms (Building L)",
        "notes_spa": "Edificio L, Planta Única.",
        "notes_eng": "Building L, Floor 1.",
    },
    "classroomM1": {
        "name_eng": "Classroom (Building M - Floor 1)",
        "notes_spa": "Edificio M, Piso 1.",
        "notes_eng": "Building M, Floor 1.",
    },
    "restroomsMenM1": {
        "name_eng": "Men's Restrooms (Building M)",
        "notes_spa": "Edificio M, Piso 1.",
        "notes_eng": "Building M, Floor 1.",
    },
    "restroomsWomenM1": {
        "name_eng": "Women's Restrooms (Building M)",
        "notes_spa": "Edificio M, Piso 1.",
        "notes_eng": "Building M, Floor 1.",
    },
    "accessibleRestroomM1": {
        "name_eng": "Inclusive Accessible Restrooms (Building M)",
        "notes_spa": "Edificio M, Piso 1.",
        "notes_eng": "Building M, Floor 1.",
    },
    "restroomsMenN1": {
        "name_eng": "Men's Restrooms (Building N - next to Chilamates Plaza)",
        "notes_spa": "Edificio N, Piso 1, junto a Plaza Chilamates.",
        "notes_eng": "Building N, Floor 1, next to Chilamates Plaza.",
    },
    "restroomsWomenN1": {
        "name_eng": "Women's Restrooms (Building N - next to Chilamates Plaza)",
        "notes_spa": "Edificio N, Piso 1, junto a Plaza Chilamates.",
        "notes_eng": "Building N, Floor 1, next to Chilamates Plaza.",
    },
    "drinkingFountainP1West": {
        "name_eng": "Drinking Fountain (Building P - Floor 1 West)",
        "notes_spa": "Edificio P, Piso 1, entre P108 y baños.",
        "notes_eng": "Building P, Floor 1, between P108 and restrooms.",
    },
    "restroomsMenP1": {
        "name_eng": "Men's Restrooms (Building P - Floor 1)",
        "notes_spa": "Edificio P, Piso 1 (izquierda).",
        "notes_eng": "Building P, Floor 1 (left side).",
    },
    "restroomsWomenP1": {
        "name_eng": "Women's Restrooms (Building P - Floor 1)",
        "notes_spa": "Edificio P, Piso 1 (derecha).",
        "notes_eng": "Building P, Floor 1 (right side).",
    },
    "restroomsMenP2": {
        "name_eng": "Men's Restrooms (Building P - Floor 2)",
        "notes_spa": "Edificio P, Piso 2.",
        "notes_eng": "Building P, Floor 2.",
    },
    "restroomsWomenP2": {
        "name_eng": "Women's Restrooms (Building P - Floor 2)",
        "notes_spa": "Edificio P, Piso 2.",
        "notes_eng": "Building P, Floor 2.",
    },
    "drinkingFountainP3West": {
        "name_eng": "Drinking Fountain (Building P - Floor 3 West)",
        "notes_spa": "Edificio P, Piso 3, entre P308 y baños.",
        "notes_eng": "Building P, Floor 3, between P308 and restrooms.",
    },
    "restroomsMenP3": {
        "name_eng": "Men's Restrooms (Building P - Floor 3)",
        "notes_spa": "Edificio P, Piso 3.",
        "notes_eng": "Building P, Floor 3.",
    },
    "restroomsWomenP3": {
        "name_eng": "Women's Restrooms (Building P - Floor 3)",
        "notes_spa": "Edificio P, Piso 3.",
        "notes_eng": "Building P, Floor 3.",
    },
    "restroomsMenSZ": {
        "name_eng": "Men's Restrooms (Sports Fields)",
        "notes_spa": "Campos Deportivos, junto a Kiosko Jaguarcito.",
        "notes_eng": "Sports Fields, next to Jaguarcito Kiosk.",
    },
    "restroomsWomenSZ": {
        "name_eng": "Women's Restrooms (Sports Fields)",
        "notes_spa": "Campos Deportivos, junto a Kiosko Jaguarcito.",
        "notes_eng": "Sports Fields, next to Jaguarcito Kiosk.",
    },
    "kioskJaguarcitoSZ": {
        "name_eng": "Jaguarcito Kiosk",
        "notes_spa": "Campos Deportivos.",
        "notes_eng": "Sports Fields.",
    },
    "sportsOfficesSZ": {
        "name_eng": "Sports Offices",
        "notes_spa": "Campos Deportivos / Complejo Deportivo.",
        "notes_eng": "Sports Fields / Sports Complex.",
    },
    "sportsWarehouseSZ": {
        "name_eng": "Sports Equipment Storage",
        "notes_spa": "Campos Deportivos.",
        "notes_eng": "Sports Fields.",
    },
    "martialArtsHallJC": {
        "name_eng": "Martial Arts Hall",
        "notes_spa": "Complejo Deportivo Jaguar Center.",
        "notes_eng": "Jaguar Center Sports Complex.",
    },
    "multipurposeHallJC": {
        "name_eng": "Multipurpose Hall - DVE",
        "notes_spa": "Complejo Deportivo Jaguar Center.",
        "notes_eng": "Jaguar Center Sports Complex.",
    },
    "beachVolleyballJC": {
        "name_eng": "Beach Volleyball Court (Jaguar Center)",
        "notes_spa": "Complejo Deportivo Jaguar Center.",
        "notes_eng": "Jaguar Center Sports Complex.",
    },
    "kioskJaguarSportJC": {
        "name_eng": "Jaguar Sport Kiosk",
        "notes_spa": "Complejo Deportivo Jaguar Center.",
        "notes_eng": "Jaguar Center Sports Complex.",
    },
    "sportsPsychJC": {
        "name_eng": "Sports Psychology Office",
        "notes_spa": "Complejo Deportivo Jaguar Center.",
        "notes_eng": "Jaguar Center Sports Complex.",
    },
    "generalWarehouseJC": {
        "name_eng": "General Warehouse & Containers",
        "notes_spa": "Sector Bodega General y Contenedores.",
        "notes_eng": "General Warehouse & Containers area.",
    },
    "sportsOfficesJC": {
        "name_eng": "Sports Offices 1-3",
        "notes_spa": "Sector Bodega General y Complejo Jaguar Center.",
        "notes_eng": "General Warehouse & Jaguar Center Sports Complex area.",
    },
    "staffDiningJC": {
        "name_eng": "Staff Dining Hall",
        "notes_spa": "Sector Bodega General y Complejo Jaguar Center.",
        "notes_eng": "General Warehouse & Jaguar Center Sports Complex area.",
    },
}


# =============================================================================
# 3. INDOOR SUBGRAPH NODE TRANSLATIONS (ALL 333 NODES — (SPA, ENG))
# =============================================================================
INDOOR_NODE_TRANSLATIONS: Dict[str, Tuple[str, str]] = {
    # --- Building A (24) ---
    "a_contabilidad_101": ("Contabilidad (A101)", "Accounting (A101)"),
    "a_cae_lobby": ("Centro de Atención al Estudiante (CAE) / Zona Común", "Student Care Center (CAE) / Common Area"),
    "a_mercadeo_admision": ("Dirección de Mercadeo y Admisión", "Admissions & Marketing Directorate"),
    "a_registro_academico": ("Registro Académico", "Academic Records"),
    "a_cartera_cobro": ("Cartera y Cobro", "Collections Office"),
    "a_direccion_academica": ("Dirección Académica (Edificio A)", "Academic Directorate (Building A)"),
    "a_direccion_financiera": ("Dirección Financiera", "Finance Directorate"),
    "a_reception_lost_found": ("Objetos Perdidos (JaguarFind) y Recepción", "Lost & Found (JaguarFind) & Reception"),
    "a_atm_map": ("Cajeros Automáticos (BAC y LAFISE) y Mapa UAM", "ATMs (BAC & LAFISE) & UAM Map"),
    "a_stairs_f1": ("Escaleras Edificio A (conexión con Edificio C - Piso 1)", "Building A Stairs (connection to Building C - Floor 1)"),
    "a_admin_201": ("Dirección Administrativa (A201)", "Administrative Directorate (A201)"),
    "a_logistica_academica": ("Logística Académica", "Academic Logistics"),
    "a_tic_203": ("Dirección Tecnología de la Información y Comunicación - TIC (A203)", "Information & Communications Technology Directorate - IT/TIC (A203)"),
    "a_marketing_204": ("Mercadeo y Publicidad (A204)", "Marketing & Advertising (A204)"),
    "a_gestion_talento": ("Dirección de Gestión del Talento", "Talent Management Directorate"),
    "a_hr_205": ("Recursos Humanos (A205)", "Human Resources (A205)"),
    "a_stairs_f2": ("Escaleras Edificio A (Piso 2)", "Building A Stairs (Floor 2)"),
    "a_dpa_301": ("Dirección de Producción Audiovisual (DPA / A301)", "Audiovisual Production Directorate (DPA / A301)"),
    "a_ciclograma": ("Set de Grabación Ciclograma", "Cyclorama Recording Set"),
    "a_estudio_sonido": ("Estudio de Sonido", "Sound Studio"),
    "a_oficinas_dpa": ("Oficinas Auxiliares DPA", "DPA Auxiliary Offices"),
    "a_control_master": ("Control Máster", "Master Control"),
    "a_set_radio": ("Set de Radio", "Radio Set"),
    "a_stairs_f3": ("Escaleras Edificio A (Piso 3)", "Building A Stairs (Floor 3)"),

    # --- Building B (27) ---
    "b_pharmacy": ("Módulo Comercial 1 (Farmacia)", "Commercial Module 1 (Pharmacy)"),
    "b_room_101": ("Aula B101", "Classroom B101"),
    "b_room_102": ("Aula B102", "Classroom B102"),
    "b_room_103": ("Aula B103", "Classroom B103"),
    "b_room_104": ("Aula B104", "Classroom B104"),
    "b_room_105": ("Aula B105", "Classroom B105"),
    "b_room_106": ("Aula B106", "Classroom B106"),
    "b_room_107": ("Aula B107", "Classroom B107"),
    "b_room_108": ("Aula B108", "Classroom B108"),
    "b_room_109": ("Aula B109", "Classroom B109"),
    "b_restrooms_men_f1": ("Servicios Sanitarios Hombres (Edificio B)", "Men's Restrooms (Building B)"),
    "b_fountain_f1": ("Bebedero de Agua (Edificio B)", "Drinking Fountain (Building B)"),
    "b_restrooms_women_f1": ("Servicios Sanitarios Mujeres (Edificio B)", "Women's Restrooms (Building B)"),
    "b_photocopy": ("Fotocopias (Edificio B)", "Photocopy Shop (Building B)"),
    "b_fountain_bc": ("Bebedero de Agua (Entre Edificio C y B)", "Drinking Fountain (Between Building C & B)"),
    "b_stairs_f1": ("Escaleras al Segundo Piso (Edificio B - Piso 1)", "Stairs to Floor 2 (Building B - Floor 1)"),
    "b_room_201": ("Aula B201", "Classroom B201"),
    "b_room_202": ("Aula B202", "Classroom B202"),
    "b_room_203": ("Aula B203", "Classroom B203"),
    "b_room_204": ("Aula B204", "Classroom B204"),
    "b_room_205": ("Aula B205", "Classroom B205"),
    "b_room_206": ("Aula B206", "Classroom B206"),
    "b_room_207": ("Aula B207", "Classroom B207"),
    "b_room_208": ("Aula B208", "Classroom B208"),
    "b_room_209": ("Aula B209", "Classroom B209"),
    "b_room_210": ("Aula B210", "Classroom B210"),
    "b_stairs_f2": ("Escaleras del Segundo Piso (Edificio B)", "Floor 2 Stairs (Building B)"),

    # --- Building C (42) ---
    "c_auditorium_101": ("Auditorio C101", "Auditorium C101"),
    "c_room_102": ("Aula C102", "Classroom C102"),
    "c_room_103": ("Aula C103", "Classroom C103"),
    "c_room_104": ("Aula C104", "Classroom C104"),
    "c_treasury_105": ("Tesorería UAM (C105)", "UAM Treasury (C105)"),
    "c_fountain_f1": ("Bebedero de Agua (Edificio C - Piso 1)", "Drinking Fountain (Building C - Floor 1)"),
    "c_cashier": ("Caja UAM / Tesorería", "UAM Cashier / Treasury"),
    "c_room_106": ("Aula C106", "Classroom C106"),
    "c_lab_mac_107": ("Laboratorio MAC C107", "MAC Lab C107"),
    "c_lab_acai_108": ("Laboratorio de Computación ACAI-Erasmus+ (C108)", "ACAI-Erasmus+ Computer Lab (C108)"),
    "c_auditorium_109": ("Auditorio C109", "Auditorium C109"),
    "c_mapa_uam_f1": ("Mapa UAM (Entrada Edificio C)", "UAM Map (Building C Entrance)"),
    "c_ramp_f1": ("Rampa Accesible Edificio C", "Building C Accessible Ramp"),
    "c_stairs_left_f1": ("Escaleras Izquierda Edificio C (Piso 1)", "Building C Left Stairs (Floor 1)"),
    "c_stairs_right_f1": ("Escaleras Derecha Edificio C (Piso 1)", "Building C Right Stairs (Floor 1)"),
    "c_lab_201": ("Laboratorio de Computación C201", "Computer Lab C201"),
    "c_lab_202": ("Laboratorio de Computación C202", "Computer Lab C202"),
    "c_lab_mac_203": ("Laboratorio MAC C203", "MAC Lab C203"),
    "c_lab_204": ("Laboratorio de Computación C204", "Computer Lab C204"),
    "c_fountain_f2": ("Bebedero de Agua (Edificio C - Piso 2)", "Drinking Fountain (Building C - Floor 2)"),
    "c_lab_205": ("Laboratorio de Computación C205", "Computer Lab C205"),
    "c_warehouse_206": ("Bodega de Logística Académica (C206)", "Academic Logistics Storage (C206)"),
    "c_restrooms_men": ("Servicios Sanitarios Hombres (Edificio C - Piso 2)", "Men's Restrooms (Building C - Floor 2)"),
    "c_restrooms_women": ("Servicios Sanitarios Mujeres (Edificio C - Piso 2)", "Women's Restrooms (Building C - Floor 2)"),
    "c_room_209": ("Aula C209", "Classroom C209"),
    "c_room_210": ("Aula C210", "Classroom C210"),
    "c_room_211": ("Aula C211", "Classroom C211"),
    "c_mapa_uam_f2": ("Mapa UAM (Edificio C - Piso 2)", "UAM Map (Building C - Floor 2)"),
    "c_stairs_left_f2": ("Escaleras Izquierda Edificio C (Piso 2)", "Building C Left Stairs (Floor 2)"),
    "c_stairs_right_f2": ("Escaleras Derecha Edificio C (Piso 2)", "Building C Right Stairs (Floor 2)"),
    "c_room_301": ("Aula C301", "Classroom C301"),
    "c_room_302": ("Aula C302", "Classroom C302"),
    "c_room_303": ("Aula C303", "Classroom C303"),
    "c_room_304": ("Aula C304", "Classroom C304"),
    "c_room_305": ("Aula C305", "Classroom C305"),
    "c_compras_306": ("Coordinación de Compras (C306)", "Procurement Coordination (C306)"),
    "c_room_307": ("Aula C307", "Classroom C307"),
    "c_room_308": ("Aula C308", "Classroom C308"),
    "c_room_309": ("Aula C309", "Classroom C309"),
    "c_room_310": ("Aula C310", "Classroom C310"),
    "c_stairs_ac_f3": ("Escaleras de Conexión Edificios A y C (Piso 3)", "Building A & C Connecting Stairs (Floor 3)"),
    "c_stairs_right_f3": ("Escaleras Derecha Edificio C (Piso 3)", "Building C Right Stairs (Floor 3)"),

    # --- Building D (5) ---
    "d_room_102": ("Aula D102", "Classroom D102"),
    "d_lab_cam_cam": ("Laboratorio de Odontología Digital CAM-CAM", "CAM-CAM Digital Dentistry Lab"),
    "d_customer_service": ("Oficina de Servicio al Cliente", "Customer Service Office"),
    "d_meeting_room": ("Sala de Reunión (Edificio D)", "Meeting Room (Building D)"),
    "d_uam_map": ("Mapa UAM (Entrada Edificio D)", "UAM Map (Building D Entrance)"),

    # --- Building E (22) ---
    "e_clinica_medica": ("Clínicas Médicas", "Medical Clinics"),
    "e_restrooms_men_f1": ("Servicios Sanitarios Hombres (Edificio E)", "Men's Restrooms (Building E)"),
    "e_restrooms_women_f1": ("Servicios Sanitarios Mujeres (Edificio E)", "Women's Restrooms (Building E)"),
    "e_restrooms_f1": ("Servicios Sanitarios Personas con Discapacidades Mixtos (Edificio E)", "Inclusive Accessible Restrooms (Building E)"),
    "e_cardiology": ("Centro de Cardiología", "Cardiology Center"),
    "e_faculty_medicine": ("Facultad de Ciencias Médicas", "Faculty of Medical Sciences"),
    "e_vida_estudiantil": ("Dirección de Vida Estudiantil (Anexo Oeste)", "Student Life Directorate (West Annex)"),
    "e_die_innovation": ("Dirección de Innovación y Emprendimientos (DIE) (Anexo Norte)", "Innovation & Entrepreneurship Directorate (DIE) (North Annex)"),
    "e_bancas": ("Bancas (Edificio E)", "Seating Benches (Building E)"),
    "e_consultorio_pediatria": ("Consultorio de Pediatría / Lab de Medicina", "Pediatrics Clinic / Medical Lab"),
    "e_fountain_f1": ("Bebedero de Agua (Edificio E)", "Drinking Fountain (Building E)"),
    "e_ramp_f1": ("Rampa Accesible hacia Edificio E", "Accessible Ramp to Building E"),
    "e_mapa_uam_north": ("Mapa UAM (Acceso Norte Edificio E)", "UAM Map (Building E North Entrance)"),
    "e_mapa_uam_south": ("Mapa UAM (Pasillo Facultad de Medicina)", "UAM Map (Faculty of Medicine Hallway)"),
    "e_stairs_left_f1": ("Escaleras Izquierda Edificio E (Piso 1)", "Building E Left Stairs (Floor 1)"),
    "e_stairs_south_f1": ("Escaleras Sur Edificio E (Piso 1)", "Building E South Stairs (Floor 1)"),
    "e_sim_center_201": ("Laboratorio Simuladores de Habilidades Medicina (E201)", "Medical Clinical Skills Simulators Lab (E201)"),
    "e_pediatrics_control": ("Laboratorio Simuladores de Medicina (Pediatría, Neonatología y Salas de Control)", "Medical Simulators Lab (Pediatrics, Neonatology & Control Rooms)"),
    "e_psychology": ("Oficina Psicología", "Psychology Office"),
    "e_lab_clinico": ("Laboratorio Clínico de Medicina", "Clinical Medicine Lab"),
    "e_stairs_left_f2": ("Escaleras Izquierda Edificio E (Piso 2)", "Building E Left Stairs (Floor 2)"),
    "e_stairs_south_f2": ("Escaleras Sur Edificio E (Piso 2)", "Building E South Stairs (Floor 2)"),

    # --- Building F (8) ---
    "f_teachers_lounge": ("Salón de Profesores (Edificio F)", "Faculty Lounge (Building F)"),
    "f_posgrados": ("Dirección de Posgrados y Educación Continua", "Postgraduate & Continuing Education Directorate"),
    "f_fcae": ("Facultad de Ciencias Administrativas y Económicas (FCAE)", "Faculty of Administrative & Economic Sciences (FCAE)"),
    "f_fmdcc": ("Facultad de Marketing, Diseño y Ciencias de la Comunicación (FMDCC)", "Faculty of Marketing, Design & Communication (FMDCC)"),
    "f_ramp_teachers_map": ("Escaleras, Rampa al Salón de Profesores y Mapa UAM (Edificio F)", "Stairs, Ramp to Faculty Lounge & UAM Map (Building F)"),
    "f_ramp_to_i": ("Escaleras y Rampa hacia Edificio I", "Stairs & Ramp to Building I"),
    "f_ramp_fcae": ("Rampa Accesible FCAE", "FCAE Accessible Ramp"),
    "f_vida_estudiantil_link": ("Paso hacia Dirección de Vida Estudiantil", "Walkway to Student Life Directorate"),

    # --- Building G (12) ---
    "g_fcjhri": ("Facultad de Ciencias Jurídicas, Humanidades y Relaciones Internacionales (FCJHRI)", "Faculty of Legal Sciences, Humanities & International Relations (FCJHRI)"),
    "g_auditorium_fcjhri": ("Auditorio FCJHRI", "FCJHRI Auditorium"),
    "g_mediation_center": ("Centro de Mediación y Arbitraje", "Mediation & Arbitration Center"),
    "g_language_center": ("Language Center", "UAM Language Center"),
    "g_uam_college": ("UAM College", "UAM College"),
    "g_intl_relations": ("Dirección de Relaciones Internacionales e Internacionalización", "International Relations & Internationalization Directorate"),
    "g_restrooms_mixed": ("Baños Mixtos (Edificio G)", "All-Gender Restrooms (Building G)"),
    "g_restrooms_f1": ("Baños para Personas con Discapacidades Mixtos (Edificio G)", "Inclusive Accessible Restrooms (Building G)"),
    "g_stairs_f1": ("Escaleras Edificio G (Piso 1)", "Building G Stairs (Floor 1)"),
    "g_ramp_gf_auditorium": ("Escaleras y Rampa entre G y F (Acceso Auditorio Central)", "Stairs & Ramp between Building G & F (Central Auditorium Access)"),
    "g_auditorium_central": ("Auditorio Central / Auditorio Rubén Darío", "Central Auditorium / Rubén Darío Auditorium"),
    "g_stairs_f2": ("Escaleras Edificio G (Piso 2)", "Building G Stairs (Floor 2)"),

    # --- Building H (21) ---
    "h_restrooms_men_f1": ("Baños Hombres (Edificio H)", "Men's Restrooms (Building H)"),
    "h_restrooms_women_f1": ("Baños Mujeres (Edificio H)", "Women's Restrooms (Building H)"),
    "h_lab_101": ("Laboratorio de Medicina H101", "Medical Lab H101"),
    "h_lab_102": ("Laboratorio de Medicina H102", "Medical Lab H102"),
    "h_lab_103": ("Laboratorio de Medicina H103", "Medical Lab H103"),
    "h_lab_104": ("Coordinación de Gestión de Calidad (Laboratorio H104)", "Quality Management Coordination (Lab H104)"),
    "h_lab_coord_necroteca": ("Oficina de Supervisión de Laboratorios de Medicina (Necroteca)", "Medical Labs Supervision Office (Anatomy Lab)"),
    "h_lab_105": ("Laboratorio de Medicina H105", "Medical Lab H105"),
    "h_lab_106": ("Laboratorio de Medicina H106", "Medical Lab H106"),
    "h_lab_107": ("Laboratorio de Medicina H107", "Medical Lab H107"),
    "h_food_science_lab": ("Laboratorio de Ciencias de los Alimentos", "Food Science Lab"),
    "h_stairs_from_c": ("Acceso y Escaleras al Edificio H (lado C)", "Building H Entrance & Stairs (Building C side)"),
    "h_stairs_main_f1": ("Escaleras Principales Edificio H (Piso 1)", "Building H Main Stairs (Floor 1)"),
    "h_lab_201": ("Laboratorio de Medicina H201", "Medical Lab H201"),
    "h_lab_202": ("Laboratorio de Medicina H202", "Medical Lab H202"),
    "h_lab_203": ("Laboratorio de Medicina H203", "Medical Lab H203"),
    "h_lab_204": ("Laboratorio de Medicina H204", "Medical Lab H204"),
    "h_lab_205": ("Laboratorio de Medicina H205", "Medical Lab H205"),
    "h_lab_206": ("Laboratorio de Medicina H206", "Medical Lab H206"),
    "h_lab_207": ("Laboratorio de Medicina H207", "Medical Lab H207"),
    "h_stairs_main_f2": ("Escaleras Principales Edificio H (Piso 2)", "Building H Main Stairs (Floor 2)"),

    # --- Building I (21) ---
    "i_vicepresidencia": ("Vicepresidencia y Mapa UAM", "Vice Presidency & UAM Map"),
    "i_sala_directores": ("Sala de Reunión Directores", "Directors' Meeting Room"),
    "i_dir_academica": ("Dirección Académica (Edificio I)", "Academic Directorate (Building I)"),
    "i_rectoria": ("Rectoría", "Rectorate"),
    "i_gerencia_general": ("Gerencia General", "General Management"),
    "i_secretaria_general": ("Secretaría General", "General Secretariat"),
    "i_oficina_reunion": ("Oficina / Sala de Reunión (Edificio I)", "Office / Meeting Room (Building I)"),
    "i_biblioteca": ("Biblioteca Pablo Antonio Cuadra", "Pablo Antonio Cuadra Library"),
    "i_restrooms_lib_men": ("Baños Biblioteca Hombres", "Library Men's Restrooms"),
    "i_restrooms_lib_women": ("Baños Biblioteca Mujeres", "Library Women's Restrooms"),
    "i_relaciones_publicas": ("Dirección de Relaciones Públicas", "Public Relations Directorate"),
    "i_presidencia": ("Presidencia UAM", "UAM Presidency"),
    "i_fountain": ("Bebedero de Agua (Edificio I)", "Drinking Fountain (Building I)"),
    "i_mapa_uam": ("Mapa UAM (Edificio I)", "UAM Map (Building I)"),
    "i_ramp_jaguar_start": ("Inicio Rampa hacia Edificio I (camino Jaguar Center)", "Start of Building I Ramp (Jaguar Center path)"),
    "i_ramp_street": ("Rampa de la Calle hacia Edificio I", "Street Ramp to Building I"),
    "i_ramp_sidewalk_lib": ("Paso de Rampa hacia Acera de Biblioteca", "Ramp Path to Library Sidewalk"),
    "i_ramp_end": ("Fin de Rampa Edificio I (Pasillo Principal)", "End of Building I Ramp (Main Hallway)"),
    "i_stairs_lib_street": ("Escaleras de la Calle a Biblioteca Central", "Street Stairs to Central Library"),
    "i_stairs_lib_front": ("Escaleras frente a Puerta de Biblioteca", "Stairs in front of Library Door"),
    "i_ramp_lib": ("Rampa Accesible de Biblioteca Central", "Central Library Accessible Ramp"),

    # --- Building J (6) ---
    "j_lab_101": ("Laboratorio de Odontología J101", "Dental Lab J101"),
    "j_lab_102": ("Laboratorio de Odontología J102", "Dental Lab J102"),
    "j_restrooms_men": ("Baños Hombres (Edificio J)", "Men's Restrooms (Building J)"),
    "j_restrooms_women": ("Baños Mujeres (Edificio J)", "Women's Restrooms (Building J)"),
    "j_uam_map": ("Mapa UAM (Edificio J)", "UAM Map (Building J)"),
    "j_entrance": ("Entrada Principal Edificio J", "Building J Main Entrance"),

    # --- Building K (13) ---
    "k_restrooms_men_f1": ("Baños Hombres (Edificio K)", "Men's Restrooms (Building K)"),
    "k_restrooms_women_f1": ("Baños Mujeres (Edificio K)", "Women's Restrooms (Building K)"),
    "k_tables_f1": ("Área de Mesas (Edificio K - Piso 1)", "Seating Area (Building K - Floor 1)"),
    "k_terraces_tables": ("Terrazas (Edificio K)", "Terraces (Building K)"),
    "k_jaguar_shop": ("Jaguar Shop (Edificio K)", "Jaguar Shop (Building K)"),
    "k_food_court": ("Módulos Comerciales (Food Court)", "Commercial Modules (Food Court)"),
    "k_kiosk1_f1": ("Kiosko 1 (Edificio K - Piso 1)", "Kiosk 1 (Building K - Floor 1)"),
    "k_entrance_banpro": ("Acceso Edificio K (junto a Banpro)", "Building K Entrance (next to Banpro)"),
    "k_stairs_f1": ("Escaleras hacia Piso 2 (Edificio K - Piso 1)", "Stairs to Floor 2 (Building K - Floor 1)"),
    "k_kiosk1_f2": ("Kiosko 1 (Edificio K - Piso 2)", "Kiosk 1 (Building K - Floor 2)"),
    "k_kiosk2_f2": ("Kiosko 2 (Edificio K - Piso 2)", "Kiosk 2 (Building K - Floor 2)"),
    "k_tables_f2": ("Área de Mesas (Edificio K - Piso 2)", "Seating Area (Building K - Floor 2)"),
    "k_stairs_f2": ("Escaleras Edificio K (Piso 2)", "Building K Stairs (Floor 2)"),

    # --- Building L (7) ---
    "l_duchas_visitantes": ("Duchas Visitantes (Edificio L)", "Visiting Team Showers (Building L)"),
    "l_duchas_home": ("Duchas Home (Edificio L)", "Home Team Showers (Building L)"),
    "l_cultura_map": ("Salón de Cultura y Mapa UAM (Edificio L)", "Culture Hall & UAM Map (Building L)"),
    "l_musica": ("Aula de Música (Edificio L)", "Music Classroom (Building L)"),
    "l_restrooms_men": ("Baños Hombres (Edificio L)", "Men's Restrooms (Building L)"),
    "l_restrooms_women": ("Baños Mujeres (Edificio L)", "Women's Restrooms (Building L)"),
    "l_jaguar_center_entry": ("Entrada a Jaguar Center por Edificio L", "Jaguar Center Entrance via Building L"),

    # --- Building M (21) ---
    "m_auditorium_101": ("Auditorio M101", "Auditorium M101"),
    "m_auditorium_102": ("Auditorio M102", "Auditorium M102"),
    "m_env_directorate": ("Dirección de Gestión Ambiental y Energética", "Environmental & Energy Management Directorate"),
    "m_research_extension": ("Dirección Investigación y Extensión Universitaria", "Research & University Extension Directorate"),
    "m_classroom_f1": ("Aula (Edificio M - Piso 1)", "Classroom (Building M - Floor 1)"),
    "m_restrooms_men": ("Baños Hombres (Edificio M)", "Men's Restrooms (Building M)"),
    "m_restrooms_women": ("Baños Mujeres (Edificio M)", "Women's Restrooms (Building M)"),
    "m_restrooms_accessible": ("Servicios Mixtos Discapacitados (Edificio M)", "Inclusive Accessible Restrooms (Building M)"),
    "m_fountain_f1": ("Bebedero de Agua (Edificio M)", "Drinking Fountain (Building M)"),
    "m_stairs_from_b": ("Acceso y Escaleras al Edificio M (desde Edificio B)", "Building M Entrance & Stairs (from Building B)"),
    "m_stairs_f1": ("Escaleras Principales Edificio M (Piso 1)", "Building M Main Stairs (Floor 1)"),
    "m_room_201": ("Aula M201", "Classroom M201"),
    "m_room_202": ("Aula M202", "Classroom M202"),
    "m_room_203": ("Aula M203", "Classroom M203"),
    "m_room_204": ("Aula M204", "Classroom M204"),
    "m_stairs_f2": ("Escaleras Edificio M (Piso 2)", "Building M Stairs (Floor 2)"),
    "m_room_301": ("Aula M301", "Classroom M301"),
    "m_room_302": ("Aula M302", "Classroom M302"),
    "m_room_303": ("Aula M303", "Classroom M303"),
    "m_room_304": ("Aula M304", "Classroom M304"),
    "m_stairs_f3": ("Escaleras Edificio M (Piso 3)", "Building M Stairs (Floor 3)"),

    # --- Building N (8) ---
    "n_reception": ("Recepción de Clínicas Odontológicas y Archivo - Caja (Edificio N)", "Dental Clinics Reception, Records & Cashier (Building N)"),
    "n_restrooms_men": ("Servicios Sanitarios Hombres (Edificio N - junto a Plaza Chilamates)", "Men's Restrooms (Building N - next to Chilamates Plaza)"),
    "n_restrooms_women": ("Servicios Sanitarios Mujeres (Edificio N - junto a Plaza Chilamates)", "Women's Restrooms (Building N - next to Chilamates Plaza)"),
    "n_access_from_d": ("Acceso hacia Clínicas Odontológicas (desde Lab Odontología Digital D)", "Dental Clinics Access (from Building D Digital Dentistry Lab)"),
    "n_stairs_to_p": ("Acceso Norte Edificio N hacia Parqueo y Edificio P", "Building N North Access to Parking & Building P"),
    "n_stairs_f1": ("Escaleras hacia Facultad de Odontología (FODO - Piso 1)", "Stairs to Faculty of Dentistry (FODO - Floor 1)"),
    "n_fodo_f2_reception": ("Facultad de Odontología (FODO) — Recepción Piso 2", "Faculty of Dentistry (FODO) — Floor 2 Reception"),
    "n_stairs_f2": ("Escaleras Edificio N (Piso 2)", "Building N Stairs (Floor 2)"),

    # --- Building O (25) ---
    "o_fia_101": ("Facultad de Ingeniería y Arquitectura (O101)", "Faculty of Engineering & Architecture (O101)"),
    "o_lab_suelos_102": ("Laboratorio de Mecánica de Suelos (O102)", "Soil Mechanics Lab (O102)"),
    "o_exhibition_area": ("Área de Exhibición (Edificio O)", "Exhibition Area (Building O)"),
    "o_lab_materiales_104": ("Laboratorio de Resistencia de Materiales (O104)", "Materials Testing Lab (O104)"),
    "o_mixing_area": ("Área de Mezclado (Lab Materiales)", "Mixing Area (Materials Lab)"),
    "o_curing_area": ("Área de Curado (Lab Materiales)", "Curing Area (Materials Lab)"),
    "o_lab_technicians": ("Técnicos de Laboratorio (Edificio O)", "Lab Technicians Office (Building O)"),
    "o_lab_fluidos": ("Laboratorio de Mecánica de Fluidos", "Fluid Mechanics Lab"),
    "o_restrooms_men": ("Baños Hombres (Anexo FIA)", "Men's Restrooms (FIA Annex)"),
    "o_restrooms_women": ("Baños Mujeres (Anexo FIA)", "Women's Restrooms (FIA Annex)"),
    "o_teachers_lounge": ("Sala de Maestros FIA (Anexo Norte)", "FIA Faculty Lounge (North Annex)"),
    "o_riesgos_105": ("Coordinación de Gestión Integral de Riesgos de Desastres (O105)", "Comprehensive Disaster Risk Management Coordination (O105)"),
    "o_mapa_uam": ("Mapa UAM (Entrada Edificio O)", "UAM Map (Building O Entrance)"),
    "o_stairs_f1": ("Escaleras Interiores Edificio O (Piso 1)", "Building O Interior Stairs (Floor 1)"),
    "o_stairs_parking": ("Escaleras del O al Parqueo", "Stairs from Building O to Parking"),
    "o_ramp_parking": ("Rampa Accesible del O al Parqueo", "Accessible Ramp from Building O to Parking"),
    "o_sidewalk_parking": ("Acera hacia Parqueo del Edificio O", "Sidewalk to Building O Parking"),
    "o_lab_redes_201": ("Laboratorio de Redes O201", "Networks Lab O201"),
    "o_room_202": ("Aula O202", "Classroom O202"),
    "o_tutoring_room": ("Sala de Tutoría FIA", "FIA Tutoring Room"),
    "o_ciar": ("Centro de Inteligencia Artificial y Robótica (CIAR)", "Artificial Intelligence & Robotics Center (CIAR)"),
    "o_networks_center": ("Centro de Redes (Edificio O)", "Networks Center (Building O)"),
    "o_robotics": ("Área de Robótica (CIAR)", "Robotics Area (CIAR)"),
    "o_fountain_f2": ("Bebedero de Agua (Edificio O - Piso 2)", "Drinking Fountain (Building O - Floor 2)"),
    "o_stairs_f2": ("Escaleras Interiores Edificio O (Piso 2)", "Building O Interior Stairs (Floor 2)"),

    # --- Building P (50) ---
    "p_weather_station": ("Estación de Meteorología (Edificio P)", "Weather Station (Building P)"),
    "p_room_101": ("Aula P101", "Classroom P101"),
    "p_fountain_f1": ("Bebedero de Agua (Edificio P - Piso 1 Este)", "Drinking Fountain (Building P - Floor 1 East)"),
    "p_room_102": ("Aula P102", "Classroom P102"),
    "p_room_103": ("Aula P103", "Classroom P103"),
    "p_room_104": ("Aula P104", "Classroom P104"),
    "p_room_105": ("Aula P105", "Classroom P105"),
    "p_room_106": ("Aula P106", "Classroom P106"),
    "p_room_107": ("Aula P107", "Classroom P107"),
    "p_room_108": ("Aula P108", "Classroom P108"),
    "p_fountain_f1_west": ("Bebedero de Agua (Edificio P - Piso 1 Oeste)", "Drinking Fountain (Building P - Floor 1 West)"),
    "p_restrooms_men_f1": ("Baños Hombres (Edificio P - Piso 1)", "Men's Restrooms (Building P - Floor 1)"),
    "p_restrooms_women_f1": ("Baños Mujeres (Edificio P - Piso 1)", "Women's Restrooms (Building P - Floor 1)"),
    "p_stairs_f1_ext_left": ("Escaleras del P (Izquierda / Exterior)", "Building P Stairs (Left / Exterior)"),
    "p_stairs_f1_east": ("Escaleras Este del P (Piso 1)", "Building P East Stairs (Floor 1)"),
    "p_stairs_f1_west": ("Escaleras Oeste del P (Piso 1)", "Building P West Stairs (Floor 1)"),
    "p_stairs_to_building_o": ("Escaleras del P hacia Edificio O", "Building P Stairs toward Building O"),
    "p_ramp_parking": ("Rampa del Estacionamiento hacia Edificio P", "Parking Ramp to Building P"),
    "p_room_201": ("Aula P201", "Classroom P201"),
    "p_fountain_f2_east": ("Bebedero de Agua (Edificio P - Piso 2 Este)", "Drinking Fountain (Building P - Floor 2 East)"),
    "p_room_202": ("Aula P202", "Classroom P202"),
    "p_room_203": ("Aula P203", "Classroom P203"),
    "p_room_204": ("Aula P204", "Classroom P204"),
    "p_room_205": ("Aula P205", "Classroom P205"),
    "p_room_206": ("Aula P206", "Classroom P206"),
    "p_room_207": ("Aula P207", "Classroom P207"),
    "p_room_208": ("Aula P208", "Classroom P208"),
    "p_fountain_f2_west": ("Bebedero de Agua (Edificio P - Piso 2 Oeste)", "Drinking Fountain (Building P - Floor 2 West)"),
    "p_restrooms_men_f2": ("Baños Hombres (Edificio P - Piso 2)", "Men's Restrooms (Building P - Floor 2)"),
    "p_restrooms_women_f2": ("Baños Mujeres (Edificio P - Piso 2)", "Women's Restrooms (Building P - Floor 2)"),
    "p_stairs_f2_east": ("Escaleras Este del P (Piso 2)", "Building P East Stairs (Floor 2)"),
    "p_stairs_f2_west": ("Escaleras Oeste del P (Piso 2)", "Building P West Stairs (Floor 2)"),
    "p_room_301": ("Aula P301", "Classroom P301"),
    "p_fountain_f3": ("Bebedero de Agua (Edificio P - Piso 3 Este)", "Drinking Fountain (Building P - Floor 3 East)"),
    "p_room_302": ("Aula P302", "Classroom P302"),
    "p_room_303": ("Aula P303", "Classroom P303"),
    "p_room_304": ("Aula P304", "Classroom P304"),
    "p_room_305": ("Aula P305", "Classroom P305"),
    "p_room_306": ("Aula P306", "Classroom P306"),
    "p_room_307": ("Aula P307", "Classroom P307"),
    "p_room_308": ("Aula P308", "Classroom P308"),
    "p_fountain_f3_west": ("Bebedero de Agua (Edificio P - Piso 3 Oeste)", "Drinking Fountain (Building P - Floor 3 West)"),
    "p_restrooms_men_f3": ("Baños Hombres (Edificio P - Piso 3)", "Men's Restrooms (Building P - Floor 3)"),
    "p_restrooms_women_f3": ("Baños Mujeres (Edificio P - Piso 3)", "Women's Restrooms (Building P - Floor 3)"),
    "p_stairs_f3_east": ("Escaleras Este del P (Piso 3)", "Building P East Stairs (Floor 3)"),
    "p_stairs_f3_west": ("Escaleras Oeste del P (Piso 3)", "Building P West Stairs (Floor 3)"),
    "p_room_401": ("Aula P401", "Classroom P401"),
    "p_stairs_f4_east": ("Escaleras del Anexo del P (Piso 4)", "Building P Annex Stairs (Floor 4)"),
    "p_observatory_501": ("Observatorio Copérnico (P501)", "Copernicus Observatory (P501)"),
    "p_stairs_f5_east": ("Escaleras del Observatorio del P (Piso 5)", "Building P Observatory Stairs (Floor 5)"),

    # --- Jaguar Center (13) ---
    "jc_martial_arts": ("Salón de Artes Marciales", "Martial Arts Hall"),
    "jc_multipurpose": ("Salón de Usos Múltiples - DVE", "Multipurpose Hall - DVE"),
    "jc_multipurpose_court": ("Cancha Multi-Usos (Jaguar Center)", "Multipurpose Court (Jaguar Center)"),
    "jc_beach_volleyball": ("Cancha de Volleyball Arena (Jaguar Center)", "Beach Volleyball Court (Jaguar Center)"),
    "jc_kiosk_sport": ("Kiosko Jaguar Sport", "Jaguar Sport Kiosk"),
    "jc_physiotherapy": ("Clínica Fisioterapia", "Physiotherapy Clinic"),
    "jc_gym": ("Gimnasio JAGUAR GYM y Bebedero", "Jaguar Gym & Drinking Fountain"),
    "jc_sports_psych": ("Oficina Psicología Deportiva", "Sports Psychology Office"),
    "jc_bodega_general": ("Bodega General y Contenedores", "General Warehouse & Containers"),
    "jc_sports_office": ("Oficinas Deportivas 1-3 (Oficina de Deportes)", "Sports Offices 1-3 (Sports Office)"),
    "jc_comedor_colaboradores": ("Comedor de Colaboradores", "Staff Dining Hall"),
    "jc_main_entry": ("Entrada Jaguar Center (junto a Edificio L)", "Jaguar Center Entrance (next to Building L)"),
    "jc_mapa_uam": ("Mapa UAM (Complejo Jaguar Center)", "UAM Map (Jaguar Center Complex)"),

    # --- Sports Zone (8) ---
    "sp_baseball_stadium": ("Estadio de Baseball (Jaguar Stadium)", "Baseball Stadium (Jaguar Stadium)"),
    "sp_soccer_field": ("Cancha de Fútbol", "Soccer Field"),
    "sp_restrooms_men": ("Baños Hombres (Campos Deportivos)", "Men's Restrooms (Sports Fields)"),
    "sp_restrooms_women": ("Baños Mujeres (Campos Deportivos)", "Women's Restrooms (Sports Fields)"),
    "sp_kiosk_jaguarcito": ("Kiosko Jaguarcito", "Jaguarcito Kiosk"),
    "sp_sports_office": ("Oficinas de Deportes", "Sports Offices"),
    "sp_sports_warehouse": ("Bodega de Deportes", "Sports Equipment Storage"),
    "sp_soccer_left": ("Cancha de Fútbol (Entrada Izquierda)", "Soccer Field (Left Entrance)"),
}


# =============================================================================
# 4. HELPER FUNCTIONS
# =============================================================================
def getLocalizedPlaceName(place: dict, lang: str = "spa") -> str:
    """Returns the localized display name for a PLACES_CATALOG entry."""
    activeLang = normalize_language(lang)
    placeId = place.get("placeId", "")
    entry = PLACE_TRANSLATIONS.get(placeId)
    if entry:
        if activeLang == "eng":
            return entry.get("name_eng") or place.get("name", "")
        return entry.get("name_spa") or place.get("name", "")
    return place.get("name", "")


def getLocalizedPlaceNotes(place: dict, lang: str = "spa") -> str:
    """Returns the localized location notes for a PLACES_CATALOG entry."""
    activeLang = normalize_language(lang)
    placeId = place.get("placeId", "")
    entry = PLACE_TRANSLATIONS.get(placeId)
    if entry:
        if activeLang == "eng":
            return entry.get("notes_eng") or place.get("locationNotes", "")
        return entry.get("notes_spa") or place.get("locationNotes", "")
    return place.get("locationNotes", "")


def getPlaceBilingualNames(place: dict) -> List[str]:
    """Returns both Spanish and English display names for bilingual search indexing."""
    names: List[str] = []
    rawName = place.get("name", "")
    if rawName:
        names.append(rawName)
    placeId = place.get("placeId", "")
    entry = PLACE_TRANSLATIONS.get(placeId)
    if entry:
        for k in ("name_spa", "name_eng"):
            val = entry.get(k)
            if val and val not in names:
                names.append(val)
    return names


def getIndoorNodeNames(nodeId: str, fallbackName: str) -> Tuple[str, str]:
    """Returns (spaName, engName) for a BuildingSubgraph indoor node."""
    pair = INDOOR_NODE_TRANSLATIONS.get(nodeId)
    if pair:
        return pair
    return (fallbackName, fallbackName)


def getLocalizedSubgraphName(buildingId: str, fallbackName: str, lang: str = "spa") -> str:
    """Returns the localized display name for a BuildingSubgraph."""
    activeLang = normalize_language(lang)
    entry = SUBGRAPH_TRANSLATIONS.get(buildingId)
    if entry:
        return entry.get(f"name_{activeLang}") or fallbackName
    return fallbackName


def getLocalizedSubgraphDescription(buildingId: str, fallbackDesc: str, lang: str = "spa") -> str:
    """Returns the localized description for a BuildingSubgraph."""
    activeLang = normalize_language(lang)
    entry = SUBGRAPH_TRANSLATIONS.get(buildingId)
    if entry:
        return entry.get(f"desc_{activeLang}") or fallbackDesc
    return fallbackDesc
