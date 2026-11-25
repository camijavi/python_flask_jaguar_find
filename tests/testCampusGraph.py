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

from backend.graphUam import globalNavigationService, CampusCategory, CATEGORY_METADATA, CampusGeoUtils, t

def runGraphTestSuite():
    print("=" * 80)
    print("  JAGUARFIND & JAGUARMAPS - UAM CAMPUS GRAPH VERIFICATION SUITE")
    print("=" * 80)

    # 1a. Standard Pedestrian Route in English (Default Internal Representation)
    print("\n[TEST 1A] Calculating Pedestrian Route in English (lang='eng'):")
    print("  Origin: mainParking (Main Parking)")
    print("  Destination: 'B103' (Classroom B103)")
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
    print("  Destination: 'B103' (Aula B103)")
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
    print(f"\n  • 6a. Route Floor 1 (P101 -> P108):")
    print(f"     Path: {' -> '.join(resF1['pathNodeIds'])}")
    print(f"     Distance: {resF1['totalDistanceMeters']}m (~{resF1['estimatedWalkingMinutes']} min)")
    assert resF1["success"] is True, "Test 6a Failed: Expected successful route P101 -> P108"
    assert "p_room_108" in resF1["pathNodeIds"], "Test 6a Failed: Target node not reached"

    # 6b. Multi-Floor Vertical Route (P101 -> P205 via East Stairs)
    resF2 = sgP.calculateIndoorRoute("p_room_101", "p_room_205", accessibleOnly=False, lang="spa")
    print(f"\n  • 6b. Route Floor 1 -> Floor 2 (P101 -> P205 via Escaleras Este):")
    print(f"     Path: {' -> '.join(resF2['pathNodeIds'])}")
    print(f"     Floors crossed: {resF2['floorsCrossed']}")
    print(f"     Distance: {resF2['totalDistanceMeters']}m")
    assert resF2["success"] is True, "Test 6b Failed: Expected successful route P101 -> P205"
    assert resF2["floorsCrossed"] == [1, 2], "Test 6b Failed: Expected floors [1, 2]"
    assert "p_stairs_f1_east" in resF2["pathNodeIds"] and "p_stairs_f2_east" in resF2["pathNodeIds"]

    # 6c. Multi-Floor Route to Top Floor (P101 -> P308 via Stairs)
    resF3 = sgP.calculateIndoorRoute("p_room_101", "p_room_308", accessibleOnly=False, lang="spa")
    print(f"\n  • 6c. Route Floor 1 -> Floor 3 (P101 -> P308):")
    print(f"     Path: {' -> '.join(resF3['pathNodeIds'])}")
    print(f"     Floors crossed: {resF3['floorsCrossed']}")
    print(f"     Distance: {resF3['totalDistanceMeters']}m")
    assert resF3["success"] is True, "Test 6c Failed: Expected successful route P101 -> P308"
    assert resF3["floorsCrossed"] == [1, 2, 3], "Test 6c Failed: Expected floors [1, 2, 3]"
    assert sgP.graph.nodes["p_room_308"].latitude == 12.107435 and sgP.graph.nodes["p_room_308"].longitude == -86.257136

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
    assert len(nodesJ) == 6, f"Test 8 Failed: Expected 6 nodes in Building J, got {len(nodesJ)}"
    print(f"  [OK] Building J Loaded: {sgJ.name} ({len(nodesJ)} nodes on Floor 1)")
    for n in nodesJ:
        print(f"     • {n.nodeId}: {n.name} [{n.latitude}, {n.longitude}]")

    # 8a. Indoor Route: Entrada -> Lab J101
    resJ1 = sgJ.calculateIndoorRoute("j_entrance", "j_lab_101", lang="spa")
    assert resJ1["success"] is True, f"Test 8a Failed: {resJ1}"
    print(f"\n  • 8a. Route Entrada -> Lab J101:")
    print(f"     Path: {' -> '.join(resJ1['pathNodeIds'])}")
    print(f"     Distance: {resJ1['totalDistanceMeters']}m")

    # 8b. Indoor Route: Lab J101 -> Lab J102
    resJ2 = sgJ.calculateIndoorRoute("j_lab_101", "j_lab_102", lang="spa")
    assert resJ2["success"] is True, f"Test 8b Failed: {resJ2}"
    print(f"\n  • 8b. Route Lab J101 -> Lab J102:")
    print(f"     Path: {' -> '.join(resJ2['pathNodeIds'])}")
    print(f"     Distance: {resJ2['totalDistanceMeters']}m")

    # 8c. Indoor Route: Lab J102 -> Baños Hombres
    resJ3 = sgJ.calculateIndoorRoute("j102", "hombres", lang="spa")
    assert resJ3["success"] is True, f"Test 8c Failed: {resJ3}"
    print(f"\n  • 8c. Route Lab J102 -> Baños Hombres:")
    print(f"     Path: {' -> '.join(resJ3['pathNodeIds'])}")
    print(f"     Distance: {resJ3['totalDistanceMeters']}m")

    # 8d. Indoor Route: Lab J101 -> Baños Mujeres
    resJ4 = sgJ.calculateIndoorRoute("j101", "mujeres", lang="spa")
    assert resJ4["success"] is True, f"Test 8d Failed: {resJ4}"
    print(f"\n  • 8d. Route Lab J101 -> Baños Mujeres:")
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

    # 10d. Multi-floor Route: Caja UAM (Piso 1) -> Aula C305 (Piso 3)
    resC4 = sgC.calculateIndoorRoute("caja", "c305", lang="spa")
    assert resC4["success"] is True, f"Test 10d Failed: {resC4}"
    assert resC4["floorsCrossed"] == [1, 2, 3], f"Test 10d Failed floors: {resC4['floorsCrossed']}"
    print(f"\n  • 10d. Multi-floor Route (Piso 1 -> Piso 3: Caja UAM -> Aula C305):")
    print(f"     Path: {' -> '.join(resC4['pathNodeIds'])}")
    print(f"     Floors crossed: {resC4['floorsCrossed']}")
    print(f"     Distance: {resC4['totalDistanceMeters']}m")

    # 10e. Floor 3 Route: Aula C301 -> Coordinación de Compras C306 -> Aula C310
    resC5 = sgC.calculateIndoorRoute("c301", "c310", lang="spa")
    assert resC5["success"] is True, f"Test 10e Failed: {resC5}"
    print(f"\n  • 10e. Route Floor 3 (Aula C301 -> Aula C310):")
    print(f"     Path: {' -> '.join(resC5['pathNodeIds'])}")
    print(f"     Distance: {resC5['totalDistanceMeters']}m")

    # 10f. Building A Floor 3 DPA (A301) properly belongs to Building A, NOT Building C
    sgA = getBuildingSubgraph("buildingA")
    assert sgC.resolveRoomQuery("a301") is None, "A301 must not resolve inside Building C"
    assert sgA.resolveRoomQuery("a301") == "a_dpa_301", "A301 must resolve inside Building A Floor 3"
    resA3 = sgA.calculateIndoorRoute("a101", "set de radio", lang="spa")
    assert resA3["success"] is True and resA3["floorsCrossed"] == [1, 2, 3], f"Test 10f Failed: {resA3}"
    print(f"  [OK] 10f. A301 / DPA strictly mapped to Building A Floor 3 ({' -> '.join(resA3['pathNodeIds'])})")

    # -------------------------------------------------------------------------
    # 11. Formal Graph Properties: All 18 Building Subgraphs + Pedestrian Walkways
    # -------------------------------------------------------------------------
    print("\n[TEST 11] Formal Graph Theory Verification (Weighted, Directed, Non-Complete G = (V, E, W)):")
    from backend.subgraphs import getAllBuildingSubgraphs
    from backend.graph.pedestrianWalkwayGraph import globalPedestrianWalkwayGraph
    import re

    allSubgraphs = getAllBuildingSubgraphs()
    assert len(allSubgraphs) >= 18, f"Test 11 Failed: Expected >= 18 subgraphs, got {len(allSubgraphs)}"
    for bid, sg in allSubgraphs.items():
        nodes = sg.getAllNodes()
        edgeCount = 0
        for n in nodes:
            for e in n.outgoingEdges:
                assert e.distanceMeters > 0, f"Non-positive edge weight in {bid}: {n.nodeId}->{e.targetNodeId}"
                edgeCount += 1
        maxEdges = len(nodes) * max(1, len(nodes) - 1)
        assert edgeCount <= maxEdges, f"Invalid edge count in {bid}"
        # Connectivity check from primary entrance
        visited = set()
        stack = [sg.entranceNodeIds[0]]
        while stack:
            u = stack.pop()
            if u in visited:
                continue
            visited.add(u)
            for e in sg.graph.nodes[u].outgoingEdges:
                stack.append(e.targetNodeId)
        assert len(visited) == len(nodes), f"Disconnected nodes in {bid}: {set(sg.graph.nodes.keys()) - visited}"
    print(f"  [OK] All {len(allSubgraphs)} building subgraphs verified: weighted (w>0), directed, non-complete, fully connected.")

    wNodes = globalPedestrianWalkwayGraph.getAllNodes()
    wEdges = sum(len(n.outgoingEdges) for n in wNodes)
    wDensity = wEdges / (len(wNodes) * (len(wNodes) - 1))
    assert len(wNodes) >= 200 and wEdges >= 400 and wDensity < 0.05, "Walkway graph must be sparse & non-complete"
    for n in wNodes:
        for e in n.outgoingEdges:
            assert e.distanceMeters > 0, f"Non-positive walkway edge weight on {n.nodeId}->{e.targetNodeId}"
    print(f"  [OK] Pedestrian Walkway Graph verified: |V|={len(wNodes)}, |E_dir|={wEdges}, density={wDensity:.4f} (non-complete).")

    # -------------------------------------------------------------------------
    # 12. Human Instructions Quality (Zero Meters, Zero Cardinals, Real Walkways)
    # -------------------------------------------------------------------------
    print("\n[TEST 12] Human Landmark Instructions & Real Pedestrian Walkway Sync:")
    forbiddenMetric = re.compile(r"\b\d+\s*(m|mts|metros|meters)\b", re.IGNORECASE)
    forbiddenCardinal = re.compile(r"\b(al norte|al sur|al este|al oeste|al noreste|al noroeste|al sureste|al suroeste|northeast|northwest|southeast|southwest)\b", re.IGNORECASE)

    humanCheckCases = [
        ("mainParking", "P205", False, "spa"),
        ("mainParking", "B103", False, "spa"),
        ("mainParking", "B103", False, "eng"),
        ("A101", "CIAR", False, "spa"),
        ("C102", "C205", False, "spa"),
        ("buildingB", "buildingE", False, "spa"),
        ("buildingN", "buildingP", True, "spa"),
        ("mainParking", "biblioteca", True, "spa"),
        ("mainParking", "quirofano", False, "spa"),
    ]
    for orig, dest, acc, lang in humanCheckCases:
        route = globalNavigationService.calculateRoute(orig, dest, accessibleOnly=acc, lang=lang)
        assert route["success"] is True, f"Test 12 Failed route {orig}->{dest} (acc={acc}): {route}"
        assert len(route["steps"]) >= 1, f"Test 12 Failed: empty steps for {orig}->{dest}"
        assert route.get("humanDuration"), f"Test 12 Failed: missing humanDuration for {orig}->{dest}"
        for st in route["stepInstructions"]:
            assert not forbiddenMetric.search(st), f"Metric distance leaked in step: {st}"
            assert not forbiddenCardinal.search(st), f"Cardinal direction leaked in step: {st}"
        if orig != dest and route.get("originNodeId") != route.get("destinationNodeId"):
            assert len(route.get("walkwayPath", [])) >= 2, f"Missing walkwayPath for outdoor route {orig}->{dest}"
        if orig == "buildingN" and dest == "buildingP" and acc:
            wIds = route.get("walkwayNodeIds", [])
            # Must not take the non-accessible stairs n_north_stairs -> pon_bot_mid
            for i in range(len(wIds) - 1):
                assert not (wIds[i] == "n_north_stairs" and wIds[i + 1] == "pon_bot_mid"), "Accessible route crossed stairs!"
        if dest == "quirofano":
            assert any("aviso de acceso" in s.lower() for s in route["stepInstructions"]), "Missing Gateway Pattern biosecurity notice!"
        print(f"  [OK] {orig:12s} -> {dest:11s} (acc={str(acc):5s}, {lang}): {len(route['steps'])} human steps | {route['humanDuration']}")

    # -------------------------------------------------------------------------
    # 13. Global GPS Matching (Real Field Coordinates from coordenadas.txt)
    # -------------------------------------------------------------------------
    print("\n[TEST 13] Global GPS Matching (Field Coordinates + Multi-Floor Disambiguation):")
    gpsCases = [
        ("Aula C103", 12.108527, -86.256908, "buildingC", True),
        ("Aula P205", 12.107492, -86.257090, "buildingP", True),
        ("Biblioteca Central", 12.109547, -86.257996, "buildingI", False),
        ("Auditorio M101", 12.108452, -86.257566, "buildingM", True),
        ("Jaguar Gym", 12.109309, -86.258508, "jaguarCenter", False),
        ("Edificio N", 12.107871, -86.256967, "buildingN", True),
        ("DIE (Edificio E)", 12.109312, -86.257369, "buildingE", True),
        ("Edificio K", 12.108775, -86.256755, "buildingK", True),
        ("Jaguar Stadium", 12.107238, -86.258449, "sportsZone", False),
        ("Campo de Fútbol", 12.108450, -86.258461, "sportsZone", False),
        ("Área de Mesas", 12.108195, -86.257314, "areaDeMesas", False),
        ("1er Acceso", 12.109617, -86.256553, "mainParking", False),
        ("2do Acceso", 12.106364, -86.258808, "northeastGate", False),
        ("3er Acceso", 12.107223, -86.256261, "northGate", False),
    ]
    for label, lat, lng, expectedBuilding, expectFloorPrompt in gpsCases:
        match = globalNavigationService.findNearestGpsNode(lat, lng, lang="spa")
        assert match["isWithinCampus"] is True, f"Expected {label} inside campus"
        assert match["nearestNodeId"] == expectedBuilding, f"GPS match mismatch for {label}: got {match['nearestNodeId']} expected {expectedBuilding}"
        assert match["needsFloorSelection"] is expectFloorPrompt, f"Floor selection mismatch for {label}: got {match['needsFloorSelection']}"
        svgPos = match["userSvgPosition"]
        assert 0 <= svgPos["x"] <= 1200 and 0 <= svgPos["y"] <= 850, f"SVG projection out of bounds: {svgPos}"
        print(f"  [OK] {label:18s} -> {match['nodeName']} ({match['distanceMeters']}m) | floorPrompt={match['needsFloorSelection']} | SVG={svgPos}")

    # -------------------------------------------------------------------------
    # 14. Central `graphCombined.py` Unification & Live Inventory Verification
    # -------------------------------------------------------------------------
    print("\n[TEST 14] Central graphCombined.py Unification, Invariants & Live Graph Count:")
    from backend.graph.graphCombined import Graph, Vertex
    from backend.graph import DijkstraRouter, getAllApplicationGraphs, getGraphsInventory
    import backend.children_graphs as childrenGraphsPkg

    # 14a. Standalone graphCombined.Graph invariants
    rawG = Graph()
    assert rawG.insertVertex("Managua") is True
    assert rawG.insertVertex("managua") is False, "Case-insensitive duplicate vertex must be rejected"
    assert rawG.insertVertex("Masaya") is True
    assert rawG.insertVertex("Granada") is True
    assert rawG.search("MANAGUA").city == "Managua"
    assert rawG.link("Managua", "Masaya", 24.0) is True
    assert rawG.addEdge("Managua", "Masaya", 24.0) is False, "Duplicate directed edge must be rejected"
    assert rawG.addEdge("Managua", "Managua", 5.0) is False, "Self-loop must be rejected"
    assert rawG.addEdge("Masaya", "Granada", 0.0) is False, "Non-positive weight must be rejected"
    assert rawG.addEdge("Masaya", "Granada", 22.0) is True
    assert rawG.hasEdge("Managua", "Masaya") is True
    assert rawG.getEdgeWeight("Masaya", "Granada") == 22.0
    assert rawG.isComplete() is False

    # DijkstraRouter works directly on a plain graphCombined.Graph
    rawRouter = DijkstraRouter(rawG)
    rawPath, rawDist, _, _ = rawRouter.findShortestPathWithEdges("Managua", "Granada")
    assert rawPath == ["Managua", "Masaya", "Granada"] and rawDist == 46.0, f"Raw Graph Dijkstra failed: {rawPath}, {rawDist}"
    assert rawG.deleteEdge("Masaya", "Granada") is True
    assert rawG.hasEdge("Masaya", "Granada") is False
    print("  [OK] Standalone graphCombined.py invariants & raw Graph Dijkstra verified.")

    # 14b. All 20 backend graphs inherit from graphCombined.Graph & sync neigh <-> outgoingEdges
    inv = getGraphsInventory()
    assert inv["totalBackendGraphs"] == 20, f"Expected 20 backend graphs, got {inv['totalBackendGraphs']}"
    assert inv["breakdown"]["macroCampusGraphs"] == 1
    assert inv["breakdown"]["microOutdoorWalkwayGraphs"] == 1
    assert inv["breakdown"]["microIndoorBuildingSubgraphs"] == 18
    assert inv["verification"]["allInheritGraphCombined"] is True
    assert inv["verification"]["allNonComplete"] is True

    appGraphs = getAllApplicationGraphs()
    assert len(appGraphs) == 20
    for entry in appGraphs:
        g = entry["graph"]
        assert isinstance(g, Graph), f"{entry['graphId']} does not inherit from graphCombined.Graph"
        assert g.vertexCount() == len(g.nodes), f"vertices/nodes mismatch in {entry['graphId']}"
        assert not g.isComplete(), f"{entry['graphId']} must be non-complete"
        for vertex in g.vertices:
            assert isinstance(vertex, Vertex), f"Vertex {vertex} does not inherit from graphCombined.Vertex"
            assert len(vertex.neigh) == len(vertex.outgoingEdges), (
                f"neigh/outgoingEdges desync in {entry['graphId']} on {vertex.nodeId}"
            )
            for (nbr, weight), edge in zip(vertex.neigh, vertex.outgoingEdges):
                assert nbr.nodeId == edge.targetNodeId and weight == edge.distanceMeters

    # 14c. Every indoor node across all 18 subgraphs owns a valid buildingId + Building P alias fix
    for bid, sg in allSubgraphs.items():
        for node in sg.getAllNodes():
            assert node.buildingId, f"Missing buildingId on {bid}.{node.nodeId}"
    assert getBuildingSubgraph("buildingP").resolveRoomQuery("observatorio") == "p_observatory_501"
    assert len(childrenGraphsPkg.BUILDING_SUBGRAPHS) == 18
    print(
        f"  [OK] All {inv['totalBackendGraphs']} backend graphs verified on graphCombined.py "
        f"(|V|={inv['totals']['vertices']}, |E_dir|={inv['totals']['directedEdges']}, 100% neigh<->outgoingEdges synced)."
    )

    # -------------------------------------------------------------------------
    # 15. Reference File Alignment (buildings.txt & coordenadas.txt)
    # -------------------------------------------------------------------------
    print("\n[TEST 15] Reference File Alignment (Nomenclature, Ordering & Floor Mappings):")
    from backend.data.placesCatalog import PLACES_CATALOG
    from backend.data.campusLocalization import PLACE_TRANSLATIONS, INDOOR_NODE_TRANSLATIONS, SUBGRAPH_TRANSLATIONS
    from backend.services.placeSearchService import buildIndexedPlaces, searchPlaces

    hyphenRoomRe = re.compile(r"\b[A-Z]-[1-5]\d{2}\b")
    for p in PLACES_CATALOG:
        assert not hyphenRoomRe.search(p["name"]), f"Hyphenated room code in PLACES_CATALOG name: {p['name']}"
    for pid, tr in PLACE_TRANSLATIONS.items():
        for field, val in tr.items():
            assert not hyphenRoomRe.search(val), f"Hyphenated room code in PLACE_TRANSLATIONS[{pid}].{field}: {val}"
    for nid, (spaName, engName) in INDOOR_NODE_TRANSLATIONS.items():
        assert not hyphenRoomRe.search(spaName), f"Hyphenated room code in INDOOR_NODE_TRANSLATIONS[{nid}] spa: {spaName}"
        assert not hyphenRoomRe.search(engName), f"Hyphenated room code in INDOOR_NODE_TRANSLATIONS[{nid}] eng: {engName}"
    for bid, tr in SUBGRAPH_TRANSLATIONS.items():
        for field, val in tr.items():
            assert not hyphenRoomRe.search(val), f"Hyphenated room code in SUBGRAPH_TRANSLATIONS[{bid}].{field}: {val}"
    for bid, sg in allSubgraphs.items():
        for node in sg.getAllNodes():
            assert not hyphenRoomRe.search(node.name), f"Hyphenated room code in {bid}.{node.nodeId}: {node.name}"

    # Verify exact left-to-right ordering of Building B, Building C, Building H, Building P
    sgB = getBuildingSubgraph("buildingB")
    bF1RoomIds = [n.nodeId for n in sgB.getNodesByFloor(1) if n.nodeId.startswith("b_room_")]
    bF2RoomIds = [n.nodeId for n in sgB.getNodesByFloor(2) if n.nodeId.startswith("b_room_")]
    assert bF1RoomIds == [f"b_room_{n}" for n in range(101, 110)], f"B F1 order mismatch: {bF1RoomIds}"
    assert bF2RoomIds == [f"b_room_{n}" for n in range(201, 211)], f"B F2 order mismatch: {bF2RoomIds}"

    sgH = getBuildingSubgraph("buildingH")
    assert sgH.graph.nodes["h_lab_coord_necroteca"].floorLevel == 1, "Necroteca / Lab Supervision must be on Floor 1 per buildings.txt"
    hF1LabIds = [n.nodeId for n in sgH.getNodesByFloor(1) if n.nodeId.startswith("h_lab_1")]
    hF2LabIds = [n.nodeId for n in sgH.getNodesByFloor(2) if n.nodeId.startswith("h_lab_2")]
    assert hF1LabIds == [f"h_lab_{n}" for n in range(101, 108)], f"H F1 order mismatch: {hF1LabIds}"
    assert hF2LabIds == [f"h_lab_{n}" for n in range(201, 208)], f"H F2 order mismatch: {hF2LabIds}"

    sgE = getBuildingSubgraph("buildingE")
    assert sgE.graph.nodes["e_psychology"].floorLevel == 2, "Oficina Psicología must be on Building E Floor 2"
    assert sgE.graph.nodes["e_lab_clinico"].floorLevel == 2, "Laboratorio Clínico must be on Building E Floor 2"

    pF3RoomIds = [n.nodeId for n in sgP.getNodesByFloor(3) if n.nodeId.startswith("p_room_")]
    assert pF3RoomIds == [f"p_room_{n}" for n in range(301, 309)], f"P F3 order mismatch: {pF3RoomIds}"

    # Verify hyphen-tolerant search still works for users who type "B-103" or "P-308"
    indexed = buildIndexedPlaces("spa")
    for q, expectedId in [("B103", "classroomB103"), ("B-103", "classroomB103"), ("P308", "classroomP308"), ("P-308", "classroomP308"), ("C305", "classroomC305")]:
        hits = searchPlaces(indexed, query=q)
        assert hits and hits[0]["placeId"] == expectedId, f"Search failed for {q}: got {[h['placeId'] for h in hits[:3]]}"
    print("  [OK] Zero hyphenated room names, exact left-to-right ordering, and floor/coordinate mappings verified.")

    print("\n" + "=" * 80)
    print("  ALL GRAPH, WALKWAY, HUMAN-INSTRUCTION, GPS & SUBGRAPH TESTS PASSED!")
    print("=" * 80)

if __name__ == "__main__":
    runGraphTestSuite()
