"""
gpsMatcher.py
================================================================================
GLOBAL CAMPUS GPS-TO-GRAPH MATCHING ENGINE (BOUNDARIES + MULTI-FLOOR + FALLBACK)
================================================================================
Matches a live user's WGS84 GPS coordinate against the UAM campus hierarchy:
  1. Campus perimeter validation (Ray-Casting + edge buffer)
  2. Defined building coordinate boundaries (WGS84 polygons & radius checks via
     `buildingBoundaries.py`) to determine the current building first
  3. Multi-floor resolution:
       - User-selected floor (`floorHint`)
       - Indoor beacon data (`beaconId` / `beaconFloor`)
       - Calibrated altitude inference ONLY when vertical accuracy is reliable
         indoors (<= 4.0m); noisy browser GPS altitude is rejected cleanly
       - Clean default (Floor 1) + floor prompt when vertical data is unavailable
  4. Confidence scoring (`high` | `medium` | `low`) for "Where I think you are"
  5. Complete manual fallback payload: returns ALL available location options
     for the detected building grouped by floor (`buildingLocationsByFloor`)
================================================================================
"""

from typing import Dict, List, Optional, Any
import unicodedata

from .directedGraph import DirectedGraph
from .geoUtils import CampusGeoUtils
from .buildingBoundaries import (
    BUILDING_BOUNDARIES,
    evaluateAllBuildingBoundaries,
    getBuildingBoundary,
    resolveBeacon,
)
from .pedestrianWalkwayGraph import globalPedestrianWalkwayGraph, WALKWAY_LANDMARKS


def _normKey(text: str) -> str:
    decomposed = unicodedata.normalize("NFD", str(text or "").strip().lower())
    return "".join(ch for ch in decomposed if unicodedata.category(ch) != "Mn")


