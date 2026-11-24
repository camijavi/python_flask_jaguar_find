"""
testGpsLocationDetection.py
================================================================================
Automated verification suite for GPS Location Detection (Building Boundaries,
Multi-Floor Inference, Confidence Scoring, Fallback Catalogs & Flask REST APIs).
================================================================================
"""

import sys
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

from backend.app import createApp
from backend.graph.geoUtils import CampusGeoUtils
from backend.graph.buildingBoundaries import (
    BUILDING_BOUNDARIES,
    BEACON_REGISTRY,
    getBuildingBoundary,
    resolveBeacon,
    evaluateAllBuildingBoundaries,
)
from backend.graph.navigationService import globalNavigationService
from backend.subgraphs import getAllBuildingSubgraphs


def runGpsDetectionTests():
    print("=" * 80)
    print("  GPS LOCATION DETECTION VERIFICATION SUITE (BOUNDARIES, FLOOR, FALLBACK)")
    print("=" * 80)

    # ------------------------------------------------------------------
    # 1. Ray-Casting & Building Coordinate Boundaries (Polygons & Radii)
    # ------------------------------------------------------------------
    print("\n[TEST 1] Building Coordinate Boundaries (Polygons & Radius Checks):")
    assert len(BUILDING_BOUNDARIES) >= 26, f"Expected >= 26 boundaries, got {len(BUILDING_BOUNDARIES)}"

    # Verify axis-aligned rectangle ray-casting works accurately
    rect = [
        (12.108600, -86.257000),
        (12.108600, -86.256800),
        (12.108400, -86.256800),
        (12.108400, -86.257000),
    ]
    assert CampusGeoUtils.isPointInPolygon(12.108500, -86.256900, rect) is True
    assert CampusGeoUtils.isPointInPolygon(12.108500, -86.257100, rect) is False
    assert CampusGeoUtils.isPointInPolygon(12.108500, -86.256700, rect) is False
    assert CampusGeoUtils.distanceToPolygonMeters(12.108500, -86.256900, rect) == 0.0
    assert CampusGeoUtils.distanceToPolygonMeters(12.108500, -86.257100, rect) > 5.0

    # Verify radius boundary check for Main Parking
    mp = getBuildingBoundary("mainParking")
    assert mp is not None and mp.boundaryType == "radius"
    evIn = mp.evaluatePoint(12.109617, -86.256553)
    assert evIn["isInsideBoundary"] is True and evIn["distanceToBoundaryMeters"] == 0.0
    evOut = mp.evaluatePoint(12.108500, -86.256553)
    assert evOut["isInsideBoundary"] is False and evOut["distanceToBoundaryMeters"] > 50.0

    # Verify Building O North Annex polygon and Sports Zone Baseball Stadium annex polygon
    bO = getBuildingBoundary("buildingO")
    evOAnnex = bO.evaluatePoint(12.108229, -86.257948)  # Sala de Maestros FIA (Anexo Norte)
    assert evOAnnex["isInsideBoundary"] is True and evOAnnex["matchedZone"] == "north_annex"

    bSports = getBuildingBoundary("sportsZone")
    evBaseball = bSports.evaluatePoint(12.107238, -86.258449)
    assert evBaseball["isInsideBoundary"] is True and evBaseball["matchedZone"] == "baseball_stadium"
    evSoccerCenter = bSports.evaluatePoint(12.108350, -86.258300)
    assert evSoccerCenter["isInsideBoundary"] is True and evSoccerCenter["matchedZone"] == "main"

    # Verify all 18 subgraphs have matching boundaries
    for bid in getAllBuildingSubgraphs():
        assert bid in BUILDING_BOUNDARIES, f"Missing boundary for subgraph {bid}"
    print(f"  [OK] Verified {len(BUILDING_BOUNDARIES)} building polygons/radii + annex footprints.")

    # ------------------------------------------------------------------
    # 2. High Confidence ("Where I think you are") — Single-Floor Building
    # ------------------------------------------------------------------
    print("\n[TEST 2] High Confidence Single-Floor Detection ('Where I think you are'):")
    libMatch = globalNavigationService.findNearestGpsNode(
        12.109547, -86.257996, accuracyMeters=6.0, lang="eng"
    )
    assert libMatch["isWithinCampus"] is True
    assert libMatch["nearestNodeId"] == "buildingI"
    assert libMatch["boundaryMatch"]["isInsideBoundary"] is True
    assert libMatch["boundaryMatch"]["boundaryType"] == "polygon"
    assert libMatch["floorDetection"]["isMultiFloor"] is False
    assert libMatch["floorDetection"]["detectedFloor"] == 1
    assert libMatch["floorDetection"]["source"] == "single_floor"
    assert libMatch["confidence"] == "high", f"Expected high confidence, got {libMatch['confidence']} ({libMatch['confidenceReasons']})"
    assert libMatch["needsManualFallback"] is False
    assert libMatch["estimatedLocation"]["isExactSpotConfident"] is True
    assert len(libMatch["buildingLocationsByFloor"]["1"]) == 15
    print(f"  [OK] High confidence match: {libMatch['nodeName']} | conf={libMatch['confidence']} | floor=1 | locations={len(libMatch['buildingLocations'])}")

    # ------------------------------------------------------------------
    # 3. Multi-Floor Building Without Altitude/Beacon -> Prompt + Clean Floor 1 Default + Full Fallback
    # ------------------------------------------------------------------
    print("\n[TEST 3] Multi-Floor Building (No Reliable Vertical Data -> Prompt, Floor 1 Default & All Locations):")
    pMatch = globalNavigationService.findNearestGpsNode(
        12.107492, -86.257090, accuracyMeters=7.0, lang="eng"
    )
    assert pMatch["nearestNodeId"] == "buildingP"
    assert pMatch["boundaryMatch"]["isInsideBoundary"] is True
    assert pMatch["buildingConfidence"] == "high"
    assert pMatch["floorDetection"]["isMultiFloor"] is True
    assert pMatch["floorDetection"]["detectedFloor"] is None
    assert pMatch["floorDetection"]["defaultFloor"] == 1
    assert pMatch["floorDetection"]["source"] == "prompt_required"
    assert pMatch["needsFloorSelection"] is True
    assert pMatch["needsManualFallback"] is True
    assert pMatch["fallbackReason"] == "multi_floor_unknown"
    assert pMatch["confidence"] == "medium"
    assert pMatch["availableFloors"] == [1, 2, 3, 4, 5]
    # Verify ALL floors and ALL rooms in Building P are returned for manual selection
    byFl = pMatch["buildingLocationsByFloor"]
    assert set(byFl.keys()) == {"1", "2", "3", "4", "5"}
    assert len(byFl["1"]) >= 14 and len(byFl["2"]) >= 12 and len(byFl["3"]) >= 11
    print(
        f"  [OK] Building P detected: buildingConf={pMatch['buildingConfidence']}, "
        f"floorPrompt={pMatch['needsFloorSelection']}, defaultFloor={pMatch['floorDetection']['defaultFloor']}, "
        f"floors={pMatch['availableFloors']}, totalRooms={len(pMatch['buildingLocations'])}"
    )

    # ------------------------------------------------------------------
    # 4. Multi-Floor Building With Unreliable vs Reliable Altitude
    # ------------------------------------------------------------------
    print("\n[TEST 4] Indoor Altitude Reliability Filtering (Reject Noisy GPS Altitude, Accept Calibrated Altitude):")
    # 4a. Unreliable indoor GPS altitude (altitudeAccuracy = 15m > 4m) -> MUST reject and prompt
    noisyAlt = globalNavigationService.findNearestGpsNode(
        12.107492, -86.257090, accuracyMeters=6.0,
        altitudeMeters=138.5, altitudeAccuracyMeters=15.0, lang="eng"
    )
    assert noisyAlt["floorDetection"]["detectedFloor"] is None
    assert noisyAlt["floorDetection"]["altitudeRejectedReason"] == "unreliable_indoor_altitude"
    assert noisyAlt["needsFloorSelection"] is True
    print(f"  [OK] Rejected noisy indoor altitude (+/-15m): reason={noisyAlt['floorDetection']['altitudeRejectedReason']}")

    # 4b. Altitude without altitudeAccuracy -> MUST reject
    noAccAlt = globalNavigationService.findNearestGpsNode(
        12.107492, -86.257090, accuracyMeters=6.0,
        altitudeMeters=138.5, altitudeAccuracyMeters=None, lang="eng"
    )
    assert noAccAlt["floorDetection"]["detectedFloor"] is None
    assert noAccAlt["floorDetection"]["altitudeRejectedReason"] == "unreliable_indoor_altitude"

    # 4c. Reliable calibrated/barometric altitude (138.5m = base 135.0m + 1 * 3.5m -> Floor 2, accuracy=1.5m)
    goodAlt = globalNavigationService.findNearestGpsNode(
        12.107492, -86.257090, accuracyMeters=6.0,
        altitudeMeters=138.5, altitudeAccuracyMeters=1.5, lang="eng"
    )
    assert goodAlt["nearestNodeId"] == "buildingP"
    assert goodAlt["floorDetection"]["detectedFloor"] == 2
    assert goodAlt["floorDetection"]["source"] == "altitude"
    assert goodAlt["floorDetection"]["confidence"] == "high"
    assert goodAlt["needsFloorSelection"] is False
    assert goodAlt["confidence"] == "high"
    assert goodAlt["nearestSpecificNodeId"] == "p_room_205"
    print(f"  [OK] Accepted reliable altitude (138.5m +/-1.5m): Floor {goodAlt['floorDetection']['detectedFloor']} -> {goodAlt['nodeName']} (conf={goodAlt['confidence']})")

    # ------------------------------------------------------------------
    # 5. Multi-Floor Building With Indoor Beacon Data & User Floor Selection
    # ------------------------------------------------------------------
    print("\n[TEST 5] Beacon Floor Inference & Explicit User Floor Selection:")
    assert resolveBeacon("uam-c-f3") is not None
    beaconMatch = globalNavigationService.findNearestGpsNode(
        12.108415, -86.257020, accuracyMeters=8.0, beaconId="UAM-C-F3", lang="spa"
    )
    assert beaconMatch["nearestNodeId"] == "buildingC"
    assert beaconMatch["floorDetection"]["detectedFloor"] == 3
    assert beaconMatch["floorDetection"]["source"] == "beacon"
    assert beaconMatch["needsFloorSelection"] is False
    assert beaconMatch["confidence"] == "high"
    assert beaconMatch["bestMatch"]["floorLevel"] == 3
    print(f"  [OK] Beacon UAM-C-F3 resolved: {beaconMatch['nodeName']} (Floor {beaconMatch['floorDetection']['detectedFloor']}, conf={beaconMatch['confidence']})")

    # Explicit user floor hint
    userFlMatch = globalNavigationService.findNearestGpsNode(
        12.107492, -86.257090, accuracyMeters=6.0, floorHint=3, lang="spa"
    )
    assert userFlMatch["floorDetection"]["detectedFloor"] == 3
    assert userFlMatch["floorDetection"]["source"] == "user_selected"
    assert userFlMatch["bestMatch"]["floorLevel"] == 3
    assert userFlMatch["confidence"] == "high"
    print(f"  [OK] User floor hint=3 resolved: {userFlMatch['nodeName']} (conf={userFlMatch['confidence']})")

    # ------------------------------------------------------------------
    # 6. Poor GPS Accuracy -> Low Confidence & Full Manual Fallback
    # ------------------------------------------------------------------
    print("\n[TEST 6] Poor GPS Accuracy -> Low Confidence & Complete Manual Fallback:")
    poorAcc = globalNavigationService.findNearestGpsNode(
        12.109547, -86.257996, accuracyMeters=55.0, lang="eng"
    )
    assert poorAcc["confidence"] == "low"
    assert poorAcc["needsManualFallback"] is True
    assert poorAcc["fallbackReason"] == "low_gps_accuracy"
    assert len(poorAcc["buildingLocations"]) == 15
    assert len(poorAcc["topCandidates"]) >= 2
    print(f"  [OK] Poor accuracy (+/-55m) triggered fallback: conf={poorAcc['confidence']}, reason={poorAcc['fallbackReason']}, options={len(poorAcc['buildingLocations'])}")

    # ------------------------------------------------------------------
    # 7. Flask REST API Endpoints Verification
    # ------------------------------------------------------------------
    print("\n[TEST 7] Flask REST API Endpoints (/api/map/nearest-gps, /boundaries, /buildings/<id>/locations):")
    app = createApp()
    client = app.test_client()

    # 7a. Missing params -> 400
    r400 = client.get("/api/map/nearest-gps")
    assert r400.status_code == 400

    # 7b. High confidence single-floor API response
    rHigh = client.get("/api/map/nearest-gps?lat=12.109547&lng=-86.257996&accuracy=6&lang=eng")
    assert rHigh.status_code == 200
    dHigh = rHigh.get_json()
    assert dHigh["success"] is True and dHigh["outsideCampus"] is False
    assert dHigh["nearest"]["confidence"] == "high"
    assert dHigh["nearest"]["estimatedLocation"]["isExactSpotConfident"] is True

    # 7c. Multi-floor with calibrated altitude over HTTP
    rAlt = client.get("/api/map/nearest-gps?lat=12.107492&lng=-86.257090&accuracy=6&altitude=138.5&altitudeAccuracy=1.5&lang=eng")
    assert rAlt.status_code == 200
    dAlt = rAlt.get_json()
    assert dAlt["nearest"]["floorDetection"]["detectedFloor"] == 2
    assert dAlt["nearest"]["floorDetection"]["source"] == "altitude"
    assert dAlt["nearest"]["confidence"] == "high"

    # 7d. Multi-floor with beacon over HTTP
    rBeacon = client.get("/api/map/nearest-gps?lat=12.108415&lng=-86.257020&accuracy=8&beaconId=UAM-C-F3&lang=spa")
    assert rBeacon.status_code == 200
    dBeacon = rBeacon.get_json()
    assert dBeacon["nearest"]["floorDetection"]["detectedFloor"] == 3
    assert dBeacon["nearest"]["floorDetection"]["source"] == "beacon"

    # 7e. Outside campus response includes campusEntrances fallback list
    rOut = client.get("/api/map/nearest-gps?lat=12.1270&lng=-86.2650&lang=eng")
    assert rOut.status_code == 200
    dOut = rOut.get_json()
    assert dOut["success"] is False and dOut["outsideCampus"] is True
    assert len(dOut["campusEntrances"]) >= 5

    # 7f. GET /api/map/boundaries
    rBound = client.get("/api/map/boundaries?lang=eng")
    assert rBound.status_code == 200
    dBound = rBound.get_json()
    assert dBound["success"] is True and dBound["count"] >= 26

    # 7g. GET /api/map/buildings/buildingC/locations (all floors & filtered floor)
    rLocAll = client.get("/api/map/buildings/buildingC/locations?lang=spa")
    assert rLocAll.status_code == 200
    dLocAll = rLocAll.get_json()
    assert dLocAll["success"] is True and dLocAll["isMultiFloor"] is True
    assert dLocAll["availableFloors"] == [1, 2, 3]
    assert dLocAll["totalLocations"] >= 35

    rLocF2 = client.get("/api/map/buildings/buildingC/locations?floor=2&lang=spa")
    assert rLocF2.status_code == 200
    dLocF2 = rLocF2.get_json()
    assert all(loc["floorLevel"] == 2 for loc in dLocF2["locations"])

    # 7h. Unknown building -> 404
    r404 = client.get("/api/map/buildings/unknownBuilding999/locations")
    assert r404.status_code == 404

    # 7i. Map screen HTML includes gpsLocationDetector.js and GPS panel elements
    rHtml = client.get("/")
    assert rHtml.status_code == 200
    html = rHtml.get_data(as_text=True)
    assert "gpsLocationDetector.js" in html
    assert "gpsEstimatedCard" in html
    assert "gpsFallbackLocationsSection" in html
    assert "gpsLocationsList" in html
    print("  [OK] All REST API endpoints & rendered HTML elements verified!")

    print("\n" + "=" * 80)
    print("  ALL GPS LOCATION DETECTION TESTS PASSED!")
    print("=" * 80)


if __name__ == "__main__":
    runGpsDetectionTests()
