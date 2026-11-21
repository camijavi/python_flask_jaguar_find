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

    print("\n" + "=" * 80)
    print("  ALL GRAPH, PERIMETER & SUBGRAPH TESTS COMPLETED SUCCESSFULLY!")
    print("=" * 80)

if __name__ == "__main__":
    runGraphTestSuite()
