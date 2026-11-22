"""
campusGraphBuilder.py
Constructs the official weighted, directed, and non-complete graph of UAM campus.
Includes nodes (macro buildings, gates, outdoor POIs) and bidirectional pedestrian walkways.
All internal code, default names, and default instructions are kept in English.
Translations for Spanish and English user interfaces are loaded dynamically via i18n dictionaries.
"""

from .directedGraph import DirectedGraph, Node
from data.campusCategories import CampusCategory


def buildUamCampusGraph() -> DirectedGraph:
    """
    Constructs the official weighted, directed, and non-complete graph of UAM campus.
    Coordinates correspond to official campus map and entrance waypoints.
    Default internal representations are in English.
    """
    g = DirectedGraph()

    # 1. Main Buildings, Gates & Public Nodes (Macro Graph)
    g.addNode(Node("mainParking", "Main Parking & South Gate", CampusCategory.PARKING_LOT, 35.0, 85.0, 12.10681, -86.25790))
    g.addNode(Node("buildingK", "Building K (Central Cafeteria & Terraces)", CampusCategory.FOOD_AREA, 29.0, 66.0, 12.10746, -86.25810))
    g.addNode(Node("chilamatesPlaza", "Chilamates Plaza (Kiosks & Fast Point)", CampusCategory.FOOD_AREA, 24.0, 48.0, 12.10807, -86.25827))
    g.addNode(Node("buildingA", "Building A (Student Services & Lost and Found)", CampusCategory.ADMINISTRATIVE, 28.0, 58.0, 12.10773, -86.25814))
    g.addNode(Node("buildingB", "Building B (Classrooms B101-B106 & Pharmacy)", CampusCategory.CLASSROOM, 34.0, 58.0, 12.10773, -86.25793))
    g.addNode(Node("buildingC", "Building C (Computer Labs & Cashier Office)", CampusCategory.CLASSROOM, 34.0, 53.0, 12.10790, -86.25793))
    g.addNode(Node("buildingD", "Building D (Digital Dentistry CAM-CAM)", CampusCategory.DENTAL_LAB, 31.0, 44.0, 12.10820, -86.25803))
    g.addNode(Node("buildingJ", "Building J (Dentistry Labs)", CampusCategory.DENTAL_LAB, 29.0, 44.0, 12.10820, -86.25810, accessLevel="restricted"))
    g.addNode(Node("buildingN", "Building N (Dental Clinics - Reception)", CampusCategory.DENTAL_LAB, 33.0, 40.0, 12.10834, -86.25796, accessLevel="restricted",
                   accessNotice="Clinics Reception. Access to clinical areas and operating rooms requires sterile uniform and faculty authorization."))
    g.addNode(Node("buildingO", "Building O (Faculty of Engineering & Architecture - FIA)", CampusCategory.FACULTY, 43.0, 32.0, 12.10861, -86.25762))
    g.addNode(Node("buildingP", "Building P (Classrooms & Copernicus Observatory)", CampusCategory.CLASSROOM, 33.0, 27.0, 12.10878, -86.25796))
    g.addNode(Node("buildingM", "Building M (Classrooms & Graduate Programs)", CampusCategory.CLASSROOM, 45.0, 55.0, 12.10783, -86.25755))
    g.addNode(Node("buildingG", "Building G (Law School & Central Auditorium)", CampusCategory.FACULTY, 44.0, 62.0, 12.10759, -86.25759))
    g.addNode(Node("buildingF", "Building F (Business Administration Faculty)", CampusCategory.FACULTY, 44.0, 68.0, 12.10739, -86.25759))
    g.addNode(Node("buildingE", "Building E (Medical Faculty & Clinics)", CampusCategory.FACULTY, 41.0, 72.0, 12.10725, -86.25769))
    g.addNode(Node("buildingI", "Building I (Rectorate & Central Library)", CampusCategory.ADMINISTRATIVE, 55.0, 76.0, 12.10712, -86.25721))
    g.addNode(Node("buildingH", "Building H (Medical Labs)", CampusCategory.MEDICAL_LAB, 46.0, 50.0, 12.10800, -86.25752, accessLevel="restricted"))
    g.addNode(Node("sportsZone", "Sports Fields (Baseball Stadium & Soccer Field)", CampusCategory.SPORTS, 64.0, 45.0, 12.10817, -86.25690))
    g.addNode(Node("jaguarCenter", "Jaguar Center Complex (Sports Center)", CampusCategory.SPORTS, 64.0, 72.0, 12.10725, -86.25690))
    g.addNode(Node("jaguarGym", "Jaguar Gym", CampusCategory.SPORTS, 79.0, 85.0, 12.10712, -86.25665))
    g.addNode(Node("physiotherapy", "Physiotherapy Building", CampusCategory.MEDICAL_LAB, 80.0, 79.0, 12.10718, -86.25662))
    g.addNode(Node("buildingL", "Building L (Culture & Music)", CampusCategory.CLASSROOM, 69.0, 72.0, 12.10725, -86.25673))
    g.addNode(Node("northeastGate", "Northeast Gate (Sports Access)", CampusCategory.PARKING_LOT, 62.0, 38.0, 12.10841, -86.25697))
    g.addNode(Node("northGate", "North Gate (Copernicus / FIA Access)", CampusCategory.PARKING_LOT, 36.0, 22.0, 12.10895, -86.25786))

    # 2. Walkways / Edges with Physical Distance in Meters and Accessibility
    # Walkways are bidirectional, modeled as symmetric pairs of directed edges (u -> v) and (v -> u)
    g.addBidirectionalWalkway("mainParking", "buildingK", 65.0, isAccessible=True,
                             forwardInstruction="Walk 65m north towards Central Cafeteria (Building K).",
                             backwardInstruction="Walk 65m south towards Main Parking.")

    g.addBidirectionalWalkway("buildingK", "buildingA", 45.0, isAccessible=True,
                             forwardInstruction="Advance 45m northeast towards Building A (Student Services).",
                             backwardInstruction="Advance 45m southwest towards Building K.")

    g.addBidirectionalWalkway("buildingK", "chilamatesPlaza", 50.0, isAccessible=True,
                             forwardInstruction="Walk 50m northwest towards Chilamates Plaza.",
                             backwardInstruction="Walk 50m southeast towards Building K.")

    g.addBidirectionalWalkway("buildingA", "buildingB", 35.0, isAccessible=True,
                             forwardInstruction="Cross the central hallway 35m east towards Building B.",
                             backwardInstruction="Cross 35m west towards Building A.")

    g.addBidirectionalWalkway("buildingB", "buildingC", 30.0, isAccessible=True,
                             forwardInstruction="Advance 30m north towards Building C (Cashier / Computing).",
                             backwardInstruction="Walk 30m south towards Building B.")

    g.addBidirectionalWalkway("buildingC", "buildingD", 40.0, isAccessible=True,
                             forwardInstruction="Walk 40m north towards Building D.",
                             backwardInstruction="Walk 40m south towards Building C.")

    g.addBidirectionalWalkway("buildingD", "buildingJ", 20.0, isAccessible=True,
                             forwardInstruction="Walk 20m west towards Building J.",
                             backwardInstruction="Walk 20m east towards Building D.")

    g.addBidirectionalWalkway("buildingD", "buildingN", 35.0, isAccessible=True,
                             forwardInstruction="Walk 35m north towards Dental Clinics (Building N).",
                             backwardInstruction="Walk 35m south towards Building D.")

    # Note: Path from Building N to P has stairs; marked isAccessible = False
    g.addBidirectionalWalkway("buildingN", "buildingP", 60.0, isAccessible=False,
                             forwardInstruction="Climb the stairs and advance 60m north towards Building P (Copernicus).",
                             backwardInstruction="Go down the stairs 60m south towards Building N.")

    g.addBidirectionalWalkway("buildingP", "buildingO", 45.0, isAccessible=True,
                             forwardInstruction="Walk 45m east towards Building O (Engineering & Architecture).",
                             backwardInstruction="Walk 45m west towards Building P.")

    g.addBidirectionalWalkway("buildingO", "buildingN", 55.0, isAccessible=True,
                             forwardInstruction="Descend the ramp 55m southwest towards Building N.",
                             backwardInstruction="Ascend the ramp 55m northeast towards Building O.")

    g.addBidirectionalWalkway("buildingP", "northGate", 40.0, isAccessible=True,
                             forwardInstruction="Walk 40m north towards Copernicus Gate (North Gate).",
                             backwardInstruction="Enter through North Gate 40m south towards Building P.")

    g.addBidirectionalWalkway("buildingB", "buildingM", 40.0, isAccessible=True,
                             forwardInstruction="Advance 40m east towards Building M.",
                             backwardInstruction="Advance 40m west towards Building B.")

    g.addBidirectionalWalkway("buildingM", "buildingG", 35.0, isAccessible=True,
                             forwardInstruction="Walk 35m south towards Building G (Central Auditorium / Law).",
                             backwardInstruction="Walk 35m north towards Building M.")

    g.addBidirectionalWalkway("buildingG", "buildingF", 30.0, isAccessible=True,
                             forwardInstruction="Advance 30m south towards Building F (Business Administration).",
                             backwardInstruction="Walk 30m north towards Building G.")

    g.addBidirectionalWalkway("buildingF", "buildingE", 25.0, isAccessible=True,
                             forwardInstruction="Walk 25m south towards Building E (Medicine).",
                             backwardInstruction="Walk 25m north towards Building F.")

    g.addBidirectionalWalkway("buildingE", "buildingI", 60.0, isAccessible=True,
                             forwardInstruction="Advance 60m southeast towards Rectorate & Central Library (Building I).",
                             backwardInstruction="Walk 60m northwest towards Building E.")

    g.addBidirectionalWalkway("buildingI", "jaguarCenter", 70.0, isAccessible=True,
                             forwardInstruction="Cross the walkway 70m east towards Jaguar Center Complex.",
                             backwardInstruction="Walk 70m west towards Central Library (Building I).")

    g.addBidirectionalWalkway("buildingI", "jaguarGym", 55.0, isAccessible=True,
                             forwardInstruction="Cross the connected parking area 55m east towards Jaguar Gym.",
                             backwardInstruction="Walk 55m west across the parking area towards Building I.")

    g.addBidirectionalWalkway("jaguarCenter", "jaguarGym", 25.0, isAccessible=True,
                             forwardInstruction="Walk 25m southeast past the parking lot towards Jaguar Gym.",
                             backwardInstruction="Walk 25m northwest towards Jaguar Center.")

    g.addBidirectionalWalkway("jaguarCenter", "physiotherapy", 20.0, isAccessible=True,
                             forwardInstruction="Walk 20m east towards the Physiotherapy Building.",
                             backwardInstruction="Walk 20m west towards Jaguar Center.")

    g.addBidirectionalWalkway("jaguarGym", "physiotherapy", 15.0, isAccessible=True,
                             forwardInstruction="Walk 15m north towards the Physiotherapy Building.",
                             backwardInstruction="Walk 15m south towards Jaguar Gym.")

    g.addBidirectionalWalkway("physiotherapy", "buildingL", 20.0, isAccessible=True,
                             forwardInstruction="Walk 20m northeast towards Building L.",
                             backwardInstruction="Walk 20m southwest towards the Physiotherapy Building.")

    g.addBidirectionalWalkway("jaguarCenter", "buildingL", 30.0, isAccessible=True,
                             forwardInstruction="Walk 30m east towards Building L (Culture & Music).",
                             backwardInstruction="Walk 30m west towards Jaguar Center.")

    g.addBidirectionalWalkway("jaguarCenter", "sportsZone", 80.0, isAccessible=True,
                             forwardInstruction="Advance 80m north towards the Sports Fields.",
                             backwardInstruction="Walk 80m south towards Jaguar Center.")

    g.addBidirectionalWalkway("sportsZone", "northeastGate", 45.0, isAccessible=True,
                             forwardInstruction="Walk 45m east towards Northeast Sports Gate.",
                             backwardInstruction="Enter through Northeast Gate 45m west towards the sports fields.")

    g.addBidirectionalWalkway("buildingC", "buildingH", 40.0, isAccessible=True,
                             forwardInstruction="Walk 40m east towards Medical Labs (Building H).",
                             backwardInstruction="Walk 40m west towards Building C.")

    g.addBidirectionalWalkway("buildingM", "buildingH", 35.0, isAccessible=True,
                             forwardInstruction="Walk 35m northeast towards Building H.",
                             backwardInstruction="Walk 35m southwest towards Building M.")

    return g
