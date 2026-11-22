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
    g.addNode(Node("jaguarJungle", "Jaguar Jungle (Nature Garden & Central Connector)", CampusCategory.FOOD_AREA, 52.2, 36.0, 12.10832, -86.25742))
    g.addNode(Node("miRanchito", "Mi Ranchito (Dining & Rest Pavilion)", CampusCategory.FOOD_AREA, 46.3, 34.8, 12.10838, -86.25758))
    g.addNode(Node("labDigitalFia", "Digital FIA Laboratory (Lab Digital FIA)", CampusCategory.FACULTY, 44.2, 38.6, 12.10824, -86.25764))
    g.addNode(Node("areaDeMesas", "Outdoor Tables Area (Área de Mesas)", CampusCategory.FOOD_AREA, 44.3, 43.1, 12.10812, -86.25764))
    g.addNode(Node("buildingL", "Building L (Culture & Music)", CampusCategory.CLASSROOM, 69.0, 72.0, 12.10725, -86.25673))
    g.addNode(Node("northeastGate", "Second Access (Jaguar Stadium Road)", CampusCategory.PARKING_LOT, 75.5, 2.0, 12.10885, -86.25697))
    g.addNode(Node("northGate", "Third Access (Copernicus / West Avenue Gate)", CampusCategory.PARKING_LOT, 15.5, 9.0, 12.10895, -86.25818))

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
                             forwardInstruction="Walk 40m west along the northern road towards Third Access (Copernicus Gate).",
                             backwardInstruction="Enter through Third Access and proceed 40m east towards Building P (Copernicus).")

    g.addBidirectionalWalkway("northGate", "chilamatesPlaza", 85.0, isAccessible=True,
                             forwardInstruction="Follow the West Main Avenue 85m south from Third Access towards Chilamates Plaza.",
                             backwardInstruction="Follow the West Main Avenue 85m north from Chilamates Plaza towards Third Access.")

    g.addBidirectionalWalkway("northGate", "northeastGate", 140.0, isAccessible=True,
                             forwardInstruction="Follow the northern perimeter road 140m east past Building P towards Second Access (Jaguar Stadium Road).",
                             backwardInstruction="Follow the northern perimeter road 140m west from Second Access (Jaguar Stadium Road) towards Third Access.")

    g.addBidirectionalWalkway("buildingO", "northeastGate", 75.0, isAccessible=True,
                             forwardInstruction="Follow the internal main road 75m north past Building O parking towards Second Access (Jaguar Stadium Road).",
                             backwardInstruction="Enter via Second Access (Jaguar Stadium Road) and follow the main spine road 75m south towards Building O.")

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
                             forwardInstruction="Follow the north sports parking path 45m north towards Second Access (Jaguar Stadium Road).",
                             backwardInstruction="Enter via Second Access (Jaguar Stadium Road) and advance 45m south towards Jaguar Baseball Stadium and Sports Fields.")

    g.addBidirectionalWalkway("buildingC", "buildingH", 40.0, isAccessible=True,
                             forwardInstruction="Walk 40m east towards Medical Labs (Building H).",
                             backwardInstruction="Walk 40m west towards Building C.")

    g.addBidirectionalWalkway("buildingM", "buildingH", 35.0, isAccessible=True,
                             forwardInstruction="Walk 35m northeast towards Building H.",
                             backwardInstruction="Walk 35m southwest towards Building M.")

    # Jaguar Jungle, Mi Ranchito, Lab Digital FIA & Outdoor Tables Area (Area de Mesas) Connector Network
    g.addBidirectionalWalkway("jaguarJungle", "buildingO", 25.0, isAccessible=True,
                             forwardInstruction="Follow the Jaguar Jungle garden path 25m towards Building O (FIA).",
                             backwardInstruction="Enter Jaguar Jungle from Building O and walk 25m along the shaded garden path.")

    g.addBidirectionalWalkway("jaguarJungle", "buildingH", 25.0, isAccessible=True,
                             forwardInstruction="Continue 25m along the Jaguar Jungle path towards Building H (Medical Labs).",
                             backwardInstruction="Enter Jaguar Jungle from Building H and walk 25m along the central garden path.")

    g.addBidirectionalWalkway("jaguarJungle", "miRanchito", 20.0, isAccessible=True,
                             forwardInstruction="Walk 20m along the Jaguar Jungle walkway towards Mi Ranchito.",
                             backwardInstruction="Enter Jaguar Jungle from Mi Ranchito, walking 20m along the main garden walkway.")

    g.addBidirectionalWalkway("jaguarJungle", "labDigitalFia", 20.0, isAccessible=True,
                             forwardInstruction="Follow the Jaguar Jungle walkway 20m to the corridor beside Lab Digital FIA.",
                             backwardInstruction="Enter Jaguar Jungle from the Lab Digital FIA corridor, walking 20m into the central garden.")

    g.addBidirectionalWalkway("jaguarJungle", "sportsZone", 55.0, isAccessible=True,
                             forwardInstruction="Exit Jaguar Jungle onto the main internal road and cross 55m towards the Sports Fields.",
                             backwardInstruction="Cross the main internal road 55m from the Sports Fields into Jaguar Jungle.")

    g.addBidirectionalWalkway("miRanchito", "buildingO", 30.0, isAccessible=True,
                             forwardInstruction="Walk 30m skirting Jaguar Jungle from Mi Ranchito towards Building O (FIA).",
                             backwardInstruction="Walk 30m from Building O skirting Jaguar Jungle towards Mi Ranchito.")

    g.addBidirectionalWalkway("miRanchito", "buildingN", 25.0, isAccessible=True,
                             forwardInstruction="Walk 25m along the pedestrian walkway from Mi Ranchito towards Building N (Dental Clinics).",
                             backwardInstruction="Walk 25m from Building N along the pedestrian walkway towards Mi Ranchito.")

    g.addBidirectionalWalkway("miRanchito", "labDigitalFia", 15.0, isAccessible=True,
                             forwardInstruction="Walk 15m along the pedestrian corridor from Mi Ranchito to Lab Digital FIA.",
                             backwardInstruction="Walk 15m along the pedestrian corridor from Lab Digital FIA to Mi Ranchito.")

    g.addBidirectionalWalkway("labDigitalFia", "buildingN", 15.0, isAccessible=True,
                             forwardInstruction="Walk 15m from Lab Digital FIA directly to Building N (Dental Clinics).",
                             backwardInstruction="Exit Building N and walk 15m to Lab Digital FIA.")

    g.addBidirectionalWalkway("labDigitalFia", "areaDeMesas", 15.0, isAccessible=True,
                             forwardInstruction="Continue 15m along the walkway from Lab Digital FIA to the Outdoor Tables Area (Área de Mesas).",
                             backwardInstruction="Walk 15m along the walkway from Área de Mesas to Lab Digital FIA.")

    g.addBidirectionalWalkway("areaDeMesas", "buildingC", 20.0, isAccessible=True,
                             forwardInstruction="Walk 20m from Área de Mesas towards Building C (Computer Labs & Cashier).",
                             backwardInstruction="Walk 20m from Building C towards the Outdoor Tables Area (Área de Mesas).")

    g.addBidirectionalWalkway("areaDeMesas", "buildingH", 25.0, isAccessible=True,
                             forwardInstruction="Follow the walkway 25m from Área de Mesas towards Building H (Medical Labs).",
                             backwardInstruction="Follow the walkway 25m from Building H towards the Outdoor Tables Area (Área de Mesas).")

    g.addBidirectionalWalkway("areaDeMesas", "buildingM", 30.0, isAccessible=True,
                             forwardInstruction="Follow the pedestrian walkway 30m from Área de Mesas towards Building M.",
                             backwardInstruction="Follow the pedestrian walkway 30m from Building M towards the Outdoor Tables Area (Área de Mesas).")

    return g
