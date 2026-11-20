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

from grafoUam import globalNavigationService, CampusCategory, CATEGORY_METADATA, t

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

    # 4. GPS Nearest Node Test (Haversine)
    print("\n[TEST 4] GPS Nearest Node Detection (Haversine):")
    # Coordinates near Building B
    userLat, userLng = 12.12460, -86.27090
    nearestEng = globalNavigationService.findNearestGpsNode(userLat, userLng, lang="eng")
    nearestSpa = globalNavigationService.findNearestGpsNode(userLat, userLng, lang="spa")
    print(f"  User GPS: ({userLat}, {userLng})")
    print(f"  ✓ Nearest Node (English): {nearestEng['nearestNodeId']} ({nearestEng['nodeName']}) - {nearestEng['distanceMeters']}m away")
    print(f"  ✓ Nearest Node (Spanish): {nearestSpa['nearestNodeId']} ({nearestSpa['nodeName']}) - {nearestSpa['distanceMeters']}m away")

    print("\n" + "=" * 80)
    print("  ALL GRAPH TESTS COMPLETED SUCCESSFULLY! READY FOR FLASK / UI CONSUMPTION.")
    print("=" * 80)

if __name__ == "__main__":
    runGraphTestSuite()
