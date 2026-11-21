"""
campusCategories.py
================================================================================
Official category definitions for UAM Campus POIs and facilities.
Uses English identifiers and camelCase conventions.
================================================================================
"""

class CampusCategory:
    CLASSROOM = "classroom"
    DRINKING_FOUNTAIN = "drinkingFountain"
    MEDICAL_LAB = "medicalLab"
    DENTAL_LAB = "dentalLab"
    FACULTY = "faculty"
    FOOD_AREA = "foodArea"
    PARKING_LOT = "parkingLot"
    RESTROOM = "restroom"
    ACCESSIBLE_RAMP = "accessibleRamp"
    ADMINISTRATIVE = "administrative"
    SPORTS = "sports"
    AUDITORIUM = "auditorium"
    STAIRS = "stairs"

# Metadata dictionary for frontend icons, labels and accessibility tags
CATEGORY_METADATA = {
    CampusCategory.CLASSROOM: {
        "labelSpanish": "Aulas de Clases",
        "labelEnglish": "Classrooms",
        "icon": "chalkboard-user",
        "badgeColor": "blue"
    },
    CampusCategory.DRINKING_FOUNTAIN: {
        "labelSpanish": "Bebederos de Agua",
        "labelEnglish": "Drinking Fountains",
        "icon": "faucet",
        "badgeColor": "cyan"
    },
    CampusCategory.MEDICAL_LAB: {
        "labelSpanish": "Laboratorios de Medicina",
        "labelEnglish": "Medical Laboratories",
        "icon": "flask-vial",
        "badgeColor": "emerald"
    },
    CampusCategory.DENTAL_LAB: {
        "labelSpanish": "Laboratorios Odontología",
        "labelEnglish": "Dental Laboratories",
        "icon": "tooth",
        "badgeColor": "teal"
    },
    CampusCategory.FACULTY: {
        "labelSpanish": "Facultades UAM",
        "labelEnglish": "UAM Faculties & Deaneries",
        "icon": "graduation-cap",
        "badgeColor": "indigo"
    },
    CampusCategory.FOOD_AREA: {
        "labelSpanish": "Áreas de Comida & Cafetería",
        "labelEnglish": "Dining & Cafeterias",
        "icon": "utensils",
        "badgeColor": "amber"
    },
    CampusCategory.PARKING_LOT: {
        "labelSpanish": "Parqueos & Accesos",
        "labelEnglish": "Parking Lots & Gates",
        "icon": "square-parking",
        "badgeColor": "slate"
    },
    CampusCategory.RESTROOM: {
        "labelSpanish": "Servicios Sanitarios",
        "labelEnglish": "Restrooms",
        "icon": "restroom",
        "badgeColor": "violet"
    },
    CampusCategory.ACCESSIBLE_RAMP: {
        "labelSpanish": "Rampas Accesibles",
        "labelEnglish": "Accessible Ramps",
        "icon": "wheelchair",
        "badgeColor": "sky"
    },
    CampusCategory.ADMINISTRATIVE: {
        "labelSpanish": "Atención & Oficinas",
        "labelEnglish": "Administrative Services",
        "icon": "building-columns",
        "badgeColor": "purple"
    },
    CampusCategory.SPORTS: {
        "labelSpanish": "Deportes & Gimnasio",
        "labelEnglish": "Sports & Gymnasium",
        "icon": "dumbbell",
        "badgeColor": "rose"
    },
    CampusCategory.AUDITORIUM: {
        "labelSpanish": "Auditorios & Eventos",
        "labelEnglish": "Auditoriums & Events",
        "icon": "users-viewfinder",
        "badgeColor": "orange"
    },
    CampusCategory.STAIRS: {
        "labelSpanish": "Escaleras & Accesos Verticales",
        "labelEnglish": "Stairs & Vertical Access",
        "icon": "stairs",
        "badgeColor": "gray"
    }
}
