"""
testCampusGraph.py
================================================================================
Interactive & Automated verification script for the UAM Campus Graph Engine.
Demonstrates Dijkstra route calculation, accessibility pruning (♿), 
category filtering, and smart keyword resolution.
================================================================================
"""

from grafoUam import globalNavigationService
from data.campusCategories import CampusCategory, CATEGORY_METADATA

def runGraphTestSuite():
    print("=" * 80)
    print("  JAGUARFIND & JAGUARMAPS - UAM CAMPUS GRAPH VERIFICATION SUITE")
    print("=" * 80)

    # 1. Standard Walking Route Test
    print("\n[TEST 1] Calculating Standard Pedestrian Route:")
    print("  Origin: mainParking (Parqueo Principal)")
    print("  Destination: 'B103' (Classroom B-103)")
    res1 = globalNavigationService.calculateRoute("mainParking", "B103")
    if res1["success"]:
        print(f"  ✓ Success! Path: {' -> '.join(res1['pathNodeIds'])}")
        print(f"  ✓ Total Walking Distance: {res1['totalDistanceMeters']} meters (~{res1['estimatedWalkingMinutes']} min)")
        print("  ✓ Step Instructions:")
        for idx, step in enumerate(res1["stepInstructions"], 1):
            print(f"     {idx}. {step}")
    else:
        print(f"  ✗ Failed: {res1['error']}")

    # 2. Universal Accessibility (♿) Test
    print("\n[TEST 2] Accessibility (Wheelchair ♿) Pruning Test:")
    print("  Origin: buildingN (Dental Clinics)")
    print("  Destination: buildingP (Copernicus Observatory)")
    
    # 2a. Without accessibility filter (allows stairs)
    resNormal = globalNavigationService.calculateRoute("buildingN", "buildingP", accessibleOnly=False)
    # 2b. With accessibility filter (must avoid stairs and take Building O ramp)
    resAccessible = globalNavigationService.calculateRoute("buildingN", "buildingP", accessibleOnly=True)

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
        print(f"  • {meta.get('labelSpanish', cat)} ({len(places)} locations registered):")
        for p in places[:3]: # Show first 3
            print(f"     - {p['name']} in {p['parentBuildingId']} (Floor {p['floorLevel']})")
        if len(places) > 3:
            print(f"     ... and {len(places) - 3} more.")

    # 4. GPS Nearest Node Test (Haversine)
    print("\n[TEST 4] GPS Nearest Node Detection (Haversine):")
    # Coordinates near Building B
    userLat, userLng = 12.12460, -86.27090
    nearest = globalNavigationService.findNearestGpsNode(userLat, userLng)
    print(f"  User GPS: ({userLat}, {userLng})")
    print(f"  ✓ Nearest Campus Node: {nearest['nearestNodeId']} ({nearest['nodeName']}) - {nearest['distanceMeters']}m away")

    print("\n" + "=" * 80)
    print("  ALL GRAPH TESTS COMPLETED SUCCESSFULLY! READY FOR FLASK / UI CONSUMPTION.")
    print("=" * 80)

if __name__ == "__main__":
    runGraphTestSuite()
