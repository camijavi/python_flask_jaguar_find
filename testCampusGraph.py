"""
testCampusGraph.py
================================================================================
Interactive & Automated verification script for the UAM Campus Graph Engine.
Demonstrates Dijkstra route calculation in English and Spanish (i18n),
accessibility pruning, category filtering, and smart keyword resolution.
================================================================================
"""

import sys
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

from grafoUam import globalNavigationService, CampusCategory, CATEGORY_METADATA, CampusGeoUtils, t

def runGraphTestSuite():
    print("=" * 80)
    print("  JAGUARFIND & JAGUARMAPS - UAM CAMPUS GRAPH VERIFICATION SUITE")
    print("=" * 80)

    # 1a. Standard Pedestrian Route in English (Default Internal Representation)
    print("\n[TEST 1A] Calculating Pedestrian Route in English (lang='eng'):")
    print("  Origin: mainParking (Main Parking)")
    print("  Destination: 'B103' (Classroom B-103)")
    resEng = globalNavigationService.calculateRoute("mainParking", "B103", lang="eng")
    if resEng["success"]:
        print(f"  [OK] Success! Path: {' -> '.join(resEng['pathNodeIds'])}")
        print(f"  [OK] Total Walking Distance: {resEng['totalDistanceMeters']} meters (~{resEng['estimatedWalkingMinutes']} min)")
        print("  [OK] Step Instructions (English):")
        for idx, step in enumerate(resEng["stepInstructions"], 1):
            print(f"     {idx}. {step}")
    else:
        print(f"  [FAIL] Failed: {resEng['error']}")

    # 1b. Standard Pedestrian Route in Spanish (via languages/spa.json)
    print("\n[TEST 1B] Calculating Pedestrian Route in Spanish (lang='spa'):")
    print("  Origin: mainParking (Parqueo Principal)")
    print("  Destination: 'B103' (Aula B-103)")
    resSpa = globalNavigationService.calculateRoute("mainParking", "B103", lang="spa")
    if resSpa["success"]:
        print(f"  [OK] Success! Path: {' -> '.join(resSpa['pathNodeIds'])}")
        print(f"  [OK] Total Walking Distance: {resSpa['totalDistanceMeters']} meters (~{resSpa['estimatedWalkingMinutes']} min)")
        print("  [OK] Step Instructions (Spanish from spa.json):")
        for idx, step in enumerate(resSpa["stepInstructions"], 1):
            print(f"     {idx}. {step}")
    else:
        print(f"  [FAIL] Failed: {resSpa['error']}")

    # 2. Universal Accessibility Test
    print("\n[TEST 2] Accessibility (Wheelchair Pruning) Test:")
    print("  Origin: buildingN (Dental Clinics)")
    print("  Destination: buildingP (Copernicus Observatory)")
    
    # 2a. Without accessibility filter (allows stairs)
    resNormal = globalNavigationService.calculateRoute("buildingN", "buildingP", accessibleOnly=False, lang="eng")
    # 2b. With accessibility filter (must avoid stairs and take Building O ramp)
    resAccessible = globalNavigationService.calculateRoute("buildingN", "buildingP", accessibleOnly=True, lang="eng")

    print(f"  • Standard Route (includes stairs): {' -> '.join(resNormal['pathNodeIds'])} ({resNormal['totalDistanceMeters']}m)")
    print(f"  • Accessible Route (ramps only):    {' -> '.join(resAccessible['pathNodeIds'])} ({resAccessible['totalDistanceMeters']}m)")
    if resAccessible["pathNodeIds"] == ["buildingN", "buildingO", "buildingP"]:
        print("  [OK] Algorithm successfully bypassed stairs and routed through accessible ramps!")

    # 3. Category Queries (Drinking Fountains, Restrooms, Food, Labs)
    print("\n[TEST 3] Category Queries & Facilities Discovery:")
    categoriesToTest = [
        CampusCategory.DRINKING_FOUNTAIN,
        CampusCategory.RESTROOM,
        CampusCategory.FOOD_AREA,
        CampusCategory.MEDICAL_LAB,
        CampusCategory.DENTAL_LAB,
        CampusCategory.FACULTY,
        CampusCategory.ACCESSIBLE_RAMP
    ]

    for cat in categoriesToTest:
        meta = CATEGORY_METADATA.get(cat, {})
        places = globalNavigationService.getPlacesByCategory(cat)
        print(f"  • {meta.get('labelEnglish', cat)} / {meta.get('labelSpanish', cat)} ({len(places)} locations registered):")
        for p in places[:3]: # Show first 3
            print(f"     - {p['name']} in {p['parentBuildingId']} (Floor {p['floorLevel']})")
        if len(places) > 3:
            print(f"     ... and {len(places) - 3} more.")

    # 4. GPS Nearest Node Test (Haversine & Real UAM Coordinates)
    print("\n[TEST 4] GPS Nearest Node Detection (Haversine):")
    # Coordinates near Building B (12.10773, -86.25793)
    userLat, userLng = 12.10775, -86.25790
    nearestEng = globalNavigationService.findNearestGpsNode(userLat, userLng, lang="eng")
    nearestSpa = globalNavigationService.findNearestGpsNode(userLat, userLng, lang="spa")
    print(f"  User GPS: ({userLat}, {userLng})")
    print(f"  [OK] Nearest Node (English): {nearestEng['nearestNodeId']} ({nearestEng['nodeName']}) - {nearestEng['distanceMeters']}m away")
    print(f"  [OK] Nearest Node (Spanish): {nearestSpa['nearestNodeId']} ({nearestSpa['nodeName']}) - {nearestSpa['distanceMeters']}m away")
    print(f"  [OK] Inside Campus: {nearestEng.get('isWithinCampus')}")
    assert nearestEng["isWithinCampus"] is True, "Test 4 Failed: Expected coordinate to be inside campus."

    # 5. UAM Campus Perimeter Polygon & Out-of-Bounds Verification (Ray-Casting)
    print("\n[TEST 5] Campus Perimeter Polygon & Boundary Verification:")
    perimeter = CampusGeoUtils.getCampusPerimeter()
    print(f"  • Registered Perimeter Vertices ({len(perimeter)} points):")
    for idx, pt in enumerate(perimeter, 1):
        print(f"     {idx}. Lat: {pt['lat']:.6f}, Lng: {pt['lng']:.6f}")
    assert len(perimeter) == 8, "Test 5 Failed: Expected 8 perimeter vertices."

    # Point A: Inside campus (Building K / Central Cafeteria)
    inLat, inLng = 12.10746, -86.25810
    insideResult = CampusGeoUtils.isWithinCampusPerimeter(inLat, inLng)
    print(f"  [OK] Test Point A (Inside Cafeteria {inLat}, {inLng}): isInside={insideResult}")
    assert insideResult is True, "Test 5 Failed: Expected Building K to be inside perimeter."

    # Point B: Outside campus (Downtown Managua / Rotonda Metrocentro)
    outLat, outLng = 12.12700, -86.26500
    outsideResult = CampusGeoUtils.isWithinCampusPerimeter(outLat, outLng)
    print(f"  [OK] Test Point B (Outside Metrocentro {outLat}, {outLng}): isInside={outsideResult}")
    assert outsideResult is False, "Test 5 Failed: Expected Metrocentro to be outside perimeter."

    # Point C: Far outside campus (Tipitapa / Airport)
    farLat, farLng = 12.14000, -86.17000
    farResult = CampusGeoUtils.isWithinCampusPerimeter(farLat, farLng)
    print(f"  [OK] Test Point C (Far Outside {farLat}, {farLng}): isInside={farResult}")
    assert farResult is False, "Test 5 Failed: Expected far location to be outside perimeter."

    # Point D: Buffer tolerance check (12 meters outside south entrance)
    p8Lat, p8Lng = perimeter[7]["lat"], perimeter[7]["lng"]
    nearEdgeLat, nearEdgeLng = p8Lat - 0.00010, p8Lng - 0.00005
    distToEdge = min(
        CampusGeoUtils.pointToSegmentDistanceMeters(
            nearEdgeLat, nearEdgeLng,
            perimeter[i]["lat"], perimeter[i]["lng"],
            perimeter[(i + 1) % len(perimeter)]["lat"], perimeter[(i + 1) % len(perimeter)]["lng"]
        )
        for i in range(len(perimeter))
    )
    strictCheck = CampusGeoUtils.isWithinCampusPerimeter(nearEdgeLat, nearEdgeLng, bufferMeters=0.0)
    bufferedCheck = CampusGeoUtils.isWithinCampusPerimeter(nearEdgeLat, nearEdgeLng, bufferMeters=25.0)
    print(f"  [OK] Test Point D (Near South Boundary: {distToEdge:.1f}m off): strict={strictCheck}, with 25m buffer={bufferedCheck}")
    assert strictCheck is False and bufferedCheck is True, "Test 5 Failed: Buffer tolerance logic discrepancy."

    # 6. Building P Child Graph / Subgraph Indoor Routing Test
    print("\n[TEST 6] Building P Child Graph (Indoor Multi-Floor Navigation):")
    from backend.subgraphs import getBuildingSubgraph
    sgP = getBuildingSubgraph("buildingP")
    assert sgP is not None, "Test 6 Failed: Building P subgraph not found."

    totalNodes = len(sgP.getAllNodes())
    f1Nodes = len(sgP.getNodesByFloor(1))
    f2Nodes = len(sgP.getNodesByFloor(2))
    f3Nodes = len(sgP.getNodesByFloor(3))
    print(f"  [OK] Building P Loaded: {sgP.name} ({totalNodes} nodes across {len(sgP.floors)} floors)")
    print(f"     • Floor 1 nodes: {f1Nodes}")
    print(f"     • Floor 2 nodes: {f2Nodes}")
    print(f"     • Floor 3 nodes: {f3Nodes}")
    assert f1Nodes >= 14, f"Test 6 Failed: Expected >= 14 nodes on Floor 1, got {f1Nodes}"
    assert f2Nodes >= 12, f"Test 6 Failed: Expected >= 12 nodes on Floor 2, got {f2Nodes}"
    assert f3Nodes >= 11, f"Test 6 Failed: Expected >= 11 nodes on Floor 3, got {f3Nodes}"

    # 6a. Single-Floor Indoor Route (P101 -> P108)
    resF1 = sgP.calculateIndoorRoute("p_room_101", "p_room_108", accessibleOnly=False, lang="spa")
    print(f"\n  • 6a. Route Floor 1 (P-101 -> P-108):")
    print(f"     Path: {' -> '.join(resF1['pathNodeIds'])}")
    print(f"     Distance: {resF1['totalDistanceMeters']}m (~{resF1['estimatedWalkingMinutes']} min)")
    assert resF1["success"] is True, "Test 6a Failed: Expected successful route P101 -> P108"
    assert "p_room_108" in resF1["pathNodeIds"], "Test 6a Failed: Target node not reached"

    # 6b. Multi-Floor Vertical Route (P101 -> P205 via East Stairs)
    resF2 = sgP.calculateIndoorRoute("p_room_101", "p_room_205", accessibleOnly=False, lang="spa")
    print(f"\n  • 6b. Route Floor 1 -> Floor 2 (P-101 -> P-205 via Escaleras Este):")
    print(f"     Path: {' -> '.join(resF2['pathNodeIds'])}")
    print(f"     Floors crossed: {resF2['floorsCrossed']}")
    print(f"     Distance: {resF2['totalDistanceMeters']}m")
    assert resF2["success"] is True, "Test 6b Failed: Expected successful route P101 -> P205"
    assert resF2["floorsCrossed"] == [1, 2], "Test 6b Failed: Expected floors [1, 2]"
    assert "p_stairs_f1_east" in resF2["pathNodeIds"] and "p_stairs_f2_east" in resF2["pathNodeIds"]

    # 6c. Multi-Floor Route to Top Floor (P101 -> P306 via Stairs)
    resF3 = sgP.calculateIndoorRoute("p_room_101", "p_room_306", accessibleOnly=False, lang="spa")
    print(f"\n  • 6c. Route Floor 1 -> Floor 3 (P-101 -> P-306):")
    print(f"     Path: {' -> '.join(resF3['pathNodeIds'])}")
    print(f"     Floors crossed: {resF3['floorsCrossed']}")
    print(f"     Distance: {resF3['totalDistanceMeters']}m")
    assert resF3["success"] is True, "Test 6c Failed: Expected successful route P101 -> P306"
    assert resF3["floorsCrossed"] == [1, 2, 3], "Test 6c Failed: Expected floors [1, 2, 3]"

    # 6d. Accessible Route Verification
    # Ramp from parking to Floor 1: Accessible
    resRamp = sgP.calculateIndoorRoute("p_ramp_parking", "p_room_108", accessibleOnly=True, lang="spa")
    assert resRamp["success"] is True, "Test 6d Failed: Ramp to Floor 1 should be accessible"
    # Climbing stairs to Floor 2: Not accessible (stairs only)
    resNoWheelchairStairs = sgP.calculateIndoorRoute("p_room_101", "p_room_205", accessibleOnly=True, lang="spa")
    assert resNoWheelchairStairs["success"] is False, "Test 6d Failed: Stairs should be blocked for wheelchair routing"
    print(f"  [OK] Accessibility Check: Ramps allow wheelchair access; stairs are properly blocked when accessibleOnly=True.")

    # 7. Building D Child Graph / Subgraph Indoor Routing Test
    print("\n[TEST 7] Building D Child Graph (Odontología Digital - Single Floor Navigation):")
    sgD = getBuildingSubgraph("buildingD")
    assert sgD is not None, "Test 7 Failed: Building D subgraph not found."
    nodesD = sgD.getAllNodes()
    assert len(nodesD) == 5, f"Test 7 Failed: Expected 5 nodes in Building D, got {len(nodesD)}"
    print(f"  [OK] Building D Loaded: {sgD.name} ({len(nodesD)} nodes on Floor 1)")
    for n in nodesD:
        print(f"     • {n.nodeId}: {n.name} [{n.latitude}, {n.longitude}]")

    # 7a. Indoor Route: Mapa UAM (Entrada) -> Aula D-102
    resD1 = sgD.calculateIndoorRoute("d_uam_map", "d_room_102", lang="spa")
    assert resD1["success"] is True, f"Test 7a Failed: {resD1}"
    print(f"\n  • 7a. Route Mapa UAM -> Aula D-102:")
    print(f"     Path: {' -> '.join(resD1['pathNodeIds'])}")
    print(f"     Distance: {resD1['totalDistanceMeters']}m")
    assert resD1["pathNodeIds"] == ["d_uam_map", "d_room_102"]

    # 7b. Indoor Route: Aula D-102 -> Laboratorio CAM-CAM
    resD2 = sgD.calculateIndoorRoute("d_room_102", "d_lab_cam_cam", lang="spa")
    assert resD2["success"] is True, f"Test 7b Failed: {resD2}"
    print(f"\n  • 7b. Route Aula D-102 -> CAM-CAM:")
    print(f"     Path: {' -> '.join(resD2['pathNodeIds'])}")
    print(f"     Distance: {resD2['totalDistanceMeters']}m")
    assert resD2["pathNodeIds"] == ["d_room_102", "d_lab_cam_cam"]

    # 7c. Indoor Route: Servicio al Cliente -> Laboratorio CAM-CAM
    resD3 = sgD.calculateIndoorRoute("d_customer_service", "d_lab_cam_cam", lang="spa")
    assert resD3["success"] is True, f"Test 7c Failed: {resD3}"
    print(f"\n  • 7c. Route Servicio al Cliente -> CAM-CAM:")
    print(f"     Path: {' -> '.join(resD3['pathNodeIds'])}")
    print(f"     Distance: {resD3['totalDistanceMeters']}m")

    # 7d. Indoor Route: Sala de Reunión -> Aula D-102
    resD4 = sgD.calculateIndoorRoute("reunion", "d102", lang="spa")
    assert resD4["success"] is True, f"Test 7d Failed: {resD4}"
    print(f"\n  • 7d. Keyword Route 'reunion' -> 'd102':")
    print(f"     Path: {' -> '.join(resD4['pathNodeIds'])}")
    print(f"     Distance: {resD4['totalDistanceMeters']}m")

    # 8. Building J Child Graph / Subgraph Indoor Routing Test
    print("\n[TEST 8] Building J Child Graph (Laboratorios de Odontología - Single Floor Navigation):")
    sgJ = getBuildingSubgraph("buildingJ")
    assert sgJ is not None, "Test 8 Failed: Building J subgraph not found."
    nodesJ = sgJ.getAllNodes()
    assert len(nodesJ) == 5, f"Test 8 Failed: Expected 5 nodes in Building J, got {len(nodesJ)}"
    print(f"  [OK] Building J Loaded: {sgJ.name} ({len(nodesJ)} nodes on Floor 1)")
    for n in nodesJ:
        print(f"     • {n.nodeId}: {n.name} [{n.latitude}, {n.longitude}]")

    # 8a. Indoor Route: Entrada -> Lab J-101
    resJ1 = sgJ.calculateIndoorRoute("j_entrance", "j_lab_101", lang="spa")
    assert resJ1["success"] is True, f"Test 8a Failed: {resJ1}"
    print(f"\n  • 8a. Route Entrada -> Lab J-101:")
    print(f"     Path: {' -> '.join(resJ1['pathNodeIds'])}")
    print(f"     Distance: {resJ1['totalDistanceMeters']}m")

    # 8b. Indoor Route: Lab J-101 -> Lab J-102
    resJ2 = sgJ.calculateIndoorRoute("j_lab_101", "j_lab_102", lang="spa")
    assert resJ2["success"] is True, f"Test 8b Failed: {resJ2}"
    print(f"\n  • 8b. Route Lab J-101 -> Lab J-102:")
    print(f"     Path: {' -> '.join(resJ2['pathNodeIds'])}")
    print(f"     Distance: {resJ2['totalDistanceMeters']}m")

    # 8c. Indoor Route: Lab J-102 -> Baños Hombres
    resJ3 = sgJ.calculateIndoorRoute("j102", "hombres", lang="spa")
    assert resJ3["success"] is True, f"Test 8c Failed: {resJ3}"
    print(f"\n  • 8c. Route Lab J-102 -> Baños Hombres:")
    print(f"     Path: {' -> '.join(resJ3['pathNodeIds'])}")
    print(f"     Distance: {resJ3['totalDistanceMeters']}m")

    # 8d. Indoor Route: Lab J-101 -> Baños Mujeres
    resJ4 = sgJ.calculateIndoorRoute("j101", "mujeres", lang="spa")
    assert resJ4["success"] is True, f"Test 8d Failed: {resJ4}"
    print(f"\n  • 8d. Route Lab J-101 -> Baños Mujeres:")
    print(f"     Path: {' -> '.join(resJ4['pathNodeIds'])}")
    print(f"     Distance: {resJ4['totalDistanceMeters']}m")

    # 9. Building O Child Graph / Subgraph Indoor Routing Test (Multi-Floor FIA)
    print("\n[TEST 9] Building O Child Graph (Facultad de Ingeniería y Arquitectura - 2 Floors):")
    sgO = getBuildingSubgraph("buildingO")
    assert sgO is not None, "Test 9 Failed: Building O subgraph not found."
    nodesO = sgO.getAllNodes()
    assert len(nodesO) == 25, f"Test 9 Failed: Expected 25 nodes in Building O, got {len(nodesO)}"
    f1_nodes = sgO.getNodesByFloor(1)
    f2_nodes = sgO.getNodesByFloor(2)
    assert len(f1_nodes) == 17, f"Test 9 Failed: Expected 17 nodes on Floor 1, got {len(f1_nodes)}"
    assert len(f2_nodes) == 8, f"Test 9 Failed: Expected 8 nodes on Floor 2, got {len(f2_nodes)}"
    print(f"  [OK] Building O Loaded: {sgO.name} ({len(nodesO)} nodes across 2 floors)")
    print(f"     • Floor 1 nodes: {len(f1_nodes)}")
    print(f"     • Floor 2 nodes: {len(f2_nodes)}")

    # 9a. Route Floor 1: Mapa UAM -> Lab Resistencia de Materiales
    resO1 = sgO.calculateIndoorRoute("mapa", "materiales", lang="spa")
    assert resO1["success"] is True, f"Test 9a Failed: {resO1}"
    print(f"\n  • 9a. Route Floor 1 (Mapa UAM -> Lab Materiales):")
    print(f"     Path: {' -> '.join(resO1['pathNodeIds'])}")
    print(f"     Distance: {resO1['totalDistanceMeters']}m")

    # 9b. Route Floor 1: Decanatura FIA -> Baños Mujeres (Anexo Norte)
    resO2 = sgO.calculateIndoorRoute("fia", "baños mujeres", lang="spa")
    assert resO2["success"] is True, f"Test 9b Failed: {resO2}"
    print(f"\n  • 9b. Route Floor 1 (Decanatura FIA -> Baños Mujeres Anexo):")
    print(f"     Path: {' -> '.join(resO2['pathNodeIds'])}")
    print(f"     Distance: {resO2['totalDistanceMeters']}m")

    # 9c. Multi-floor Route: Mapa UAM (Piso 1) -> CIAR (Piso 2)
    resO3 = sgO.calculateIndoorRoute("mapa", "ciar", lang="spa")
    assert resO3["success"] is True, f"Test 9c Failed: {resO3}"
    assert resO3["floorsCrossed"] == [1, 2], f"Test 9c Failed floors: {resO3['floorsCrossed']}"
    print(f"\n  • 9c. Multi-floor Route (Piso 1 -> Piso 2: Mapa UAM -> CIAR):")
    print(f"     Path: {' -> '.join(resO3['pathNodeIds'])}")
    print(f"     Floors crossed: {resO3['floorsCrossed']}")
    print(f"     Distance: {resO3['totalDistanceMeters']}m")

    # 9d. Multi-floor Route: Lab Suelos O-102 (Piso 1) -> Aula O-202 (Piso 2)
    resO4 = sgO.calculateIndoorRoute("suelos", "o202", lang="spa")
    assert resO4["success"] is True, f"Test 9d Failed: {resO4}"
    assert resO4["floorsCrossed"] == [1, 2], f"Test 9d Failed floors: {resO4['floorsCrossed']}"
    print(f"\n  • 9d. Multi-floor Route (Suelos O-102 -> Aula O-202):")
    print(f"     Path: {' -> '.join(resO4['pathNodeIds'])}")
    print(f"     Floors crossed: {resO4['floorsCrossed']}")
    print(f"     Distance: {resO4['totalDistanceMeters']}m")

    # 9e. Wheelchair Accessibility: Parking -> Coordinación de Riesgos via Rampa
    resO5 = sgO.calculateIndoorRoute("o_sidewalk_parking", "o_riesgos_105", accessibleOnly=True, lang="spa")
    assert resO5["success"] is True, f"Test 9e Failed: {resO5}"
    assert "o_ramp_parking" in resO5["pathNodeIds"], "Wheelchair route must use ramp"
    assert "o_stairs_parking" not in resO5["pathNodeIds"], "Wheelchair route must NOT use stairs"
    print(f"\n  • 9e. Wheelchair Accessible Route (Parqueo -> Riesgos O-105 via Rampa):")
    print(f"     Path: {' -> '.join(resO5['pathNodeIds'])}")
    print(f"     Distance: {resO5['totalDistanceMeters']}m")
    print(f"  [OK] Successfully routed via accessible ramp, completely bypassing stairs.")

    # 10. Building C Child Graph / Subgraph Indoor Routing Test (Multi-Floor 3 Levels)
    print("\n[TEST 10] Building C Child Graph (Aulas, Labs Computación & Tesorería - 3 Floors):")
    sgC = getBuildingSubgraph("buildingC")
    assert sgC is not None, "Test 10 Failed: Building C subgraph not found."
    nodesC = sgC.getAllNodes()
    assert len(nodesC) == 42, f"Test 10 Failed: Expected 42 nodes in Building C, got {len(nodesC)}"
    f1_c = sgC.getNodesByFloor(1)
    f2_c = sgC.getNodesByFloor(2)
    f3_c = sgC.getNodesByFloor(3)
    assert len(f1_c) == 15, f"Test 10 Failed: Expected 15 nodes on Floor 1, got {len(f1_c)}"
    assert len(f2_c) == 15, f"Test 10 Failed: Expected 15 nodes on Floor 2, got {len(f2_c)}"
    assert len(f3_c) == 12, f"Test 10 Failed: Expected 12 nodes on Floor 3, got {len(f3_c)}"
    print(f"  [OK] Building C Loaded: {sgC.name} ({len(nodesC)} nodes across 3 floors)")
    print(f"     • Floor 1 nodes: {len(f1_c)}")
    print(f"     • Floor 2 nodes: {len(f2_c)}")
    print(f"     • Floor 3 nodes: {len(f3_c)}")

    # 10a. Route Floor 1: Rampa -> Caja UAM -> Tesorería
    resC1 = sgC.calculateIndoorRoute("rampa", "tesoreria", lang="spa")
    assert resC1["success"] is True, f"Test 10a Failed: {resC1}"
    print(f"\n  • 10a. Route Floor 1 (Rampa -> Tesorería C-105):")
    print(f"     Path: {' -> '.join(resC1['pathNodeIds'])}")
    print(f"     Distance: {resC1['totalDistanceMeters']}m")

    # 10b. Route Floor 1: Auditorio C-101 -> Lab ACAI-Erasmus+ (C-108)
    resC2 = sgC.calculateIndoorRoute("c101", "acai", lang="spa")
    assert resC2["success"] is True, f"Test 10b Failed: {resC2}"
    print(f"\n  • 10b. Route Floor 1 (Auditorio C-101 -> Lab ACAI-Erasmus+ C-108):")
    print(f"     Path: {' -> '.join(resC2['pathNodeIds'])}")
    print(f"     Distance: {resC2['totalDistanceMeters']}m")

    # 10c. Multi-floor Route: Caja UAM (Piso 1) -> Lab MAC C-203 (Piso 2)
    resC3 = sgC.calculateIndoorRoute("caja", "mac c203", lang="spa")
    assert resC3["success"] is True, f"Test 10c Failed: {resC3}"
    assert resC3["floorsCrossed"] == [1, 2], f"Test 10c Failed floors: {resC3['floorsCrossed']}"
    print(f"\n  • 10c. Multi-floor Route (Piso 1 -> Piso 2: Caja UAM -> Lab MAC C-203):")
    print(f"     Path: {' -> '.join(resC3['pathNodeIds'])}")
    print(f"     Floors crossed: {resC3['floorsCrossed']}")
    print(f"     Distance: {resC3['totalDistanceMeters']}m")

    # 10d. Multi-floor Route: Caja UAM (Piso 1) -> Estudio Audiovisual A-301 (Piso 3)
    resC4 = sgC.calculateIndoorRoute("caja", "a-301", lang="spa")
    assert resC4["success"] is True, f"Test 10d Failed: {resC4}"
    assert resC4["floorsCrossed"] == [1, 2, 3], f"Test 10d Failed floors: {resC4['floorsCrossed']}"
    print(f"\n  • 10d. Multi-floor Route (Piso 1 -> Piso 3: Caja UAM -> Estudio A-301):")
    print(f"     Path: {' -> '.join(resC4['pathNodeIds'])}")
    print(f"     Floors crossed: {resC4['floorsCrossed']}")
    print(f"     Distance: {resC4['totalDistanceMeters']}m")

    # 10e. Floor 3 Route: Estudio A-301 -> Coordinación de Compras C-306 -> Aula C-310
    resC5 = sgC.calculateIndoorRoute("a301", "c310", lang="spa")
    assert resC5["success"] is True, f"Test 10e Failed: {resC5}"
    print(f"\n  • 10e. Route Floor 3 (Estudio A-301 -> Aula C-310):")
    print(f"     Path: {' -> '.join(resC5['pathNodeIds'])}")
    print(f"     Distance: {resC5['totalDistanceMeters']}m")

    print("\n" + "=" * 80)
    print("  ALL GRAPH, PERIMETER & SUBGRAPH TESTS COMPLETED SUCCESSFULLY!")
    print("=" * 80)

if __name__ == "__main__":
    runGraphTestSuite()
