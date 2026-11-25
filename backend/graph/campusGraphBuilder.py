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
    # Coordinates calibrated against official field GPS measurements (coordenadas.txt)
    g.addNode(Node("mainParking", "Main Parking & South Gate", CampusCategory.PARKING_LOT, 22.8, 90.1, 12.109617, -86.256553))
    g.addNode(Node("buildingK", "Building K (Central Cafeteria & Terraces)", CampusCategory.FOOD_AREA, 30.2, 61.9, 12.108775, -86.256755))
    g.addNode(Node("chilamatesPlaza", "Chilamates Plaza (Kiosks & Fast Point)", CampusCategory.FOOD_AREA, 24.5, 34.4, 12.108027, -86.256705))
    g.addNode(Node("buildingA", "Building A (Student Services & Lost and Found)", CampusCategory.ADMINISTRATIVE, 26.9, 51.2, 12.108503, -86.256678))
    g.addNode(Node("buildingB", "Building B (Classrooms B101-B210 & Pharmacy)", CampusCategory.CLASSROOM, 37.0, 54.0, 12.108568, -86.256991))
    g.addNode(Node("buildingC", "Building C (Computer Labs & Cashier Office)", CampusCategory.CLASSROOM, 37.0, 48.4, 12.108446, -86.257021))
    g.addNode(Node("buildingD", "Building D (Digital Dentistry CAM-CAM)", CampusCategory.DENTAL_LAB, 34.2, 37.2, 12.108128, -86.256945))
    g.addNode(Node("buildingJ", "Building J (Dentistry Labs)", CampusCategory.DENTAL_LAB, 30.1, 37.2, 12.108126, -86.256780, accessLevel="restricted"))
    g.addNode(Node("buildingN", "Building N (Dental Clinics - Reception)", CampusCategory.DENTAL_LAB, 36.8, 30.6, 12.107871, -86.256967, accessLevel="restricted",
                   accessNotice="Clinics Reception. Access to clinical areas and operating rooms requires sterile uniform and faculty authorization."))
    g.addNode(Node("buildingO", "Building O (Faculty of Engineering & Architecture - FIA)", CampusCategory.FACULTY, 50.9, 23.1, 12.107554, -86.257487))
    g.addNode(Node("buildingP", "Building P (Classrooms & Copernicus Observatory)", CampusCategory.CLASSROOM, 38.0, 13.5, 12.107455, -86.256981))
    g.addNode(Node("buildingM", "Building M (Classrooms & Graduate Programs)", CampusCategory.CLASSROOM, 52.2, 51.2, 12.108439, -86.257594))
    g.addNode(Node("buildingG", "Building G (Law School & Central Auditorium)", CampusCategory.FACULTY, 50.3, 60.0, 12.108695, -86.257600))
    g.addNode(Node("buildingF", "Building F (Business Administration Faculty)", CampusCategory.FACULTY, 50.3, 66.4, 12.108938, -86.257431))
    g.addNode(Node("buildingE", "Building E (Medical Faculty & Clinics)", CampusCategory.FACULTY, 44.5, 68.2, 12.109062, -86.257375))
    g.addNode(Node("buildingI", "Building I (Rectorate & Central Library)", CampusCategory.ADMINISTRATIVE, 64.7, 77.2, 12.109237, -86.258051))
    g.addNode(Node("buildingH", "Building H (Medical Labs)", CampusCategory.MEDICAL_LAB, 54.3, 43.4, 12.108255, -86.257537, accessLevel="restricted"))
    g.addNode(Node("sportsZone", "Sports Fields (Baseball Stadium & Soccer Field)", CampusCategory.SPORTS, 78.2, 52.6, 12.108450, -86.258461))
    g.addNode(Node("jaguarCenter", "Jaguar Center Complex (Sports Center)", CampusCategory.SPORTS, 75.0, 73.3, 12.109111, -86.258514))
    g.addNode(Node("jaguarGym", "Jaguar Gym", CampusCategory.SPORTS, 80.8, 85.4, 12.109309, -86.258508))
    g.addNode(Node("physiotherapy", "Physiotherapy Building", CampusCategory.MEDICAL_LAB, 81.5, 79.6, 12.109303, -86.258511))
    g.addNode(Node("jaguarJungle", "Jaguar Jungle (Nature Garden & Central Connector)", CampusCategory.FOOD_AREA, 52.2, 36.0, 12.108073, -86.257787))
    g.addNode(Node("miRanchito", "Mi Ranchito (Dining & Rest Pavilion)", CampusCategory.FOOD_AREA, 46.3, 34.8, 12.108058, -86.257323))
    g.addNode(Node("labDigitalFia", "FIA Digital Laboratory", CampusCategory.FACULTY, 44.2, 38.6, 12.108110, -86.257290))
    g.addNode(Node("areaDeMesas", "Outdoor Tables Area", CampusCategory.FOOD_AREA, 44.3, 43.1, 12.108195, -86.257314))
    g.addNode(Node("buildingL", "Building L (Culture & Music)", CampusCategory.CLASSROOM, 82.4, 72.0, 12.109123, -86.258504))
    g.addNode(Node("northeastGate", "Second Access (Jaguar Stadium Road)", CampusCategory.PARKING_LOT, 75.5, 2.0, 12.106364, -86.258808))
    g.addNode(Node("northGate", "Third Access (Copernicus / West Avenue Gate)", CampusCategory.PARKING_LOT, 15.5, 9.0, 12.107223, -86.256261))

    # 2. Walkways / Edges with Physical Distance in Meters and Accessibility
    # Walkways are bidirectional, modeled as symmetric pairs of directed edges (u -> v) and (v -> u)
    g.addBidirectionalWalkway("mainParking", "buildingK", 65.0, isAccessible=True,
                             forwardInstruction="Walk 65m straight from Main Entrance towards Central Cafeteria (Building K).",
                             backwardInstruction="Walk 65m along the main sidewalk back to Main Parking & Entrance.")

    g.addBidirectionalWalkway("mainParking", "buildingA", 90.0, isAccessible=True,
                             forwardInstruction="Walk 90m straight along the main sidewalk past Building K and the bank towards Building A.",
                             backwardInstruction="Walk 90m straight along the main sidewalk past Building K towards Main Entrance.")

    g.addBidirectionalWalkway("mainParking", "buildingE", 95.0, isAccessible=True,
                             forwardInstruction="Turn right at the Main Entrance and follow the south avenue sidewalk 95m towards Building E (Medicine).",
                             backwardInstruction="Follow the south avenue sidewalk 95m back towards Main Parking & Entrance.")

    g.addBidirectionalWalkway("mainParking", "buildingI", 150.0, isAccessible=True,
                             forwardInstruction="Turn right at the Main Entrance and follow the south avenue sidewalk 150m directly to Rectorate & Central Library (Building I).",
                             backwardInstruction="Follow the south avenue sidewalk 150m from Building I back to Main Entrance.")

    g.addBidirectionalWalkway("buildingA", "buildingC", 30.0, isAccessible=True,
                             forwardInstruction="Follow the indoor corridor 30m from Building A into Building C (Computer Labs & Cashier).",
                             backwardInstruction="Follow Building C's corridor 30m towards Building A.")

    g.addBidirectionalWalkway("buildingB", "buildingE", 35.0, isAccessible=True,
                             forwardInstruction="Cross the covered 2nd-floor skybridge 35m from Building B directly to Building E (Medicine).",
                             backwardInstruction="Cross the covered 2nd-floor skybridge 35m from Building E directly to Building B.")

    g.addBidirectionalWalkway("buildingC", "buildingM", 30.0, isAccessible=True,
                             forwardInstruction="Exit Building C's west corridor and walk 30m to Building M's main entrance.",
                             backwardInstruction="Exit Building M's main entrance and walk 30m into Building C's west corridor.")

    g.addBidirectionalWalkway("buildingE", "buildingG", 25.0, isAccessible=True,
                             forwardInstruction="Cross the interior courtyard walkway 25m from Building E to Building G (Law & Auditorium).",
                             backwardInstruction="Cross the interior courtyard walkway 25m from Building G to Building E (Medicine).")

    g.addBidirectionalWalkway("buildingK", "buildingA", 45.0, isAccessible=True,
                             forwardInstruction="Advance 45m northeast towards Building A (Student Services).",
                             backwardInstruction="Advance 45m southwest towards Building K.")

    g.addBidirectionalWalkway("buildingK", "chilamatesPlaza", 50.0, isAccessible=True,
                             forwardInstruction="Walk 50m northwest towards Chilamates Plaza.",
                             backwardInstruction="Walk 50m southeast towards Building K.")

    g.addBidirectionalWalkway("chilamatesPlaza", "buildingA", 30.0, isAccessible=True,
                             forwardInstruction="Cross the zebra crosswalk 30m from Chilamates Plaza directly into Building A.",
                             backwardInstruction="Exit Building A's corridor and cross the zebra crosswalk 30m into Chilamates Plaza.")

    g.addBidirectionalWalkway("chilamatesPlaza", "buildingJ", 25.0, isAccessible=True,
                             forwardInstruction="Walk 25m east from Chilamates Plaza to Building J (Dentistry Labs).",
                             backwardInstruction="Walk 25m west from Building J into Chilamates Plaza.")

    g.addBidirectionalWalkway("chilamatesPlaza", "buildingN", 35.0, isAccessible=True,
                             forwardInstruction="Follow the internal Chilamates Plaza walkway 35m directly to Building N (Dental Clinics).",
                             backwardInstruction="Walk 35m around Building N's west side into Chilamates Plaza.")

    g.addBidirectionalWalkway("chilamatesPlaza", "buildingP", 55.0, isAccessible=True,
                             forwardInstruction="Follow the straight walkway 55m north from Chilamates Plaza across the parking lot towards Building P (Copernicus).",
                             backwardInstruction="Walk 55m south from Building P directly into Chilamates Plaza.")

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
                             forwardInstruction="Walk 15m from FIA Digital Lab directly to Building N (Dental Clinics).",
                             backwardInstruction="Exit Building N and walk 15m to FIA Digital Lab.")

    g.addBidirectionalWalkway("labDigitalFia", "areaDeMesas", 15.0, isAccessible=True,
                             forwardInstruction="Continue 15m along the walkway from FIA Digital Lab to the Outdoor Tables Area.",
                             backwardInstruction="Walk 15m along the walkway from the Outdoor Tables Area to FIA Digital Lab.")

    g.addBidirectionalWalkway("areaDeMesas", "buildingC", 20.0, isAccessible=True,
                             forwardInstruction="Walk 20m from the Outdoor Tables Area towards Building C (Computer Labs & Cashier).",
                             backwardInstruction="Walk 20m from Building C towards the Outdoor Tables Area.")

    g.addBidirectionalWalkway("areaDeMesas", "buildingH", 25.0, isAccessible=True,
                             forwardInstruction="Follow the walkway 25m from the Outdoor Tables Area towards Building H (Medical Labs).",
                             backwardInstruction="Follow the walkway 25m from Building H towards the Outdoor Tables Area.")

    g.addBidirectionalWalkway("areaDeMesas", "buildingM", 30.0, isAccessible=True,
                             forwardInstruction="Follow the pedestrian walkway 30m from the Outdoor Tables Area towards Building M.",
                             backwardInstruction="Follow the pedestrian walkway 30m from Building M towards the Outdoor Tables Area.")

    return g
