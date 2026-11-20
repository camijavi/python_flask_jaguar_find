"""
testCampusGraph.py
================================================================================
Interactive & Automated verification script for the UAM Campus Graph Engine.
Demonstrates Dijkstra route calculation in English and Spanish (i18n),
accessibility pruning (♿), category filtering, and smart keyword resolution.
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
        print(f"  ✓ Success! Path: {' -> '.join(resEng['pathNodeIds'])}")
        print(f"  ✓ Total Walking Distance: {resEng['totalDistanceMeters']} meters (~{resEng['estimatedWalkingMinutes']} min)")
        print("  ✓ Step Instructions (English):")
        for idx, step in enumerate(resEng["stepInstructions"], 1):
            print(f"     {idx}. {step}")
    else:
        print(f"  ✗ Failed: {resEng['error']}")

    # 1b. Standard Pedestrian Route in Spanish (via languages/spa.json)
    print("\n[TEST 1B] Calculating Pedestrian Route in Spanish (lang='spa'):")
    print("  Origin: mainParking (Parqueo Principal)")
    print("  Destination: 'B103' (Aula B-103)")
    resSpa = globalNavigationService.calculateRoute("mainParking", "B103", lang="spa")
    if resSpa["success"]:
        print(f"  ✓ Success! Path: {' -> '.join(resSpa['pathNodeIds'])}")
        print(f"  ✓ Total Walking Distance: {resSpa['totalDistanceMeters']} meters (~{resSpa['estimatedWalkingMinutes']} min)")
        print("  ✓ Step Instructions (Spanish from spa.json):")
        for idx, step in enumerate(resSpa["stepInstructions"], 1):
            print(f"     {idx}. {step}")
    else:
        print(f"  ✗ Failed: {resSpa['error']}")

    # 2. Universal Accessibility (♿) Test
    print("\n[TEST 2] Accessibility (Wheelchair ♿) Pruning Test:")
    print("  Origin: buildingN (Dental Clinics)")
    print("  Destination: buildingP (Copernicus Observatory)")
    
    # 2a. Without accessibility filter (allows stairs)
    resNormal = globalNavigationService.calculateRoute("buildingN", "buildingP", accessibleOnly=False, lang="eng")
    # 2b. With accessibility filter (must avoid stairs and take Building O ramp)
    resAccessible = globalNavigationService.calculateRoute("buildingN", "buildingP", accessibleOnly=True, lang="eng")

    print(f"  • Standard Route (includes stairs): {' -> '.join(resNormal['pathNodeIds'])} ({resNormal['totalDistanceMeters']}m)")
    print(f"  • Accessible Route (ramps only):    {' -> '.join(resAccessible['pathNodeIds'])} ({resAccessible['totalDistanceMeters']}m)")
    if resAccessible["pathNodeIds"] == ["buildingN", "buildingO", "buildingP"]:
        print("  ✓ Algorithm successfully bypassed stairs and routed through accessible ramps!")

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
    print(f"  ✓ Nearest Node (English): {nearestEng['nearestNodeId']} ({nearestEng['nodeName']}) - {nearestEng['distanceMeters']}m away")
    print(f"  ✓ Nearest Node (Spanish): {nearestSpa['nearestNodeId']} ({nearestSpa['nodeName']}) - {nearestSpa['distanceMeters']}m away")
    print(f"  ✓ Inside Campus: {nearestEng.get('isWithinCampus')}")
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
    print(f"  ✓ Test Point A (Inside Cafeteria {inLat}, {inLng}): isInside={insideResult}")
    assert insideResult is True, "Test 5 Failed: Expected Building K to be inside perimeter."

    # Point B: Outside campus (Downtown Managua / Rotonda Metrocentro)
    outLat, outLng = 12.12700, -86.26500
    outsideResult = CampusGeoUtils.isWithinCampusPerimeter(outLat, outLng)
    print(f"  ✓ Test Point B (Outside Metrocentro {outLat}, {outLng}): isInside={outsideResult}")
    assert outsideResult is False, "Test 5 Failed: Expected Metrocentro to be outside perimeter."

    # Point C: Far outside campus (Tipitapa / Airport)
    farLat, farLng = 12.14000, -86.17000
    farResult = CampusGeoUtils.isWithinCampusPerimeter(farLat, farLng)
    print(f"  ✓ Test Point C (Far Outside {farLat}, {farLng}): isInside={farResult}")
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
    print(f"  ✓ Test Point D (Near South Boundary: {distToEdge:.1f}m off): strict={strictCheck}, with 25m buffer={bufferedCheck}")
    assert strictCheck is False and bufferedCheck is True, "Test 5 Failed: Buffer tolerance logic discrepancy."

    print("\n" + "=" * 80)
    print("  ALL GRAPH & PERIMETER TESTS COMPLETED SUCCESSFULLY! READY FOR FLASK / UI CONSUMPTION.")
    print("=" * 80)

if __name__ == "__main__":
    runGraphTestSuite()