class GlobalGpsMatcher:
    def __init__(self, macroGraph: DirectedGraph, walkwayGraph: DirectedGraph = globalPedestrianWalkwayGraph):
        self.macroGraph = macroGraph
        self.walkwayGraph = walkwayGraph

    def getBuildingLocations(
        self,
        buildingId: str,
        userLat: Optional[float] = None,
        userLng: Optional[float] = None,
        floor: Optional[int] = None,
        lang: str = "spa",
    ) -> Dict[str, Any]:
        """
        Returns ALL available location options for a given building/zone grouped by floor,
        sorted by proximity when user GPS coordinates are provided.
        Used both in GPS match fallback payloads and when the user switches buildings manually.
        """
        from backend.subgraphs import getBuildingSubgraph
        from backend.data.placesCatalog import PLACES_CATALOG
        from backend.data.campusLocalization import getLocalizedPlaceName

        macroNode = self.macroGraph.getNode(buildingId)
        sg = getBuildingSubgraph(buildingId)
        boundary = getBuildingBoundary(buildingId)

        buildingName = (
            macroNode.getName(lang)
            if macroNode
            else (sg.getName(lang) if sg else buildingId)
        )

        if sg and sg.floors:
            availableFloors = sorted(list(sg.floors))
        elif boundary and boundary.floors:
            availableFloors = sorted(list(boundary.floors))
        else:
            availableFloors = [1]

        locations: List[Dict[str, Any]] = []
        seenKeys = set()
        orderMap: Dict[int, int] = {}

        def _appendLocation(entry: Dict[str, Any]) -> None:
            key = (_normKey(entry["name"]), int(entry["floorLevel"]))
            if key in seenKeys:
                return
            seenKeys.add(key)
            orderMap[id(entry)] = len(locations)
            locations.append(entry)

        # 1. All indoor nodes from the building's subgraph (classrooms, offices, labs, restrooms, etc.)
        if sg:
            for node in sg.getAllNodes():
                dist = None
                if userLat is not None and userLng is not None and node.latitude and node.longitude:
                    dist = round(
                        CampusGeoUtils.calculateHaversineDistance(
                            userLat, userLng, node.latitude, node.longitude
                        ),
                        1,
                    )
                _appendLocation({
                    "nodeId": node.nodeId,
                    "placeId": node.nodeId,
                    "name": node.getName(lang),
                    "buildingId": sg.macroNodeId,
                    "buildingName": buildingName,
                    "floorLevel": int(getattr(node, "floorLevel", 1) or 1),
                    "category": node.category,
                    "distanceMeters": dist,
                    "isAccessible": node.category != "stairs",
                    "lat": node.latitude,
                    "lng": node.longitude,
                    "source": "subgraph",
                    "isRecommended": False,
                })

        # 2. Supplementary places from PLACES_CATALOG for zones without an indoor subgraph
        if not sg:
            for place in PLACES_CATALOG:
                if (place.get("parentBuildingId") or "").lower() != buildingId.lower():
                    continue
                pLat = place.get("latitude") or (macroNode.latitude if macroNode else None)
                pLng = place.get("longitude") or (macroNode.longitude if macroNode else None)
                dist = None
                if userLat is not None and userLng is not None and pLat and pLng:
                    dist = round(
                        CampusGeoUtils.calculateHaversineDistance(userLat, userLng, pLat, pLng),
                        1,
                    )
                _appendLocation({
                    "nodeId": place.get("placeId"),
                    "placeId": place.get("placeId"),
                    "name": getLocalizedPlaceName(place, lang),
                    "buildingId": buildingId,
                    "buildingName": buildingName,
                    "floorLevel": int(place.get("floorLevel", 1) or 1),
                    "category": place.get("category", "other"),
                    "distanceMeters": dist,
                    "isAccessible": bool(place.get("isAccessible", True)),
                    "lat": pLat,
                    "lng": pLng,
                    "source": "catalog",
                    "isRecommended": False,
                })

        # 3. Outdoor walkway landmarks associated with this building/zone (when no indoor subgraph exists)
        if not sg:
            for wNodeId in WALKWAY_LANDMARKS:
                wNode = self.walkwayGraph.getNode(wNodeId)
                if not wNode:
                    continue
                if (wNode.buildingId or wNodeId) != buildingId:
                    continue
                dist = None
                if userLat is not None and userLng is not None:
                    dist = round(
                        CampusGeoUtils.calculateHaversineDistance(
                            userLat, userLng, wNode.latitude, wNode.longitude
                        ),
                        1,
                    )
                _appendLocation({
                    "nodeId": wNodeId,
                    "placeId": wNodeId,
                    "name": wNode.getName(lang),
                    "buildingId": buildingId,
                    "buildingName": buildingName,
                    "floorLevel": int(getattr(wNode, "floorLevel", 1) or 1),
                    "category": wNode.category,
                    "distanceMeters": dist,
                    "isAccessible": True,
                    "lat": wNode.latitude,
                    "lng": wNode.longitude,
                    "source": "walkway",
                    "isRecommended": False,
                })

        # 4. Always ensure the macro building/zone itself is available if no other entries exist
        if macroNode and not locations:
            dist = None
            if userLat is not None and userLng is not None:
                dist = round(
                    CampusGeoUtils.calculateHaversineDistance(
                        userLat, userLng, macroNode.latitude, macroNode.longitude
                    ),
                    1,
                )
            _appendLocation({
                "nodeId": macroNode.nodeId,
                "placeId": macroNode.nodeId,
                "name": macroNode.getName(lang),
                "buildingId": macroNode.nodeId,
                "buildingName": buildingName,
                "floorLevel": int(getattr(macroNode, "floorLevel", 1) or 1),
                "category": macroNode.category,
                "distanceMeters": dist,
                "isAccessible": True,
                "lat": macroNode.latitude,
                "lng": macroNode.longitude,
                "source": "macro",
                "isRecommended": True,
            })

        # Sort locations by floor, then proximity when GPS coordinates are provided,
        # strictly preserving the building's defined left-to-right order (buildings.txt)
        # when GPS coordinates are absent or distances tie.
        def _sortKey(item: Dict[str, Any]):
            d = item["distanceMeters"]
            orderIdx = orderMap.get(id(item), 0)
            if d is not None:
                return (item["floorLevel"], d, orderIdx)
            return (item["floorLevel"], orderIdx)

        locations.sort(key=_sortKey)

        # Group by floor and flag the closest option per floor as recommended
        locationsByFloor: Dict[str, List[Dict[str, Any]]] = {
            str(fl): [] for fl in availableFloors
        }
        for loc in locations:
            flKey = str(loc["floorLevel"])
            if flKey not in locationsByFloor:
                locationsByFloor[flKey] = []
                availableFloors = sorted(list(set(availableFloors + [loc["floorLevel"]])))
            locationsByFloor[flKey].append(loc)

        for flKey, flItems in locationsByFloor.items():
            if flItems:
                flItems[0]["isRecommended"] = True

        if floor is not None:
            filteredLocations = list(locationsByFloor.get(str(floor), []))
        else:
            filteredLocations = locations

        return {
            "buildingId": buildingId,
            "buildingName": buildingName,
            "availableFloors": availableFloors,
            "isMultiFloor": len(availableFloors) > 1,
            "totalLocations": len(filteredLocations),
            "locations": filteredLocations,
            "locationsByFloor": locationsByFloor,
        }

    def getCampusEntranceOptions(self, lang: str = "spa") -> List[Dict[str, Any]]:
        """Returns quick-pick campus entrance and central landmark options for off-campus / error fallback."""
        priorityIds = [
            "mainParking",
            "northGate",
            "northeastGate",
            "buildingA",
            "buildingK",
            "buildingC",
            "buildingI",
        ]
        options = []
        for nid in priorityIds:
            node = self.macroGraph.getNode(nid)
            if not node:
                continue
            options.append({
                "nodeId": nid,
                "placeId": nid,
                "buildingId": nid,
                "name": node.getName(lang),
                "buildingName": node.getName(lang),
                "category": node.category,
                "floorLevel": 1,
                "lat": node.latitude,
                "lng": node.longitude,
            })
        return options

    def matchLocation(
        self,
        userLat: float,
        userLng: float,
        accuracyMeters: Optional[float] = None,
        floorHint: Optional[int] = None,
        lang: str = "spa",
        altitudeMeters: Optional[float] = None,
        altitudeAccuracyMeters: Optional[float] = None,
        beaconId: Optional[str] = None,
        beaconFloor: Optional[int] = None,
    ) -> dict:
        from backend.subgraphs import getAllBuildingSubgraphs

        isWithinCampus = CampusGeoUtils.isWithinCampusPerimeter(userLat, userLng, bufferMeters=30.0)
        svgX, svgY = CampusGeoUtils.gpsToSvg(userLat, userLng)
        clampedX = round(max(40.0, min(1160.0, svgX)), 1)
        clampedY = round(max(15.0, min(835.0, svgY)), 1)

        allMatches: List[Dict[str, Any]] = []
        subgraphs = getAllBuildingSubgraphs()

        # ------------------------------------------------------------------
        # 1. Gather distances to all graph nodes (Subgraphs, Walkways, Macro)
        # ------------------------------------------------------------------
        for buildingId, sg in subgraphs.items():
            macroNode = self.macroGraph.getNode(sg.macroNodeId)
            buildingName = macroNode.getName(lang) if macroNode else sg.getName(lang)
            for node in sg.getAllNodes():
                if not node.latitude or not node.longitude:
                    continue
                dist = CampusGeoUtils.calculateHaversineDistance(userLat, userLng, node.latitude, node.longitude)
                allMatches.append({
                    "nodeId": node.nodeId,
                    "placeId": node.nodeId,
                    "name": node.getName(lang),
                    "buildingId": sg.macroNodeId,
                    "buildingName": buildingName,
                    "subgraphId": buildingId,
                    "floorLevel": int(getattr(node, "floorLevel", 1) or 1),
                    "availableFloors": list(sg.floors),
                    "distanceMeters": round(dist, 1),
                    "lat": node.latitude,
                    "lng": node.longitude,
                    "x": node.xSvg,
                    "y": node.ySvg,
                    "source": "subgraph",
                    "category": node.category,
                })

        for wNodeId in WALKWAY_LANDMARKS:
            wNode = self.walkwayGraph.getNode(wNodeId)
            if not wNode:
                continue
            dist = CampusGeoUtils.calculateHaversineDistance(userLat, userLng, wNode.latitude, wNode.longitude)
            bId = wNode.buildingId or wNodeId
            macroNode = self.macroGraph.getNode(bId)
            bName = macroNode.getName(lang) if macroNode else wNode.getName(lang)
            sg = subgraphs.get(bId)
            allMatches.append({
                "nodeId": wNodeId,
                "placeId": wNodeId,
                "name": wNode.getName(lang),
                "buildingId": bId,
                "buildingName": bName,
                "subgraphId": bId if sg else None,
                "floorLevel": int(getattr(wNode, "floorLevel", 1) or 1),
                "availableFloors": list(sg.floors) if sg else [1],
                "distanceMeters": round(dist, 1),
                "lat": wNode.latitude,
                "lng": wNode.longitude,
                "x": wNode.xSvg,
                "y": wNode.ySvg,
                "source": "walkway",
                "category": wNode.category,
            })

        for nodeId, node in self.macroGraph.nodes.items():
            dist = CampusGeoUtils.calculateHaversineDistance(userLat, userLng, node.latitude, node.longitude)
            sg = subgraphs.get(nodeId)
            allMatches.append({
                "nodeId": nodeId,
                "placeId": nodeId,
                "name": node.getName(lang),
                "buildingId": nodeId,
                "buildingName": node.getName(lang),
                "subgraphId": nodeId if sg else None,
                "floorLevel": 1,
                "availableFloors": list(sg.floors) if sg else [1],
                "distanceMeters": round(dist, 1),
                "lat": node.latitude,
                "lng": node.longitude,
                "x": node.xSvg,
                "y": node.ySvg,
                "source": "macro",
                "category": node.category,
            })

        allMatches.sort(key=lambda m: m["distanceMeters"])

        # Map each buildingId -> its nearest node across all tiers
        nearestByBuilding: Dict[str, Dict[str, Any]] = {}
        for m in allMatches:
            bId = m["buildingId"]
            if bId not in nearestByBuilding:
                nearestByBuilding[bId] = m

        # ------------------------------------------------------------------
        # 2. Evaluate defined Building Coordinate Boundaries (Polygons / Radii)
        # ------------------------------------------------------------------
        boundaryEvals = evaluateAllBuildingBoundaries(userLat, userLng)
        for ev in boundaryEvals:
            bNode = self.macroGraph.getNode(ev["buildingId"])
            ev["buildingName"] = bNode.getName(lang) if bNode else ev["buildingId"]
            nearestInB = nearestByBuilding.get(ev["buildingId"])
            ev["nearestNodeDistanceMeters"] = (
                nearestInB["distanceMeters"] if nearestInB else ev["distanceToCenterMeters"]
            )

        strictBoundaryHits = [ev for ev in boundaryEvals if ev["isInsideBoundary"]]
        bufferBoundaryHits = [ev for ev in boundaryEvals if ev["withinBuffer"]]

        # Sort overlapping strict hits by closest real node inside each matched building,
        # breaking ties by distance to building center
        strictBoundaryHits.sort(
            key=lambda ev: (ev["nearestNodeDistanceMeters"], ev["distanceToCenterMeters"])
        )
        bufferBoundaryHits.sort(
            key=lambda ev: (
                0 if ev["isInsideBoundary"] else 1,
                ev["nearestNodeDistanceMeters"],
                ev["distanceToBoundaryMeters"],
            )
        )

        # Optional indoor beacon lookup
        beaconMatch = resolveBeacon(beaconId)
        beaconMatchedBuilding = False

        detectedBuildingId: Optional[str] = None
        activeBoundaryEval: Optional[Dict[str, Any]] = None

        if beaconMatch and beaconMatch.get("buildingId") in self.macroGraph.nodes:
            detectedBuildingId = beaconMatch["buildingId"]
            beaconMatchedBuilding = True
            activeBoundaryEval = next(
                (ev for ev in boundaryEvals if ev["buildingId"] == detectedBuildingId),
                None,
            )
        elif strictBoundaryHits:
            activeBoundaryEval = strictBoundaryHits[0]
            detectedBuildingId = activeBoundaryEval["buildingId"]
        elif bufferBoundaryHits:
            activeBoundaryEval = bufferBoundaryHits[0]
            detectedBuildingId = activeBoundaryEval["buildingId"]
        elif allMatches:
            detectedBuildingId = allMatches[0]["buildingId"]
            activeBoundaryEval = next(
                (ev for ev in boundaryEvals if ev["buildingId"] == detectedBuildingId),
                None,
            )

        # Ensure detectedBuildingId resolves cleanly to a macro node
        if detectedBuildingId and detectedBuildingId not in self.macroGraph.nodes:
            detectedBuildingId = "mainParking"

        boundaryObj = getBuildingBoundary(detectedBuildingId) if detectedBuildingId else None
        detectedSg = subgraphs.get(detectedBuildingId) if detectedBuildingId else None

        if detectedSg and detectedSg.floors:
            availableFloors = sorted(list(detectedSg.floors))
        elif boundaryObj and boundaryObj.floors:
            availableFloors = sorted(list(boundaryObj.floors))
        else:
            availableFloors = [1]

        isMultiFloor = len(availableFloors) > 1
        defaultFloor = availableFloors[0] if availableFloors else 1

        # ------------------------------------------------------------------
        # 3. Multi-Floor Detection Cascade (User > Beacon > Reliable Altitude > Prompt/Default)
        # ------------------------------------------------------------------
        detectedFloor: Optional[int] = None
        floorSource = "single_floor"
        floorConfidence = "high"
        needsFloorSelection = False
        altitudeRejectedReason: Optional[str] = None

        nearestForDetectedBuilding = (
            nearestByBuilding.get(detectedBuildingId) if detectedBuildingId else None
        )
        distToDetectedBuilding = (
            nearestForDetectedBuilding["distanceMeters"]
            if nearestForDetectedBuilding
            else (activeBoundaryEval["distanceToBoundaryMeters"] if activeBoundaryEval else 999.0)
        )

        if not isMultiFloor:
            detectedFloor = defaultFloor
            floorSource = "single_floor"
            floorConfidence = "high"
            needsFloorSelection = False
        else:
            # Priority 1: Explicit user floor confirmation/hint
            if floorHint is not None and floorHint in availableFloors:
                detectedFloor = int(floorHint)
                floorSource = "user_selected"
                floorConfidence = "high"
                needsFloorSelection = False
            # Priority 2: Indoor beacon data (BLE / Wi-Fi / NFC)
            elif beaconMatch and beaconMatch.get("buildingId") == detectedBuildingId and beaconMatch.get("floorLevel") in availableFloors:
                detectedFloor = int(beaconMatch["floorLevel"])
                floorSource = "beacon"
                floorConfidence = "high"
                needsFloorSelection = False
            elif beaconFloor is not None and beaconFloor in availableFloors:
                detectedFloor = int(beaconFloor)
                floorSource = "beacon"
                floorConfidence = "high"
                needsFloorSelection = False
            # Priority 3: Reliable altitude inference (rejects noisy standard indoor GPS altitude)
            else:
                altEval = (
                    boundaryObj.inferFloorFromAltitude(altitudeMeters, altitudeAccuracyMeters)
                    if boundaryObj
                    else {"inferredFloor": None, "confidence": "low", "rejectedReason": "altitude_unavailable"}
                )
                altitudeRejectedReason = altEval.get("rejectedReason")
                if altEval.get("inferredFloor") is not None:
                    detectedFloor = int(altEval["inferredFloor"])
                    floorSource = "altitude"
                    floorConfidence = altEval.get("confidence", "medium")
                    needsFloorSelection = False
                else:
                    # Priority 4: Clean default (Floor 1) + prompt user for floor
                    detectedFloor = None
                    floorSource = "prompt_required"
                    floorConfidence = "low"
                    inOrNearBuilding = bool(
                        (activeBoundaryEval and (activeBoundaryEval["isInsideBoundary"] or activeBoundaryEval["withinBuffer"]))
                        or distToDetectedBuilding <= 35.0
                    )
                    needsFloorSelection = inOrNearBuilding

        # ------------------------------------------------------------------
        # 4. Resolve Best Match Node within Detected Building & Floor
        # ------------------------------------------------------------------
        buildingMatches = [
            m for m in allMatches if m["buildingId"] == detectedBuildingId
        ]
        buildingSubgraphMatches = [
            m for m in buildingMatches if m["source"] == "subgraph"
        ]

        best: Optional[Dict[str, Any]] = None
        if detectedSg and buildingSubgraphMatches:
            targetFloorForBest = detectedFloor if detectedFloor is not None else defaultFloor
            floorFiltered = [
                m for m in buildingSubgraphMatches if m["floorLevel"] == targetFloorForBest
            ]
            if floorFiltered:
                best = dict(floorFiltered[0])
            else:
                best = dict(buildingSubgraphMatches[0])
        elif buildingMatches:
            # Prefer a walkway landmark or macro node inside the matched building/zone
            best = dict(buildingMatches[0])
        elif allMatches:
            best = dict(allMatches[0])

        # Build 1 best candidate per floor for quick floor pills
        floorCandidates: List[Dict[str, Any]] = []
        if detectedSg and len(availableFloors) > 1:
            for fl in availableFloors:
                flMatches = [
                    m for m in buildingSubgraphMatches if m["floorLevel"] == fl
                ]
                if flMatches:
                    topFl = flMatches[0]
                    floorCandidates.append({
                        "floorLevel": fl,
                        "nodeId": topFl["nodeId"],
                        "name": topFl["name"],
                        "buildingId": topFl["buildingId"],
                        "distanceMeters": topFl["distanceMeters"],
                        "roomCount": len(flMatches),
                        "isDefault": fl == defaultFloor,
                    })

        # ------------------------------------------------------------------
        # 5. Top Nearby Buildings & Full Manual Fallback Locations Catalog
        # ------------------------------------------------------------------
        topCandidates: List[Dict[str, Any]] = []
        seenBuildings = set()

        # Put detected building first so topCandidates[0] always reflects the boundary-matched building
        if best:
            seenBuildings.add(best["buildingId"])
            topCandidates.append({
                "nodeId": best["nodeId"],
                "buildingId": best["buildingId"],
                "name": best["name"],
                "buildingName": best["buildingName"],
                "floorLevel": best["floorLevel"],
                "availableFloors": availableFloors,
                "distanceMeters": best["distanceMeters"],
                "source": best["source"],
                "isInsideBoundary": bool(activeBoundaryEval and activeBoundaryEval["isInsideBoundary"]),
                "distanceToBoundaryMeters": (
                    activeBoundaryEval["distanceToBoundaryMeters"]
                    if activeBoundaryEval
                    else best["distanceMeters"]
                ),
            })

        # Next add any other buildings whose polygon/radius+buffer matched
        for ev in bufferBoundaryHits:
            bId = ev["buildingId"]
            if bId in seenBuildings:
                continue
            m = nearestByBuilding.get(bId)
            if not m:
                continue
            seenBuildings.add(bId)
            topCandidates.append({
                "nodeId": m["nodeId"],
                "buildingId": bId,
                "name": m["name"],
                "buildingName": m["buildingName"],
                "floorLevel": m["floorLevel"],
                "availableFloors": list(ev["floors"]),
                "distanceMeters": m["distanceMeters"],
                "source": m["source"],
                "isInsideBoundary": ev["isInsideBoundary"],
                "distanceToBoundaryMeters": ev["distanceToBoundaryMeters"],
            })
            if len(topCandidates) >= 4:
                break

        # Fill remaining slots up to 4 with nearest overall buildings
        if len(topCandidates) < 4:
            for m in allMatches:
                bId = m["buildingId"]
                if bId in seenBuildings:
                    continue
                seenBuildings.add(bId)
                bEval = next((ev for ev in boundaryEvals if ev["buildingId"] == bId), None)
                topCandidates.append({
                    "nodeId": m["nodeId"],
                    "buildingId": bId,
                    "name": m["name"],
                    "buildingName": m["buildingName"],
                    "floorLevel": m["floorLevel"],
                    "availableFloors": m.get("availableFloors", [1]),
                    "distanceMeters": m["distanceMeters"],
                    "source": m["source"],
                    "isInsideBoundary": bool(bEval and bEval["isInsideBoundary"]),
                    "distanceToBoundaryMeters": (
                        bEval["distanceToBoundaryMeters"] if bEval else m["distanceMeters"]
                    ),
                })
                if len(topCandidates) >= 4:
                    break

        # Complete manual location options for the detected building grouped by floor
        buildingLocationsPayload = (
            self.getBuildingLocations(
                detectedBuildingId,
                userLat=userLat,
                userLng=userLng,
                lang=lang,
            )
            if detectedBuildingId
            else {
                "buildingId": None,
                "buildingName": None,
                "availableFloors": [1],
                "isMultiFloor": False,
                "totalLocations": 0,
                "locations": [],
                "locationsByFloor": {},
            }
        )

        # ------------------------------------------------------------------
        # 6. Confidence Scoring ("Where I think you are" vs Manual Fallback)
        # ------------------------------------------------------------------
        confidenceReasons: List[str] = []
        isInsideBoundary = bool(activeBoundaryEval and activeBoundaryEval["isInsideBoundary"])
        withinBuffer = bool(activeBoundaryEval and activeBoundaryEval["withinBuffer"])
        bestDist = best["distanceMeters"] if best else 999.0

        # Check competing building ambiguity
        competingBoundaryAmbiguity = False
        if len(strictBoundaryHits) >= 2:
            # Two overlapping polygons both contain the point; only ambiguous if runner-up node is also very close
            d0 = strictBoundaryHits[0]["nearestNodeDistanceMeters"]
            d1 = strictBoundaryHits[1]["nearestNodeDistanceMeters"]
            if (d1 - d0) <= 6.0:
                competingBoundaryAmbiguity = True
        elif not isInsideBoundary and len(topCandidates) >= 2:
            if (topCandidates[1]["distanceMeters"] - topCandidates[0]["distanceMeters"]) <= 12.0:
                competingBoundaryAmbiguity = True

        poorAccuracy = bool(accuracyMeters is not None and accuracyMeters > 40.0)
        moderateAccuracy = bool(accuracyMeters is not None and 20.0 < accuracyMeters <= 40.0)
        lowAccuracyLegacy = bool(accuracyMeters is not None and accuracyMeters > 15.0)

        # Building-level confidence
        if not isWithinCampus:
            buildingConfidence = "low"
            confidenceReasons.append("outside_campus_perimeter")
        elif beaconMatchedBuilding:
            buildingConfidence = "high"
            confidenceReasons.append("indoor_beacon_match")
        elif poorAccuracy:
            buildingConfidence = "low"
            confidenceReasons.append("poor_gps_accuracy")
        elif isInsideBoundary and not moderateAccuracy and not competingBoundaryAmbiguity:
            buildingConfidence = "high"
            confidenceReasons.append(
                f"inside_building_{activeBoundaryEval['boundaryType']}"
            )
        elif withinBuffer and not moderateAccuracy and bestDist <= 15.0 and not competingBoundaryAmbiguity:
            buildingConfidence = "high"
            confidenceReasons.append("within_building_buffer")
        elif isInsideBoundary or withinBuffer or bestDist <= 28.0:
            buildingConfidence = "medium"
            if competingBoundaryAmbiguity:
                confidenceReasons.append("near_adjacent_building_boundary")
            if moderateAccuracy:
                confidenceReasons.append("moderate_gps_accuracy")
            if not isInsideBoundary and withinBuffer:
                confidenceReasons.append("near_building_edge")
        else:
            buildingConfidence = "low"
            confidenceReasons.append("far_from_defined_buildings")

        # Floor reasons
        if floorSource == "beacon":
            confidenceReasons.append("floor_resolved_by_beacon")
        elif floorSource == "altitude":
            confidenceReasons.append("floor_inferred_by_altitude")
        elif floorSource == "user_selected":
            confidenceReasons.append("floor_confirmed_by_user")
        elif floorSource == "prompt_required":
            confidenceReasons.append("multi_floor_altitude_unreliable")

        # Spot-level confidence
        if not isWithinCampus:
            spotConfidence = "low"
        elif beaconMatchedBuilding and floorConfidence == "high":
            spotConfidence = "high"
        elif (
            buildingConfidence == "high"
            and floorConfidence == "high"
            and bestDist <= 18.0
            and not poorAccuracy
            and not moderateAccuracy
        ):
            spotConfidence = "high"
            confidenceReasons.append("exact_spot_matched")
        elif buildingConfidence in ("high", "medium") and bestDist <= 35.0:
            spotConfidence = "medium"
            if bestDist > 18.0:
                confidenceReasons.append("uncertain_exact_spot_inside_building")
        else:
            spotConfidence = "low"

        # Overall confidence & fallback determination
        isAmbiguous = bool(
            lowAccuracyLegacy
            or competingBoundaryAmbiguity
            or (
                not isInsideBoundary
                and len(topCandidates) >= 2
                and (topCandidates[1]["distanceMeters"] - topCandidates[0]["distanceMeters"]) <= 12.0
            )
        )

        if (
            isWithinCampus
            and buildingConfidence == "high"
            and floorConfidence == "high"
            and spotConfidence == "high"
            and not competingBoundaryAmbiguity
        ):
            confidence = "high"
            confidenceScore = 0.96 if (beaconMatchedBuilding or bestDist <= 8.0) else 0.88
            needsManualFallback = False
            fallbackReason = None
        elif isWithinCampus and buildingConfidence in ("high", "medium"):
            confidence = "medium"
            confidenceScore = 0.68 if buildingConfidence == "high" else 0.52
            needsManualFallback = True
            if needsFloorSelection:
                fallbackReason = "multi_floor_unknown"
            elif floorSource == "altitude" and floorConfidence == "medium":
                fallbackReason = "altitude_floor_uncertain"
            elif competingBoundaryAmbiguity:
                fallbackReason = "ambiguous_building_boundary"
            elif moderateAccuracy:
                fallbackReason = "moderate_gps_accuracy"
            else:
                fallbackReason = "uncertain_indoor_spot"
        else:
            confidence = "low"
            confidenceScore = 0.2 if isWithinCampus else 0.0
            needsManualFallback = True
            if not isWithinCampus:
                fallbackReason = "outside_campus"
            elif poorAccuracy:
                fallbackReason = "low_gps_accuracy"
            else:
                fallbackReason = "far_from_buildings"

        nearestMacroId = detectedBuildingId or (best["buildingId"] if best else None)
        if nearestMacroId and nearestMacroId not in self.macroGraph.nodes:
            nearestMacroId = "mainParking"

        boundaryMatchSummary = {
            "buildingId": nearestMacroId,
            "buildingName": best["buildingName"] if best else None,
            "boundaryType": activeBoundaryEval["boundaryType"] if activeBoundaryEval else "proximity",
            "isInsideBoundary": isInsideBoundary,
            "withinBuffer": withinBuffer,
            "distanceToBoundaryMeters": (
                activeBoundaryEval["distanceToBoundaryMeters"]
                if activeBoundaryEval
                else bestDist
            ),
            "distanceToCenterMeters": (
                activeBoundaryEval["distanceToCenterMeters"]
                if activeBoundaryEval
                else bestDist
            ),
            "matchedZone": activeBoundaryEval.get("matchedZone") if activeBoundaryEval else None,
            "radiusMeters": activeBoundaryEval.get("radiusMeters") if activeBoundaryEval else None,
        }

        floorDetectionSummary = {
            "isMultiFloor": isMultiFloor,
            "detectedFloor": detectedFloor,
            "defaultFloor": defaultFloor,
            "availableFloors": availableFloors,
            "source": floorSource,
            "confidence": floorConfidence,
            "altitudeMeters": altitudeMeters,
            "altitudeAccuracyMeters": altitudeAccuracyMeters,
            "altitudeRejectedReason": altitudeRejectedReason,
            "beaconId": beaconMatch["beaconId"] if beaconMatch else beaconId,
            "needsFloorSelection": needsFloorSelection,
        }

        estimatedLocation = {
            "label": best["name"] if best else None,
            "buildingId": nearestMacroId,
            "buildingName": best["buildingName"] if best else None,
            "nodeId": best["nodeId"] if best else None,
            "floorLevel": detectedFloor if detectedFloor is not None else defaultFloor,
            "isFloorConfirmed": detectedFloor is not None,
            "isExactSpotConfident": confidence == "high",
        }

        return {
            # Backward-compatible fields
            "isWithinCampus": isWithinCampus,
            "nearestNodeId": nearestMacroId,
            "nearestSpecificNodeId": best["nodeId"] if best else None,
            "nodeName": best["name"] if best else None,
            "buildingName": best["buildingName"] if best else None,
            "distanceMeters": best["distanceMeters"] if best else None,
            "bestMatch": best,
            "needsFloorSelection": needsFloorSelection,
            "availableFloors": availableFloors,
            "floorCandidates": floorCandidates,
            "topCandidates": topCandidates,
            "isAmbiguous": isAmbiguous,
            "accuracyMeters": accuracyMeters,
            "userSvgPosition": {"x": clampedX, "y": clampedY},

            # Rich GPS Location Detection fields (Boundaries, Multi-Floor, Confidence, Manual Fallback)
            "boundaryMatch": boundaryMatchSummary,
            "matchingBoundaries": [
                {
                    "buildingId": ev["buildingId"],
                    "buildingName": ev["buildingName"],
                    "boundaryType": ev["boundaryType"],
                    "isInsideBoundary": ev["isInsideBoundary"],
                    "distanceToBoundaryMeters": ev["distanceToBoundaryMeters"],
                    "floors": ev["floors"],
                }
                for ev in bufferBoundaryHits[:4]
            ],
            "floorDetection": floorDetectionSummary,
            "confidence": confidence,
            "confidenceScore": confidenceScore,
            "buildingConfidence": buildingConfidence,
            "floorConfidence": floorConfidence,
            "spotConfidence": spotConfidence,
            "confidenceReasons": confidenceReasons,
            "estimatedLocation": estimatedLocation,
            "needsManualFallback": needsManualFallback,
            "fallbackReason": fallbackReason,
            "buildingLocations": buildingLocationsPayload["locations"],
            "buildingLocationsByFloor": buildingLocationsPayload["locationsByFloor"],
        }
