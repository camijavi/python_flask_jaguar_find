"""
gpsMatcher.py
================================================================================
GLOBAL CAMPUS GPS-TO-GRAPH MATCHING ENGINE (MACRO + WALKWAYS + SUBGRAPHS)
================================================================================
Matches a live user's WGS84 GPS coordinate against every field-measured node in
the UAM campus graph hierarchy:
  1. All 18 Building Subgraphs (exact classrooms, offices, labs, restrooms, ramps)
  2. Outdoor Pedestrian Walkway Landmarks (Banpro, Crosswalk, Chilamates, etc.)
  3. Macro Campus Buildings & Gates

Handles real-world mobile GPS challenges:
  - Campus perimeter boundary validation (Ray-Casting + buffer)
  - Vertical Z-axis ambiguity in multi-story buildings (returns availableFloors
    + best room candidate per floor so the user confirms their floor in 1 tap)
  - Indoor GPS inaccuracy / building boundary proximity (returns top 3 distinct
    candidate buildings/locations for rapid disambiguation)
  - Calibrated Affine GPS -> SVG (x, y) projection for live 2D/2.5D rendering
================================================================================
"""

from typing import Dict, List, Optional, Any
from .directedGraph import DirectedGraph
from .geoUtils import CampusGeoUtils
from .pedestrianWalkwayGraph import globalPedestrianWalkwayGraph, WALKWAY_LANDMARKS


class GlobalGpsMatcher:
    def __init__(self, macroGraph: DirectedGraph, walkwayGraph: DirectedGraph = globalPedestrianWalkwayGraph):
        self.macroGraph = macroGraph
        self.walkwayGraph = walkwayGraph

    def matchLocation(
        self,
        userLat: float,
        userLng: float,
        accuracyMeters: Optional[float] = None,
        floorHint: Optional[int] = None,
        lang: str = "spa",
    ) -> dict:
        from backend.subgraphs import getAllBuildingSubgraphs

        isWithinCampus = CampusGeoUtils.isWithinCampusPerimeter(userLat, userLng, bufferMeters=30.0)
        svgX, svgY = CampusGeoUtils.gpsToSvg(userLat, userLng)
        # Clamp SVG visual dot softly within campus bounds when inside perimeter
        clampedX = round(max(40.0, min(1160.0, svgX)), 1)
        clampedY = round(max(15.0, min(835.0, svgY)), 1)

        allMatches: List[Dict[str, Any]] = []
        subgraphs = getAllBuildingSubgraphs()

        # 1. Search all indoor/building subgraph nodes (exact field-measured coordinates!)
        for buildingId, sg in subgraphs.items():
            macroNode = self.macroGraph.getNode(sg.macroNodeId)
            buildingName = macroNode.getName(lang) if macroNode else sg.name
            for node in sg.getAllNodes():
                if not node.latitude or not node.longitude:
                    continue
                dist = CampusGeoUtils.calculateHaversineDistance(userLat, userLng, node.latitude, node.longitude)
                allMatches.append({
                    "nodeId": node.nodeId,
                    "placeId": node.nodeId,
                    "name": node.name,
                    "buildingId": sg.macroNodeId,
                    "buildingName": buildingName,
                    "subgraphId": buildingId,
                    "floorLevel": getattr(node, "floorLevel", 1),
                    "availableFloors": list(sg.floors),
                    "distanceMeters": round(dist, 1),
                    "lat": node.latitude,
                    "lng": node.longitude,
                    "x": node.xSvg,
                    "y": node.ySvg,
                    "source": "subgraph",
                    "category": node.category,
                })

        # 2. Search outdoor pedestrian walkway landmark nodes (Banpro, Plaza Chilamates, etc.)
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
                "floorLevel": wNode.floorLevel,
                "availableFloors": list(sg.floors) if sg else [1],
                "distanceMeters": round(dist, 1),
                "lat": wNode.latitude,
                "lng": wNode.longitude,
                "x": wNode.xSvg,
                "y": wNode.ySvg,
                "source": "walkway",
                "category": wNode.category,
            })

        # 3. Search macro campus nodes (gates, parking, outdoor connectors)
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

        # Apply optional floorHint when filtering best match inside detected building
        best = allMatches[0] if allMatches else None
        if best and floorHint is not None and best.get("subgraphId"):
            sameBuildingFloor = [
                m for m in allMatches
                if m.get("subgraphId") == best["subgraphId"]
                and m["source"] == "subgraph"
                and m["floorLevel"] == floorHint
            ]
            if sameBuildingFloor:
                best = sameBuildingFloor[0]

        # Build floor candidates if the matched building has multiple floors
        floorCandidates: List[Dict[str, Any]] = []
        needsFloorSelection = False
        if best and best.get("subgraphId") and len(best.get("availableFloors", [])) > 1:
            sg = subgraphs.get(best["subgraphId"])
            if sg:
                for fl in sg.floors:
                    flMatches = [
                        m for m in allMatches
                        if m.get("subgraphId") == best["subgraphId"]
                        and m["source"] == "subgraph"
                        and m["floorLevel"] == fl
                    ]
                    if flMatches:
                        topFl = flMatches[0]
                        floorCandidates.append({
                            "floorLevel": fl,
                            "nodeId": topFl["nodeId"],
                            "name": topFl["name"],
                            "buildingId": topFl["buildingId"],
                            "distanceMeters": topFl["distanceMeters"],
                        })
                if floorHint is None and len(floorCandidates) > 1 and best["distanceMeters"] <= 35.0:
                    needsFloorSelection = True

        # Top 3 distinct nearby buildings/zones for quick disambiguation
        topCandidates: List[Dict[str, Any]] = []
        seenBuildings = set()
        for m in allMatches:
            key = m["buildingId"]
            if key in seenBuildings:
                continue
            seenBuildings.add(key)
            topCandidates.append({
                "nodeId": m["nodeId"],
                "buildingId": m["buildingId"],
                "name": m["name"],
                "buildingName": m["buildingName"],
                "floorLevel": m["floorLevel"],
                "distanceMeters": m["distanceMeters"],
                "source": m["source"],
            })
            if len(topCandidates) >= 3:
                break

        lowAccuracy = bool(accuracyMeters is not None and accuracyMeters > 15.0)
        isAmbiguous = lowAccuracy or (
            len(topCandidates) >= 2
            and (topCandidates[1]["distanceMeters"] - topCandidates[0]["distanceMeters"]) <= 12.0
        )

        # Backward-compatible fields + rich new GPS match payload
        nearestMacroId = best["buildingId"] if best else None
        if nearestMacroId and nearestMacroId not in self.macroGraph.nodes:
            nearestMacroId = "mainParking"

        return {
            "isWithinCampus": isWithinCampus,
            "nearestNodeId": nearestMacroId,
            "nearestSpecificNodeId": best["nodeId"] if best else None,
            "nodeName": best["name"] if best else None,
            "buildingName": best["buildingName"] if best else None,
            "distanceMeters": best["distanceMeters"] if best else None,
            "bestMatch": best,
            "needsFloorSelection": needsFloorSelection,
            "availableFloors": best.get("availableFloors", [1]) if best else [1],
            "floorCandidates": floorCandidates,
            "topCandidates": topCandidates,
            "isAmbiguous": isAmbiguous,
            "accuracyMeters": accuracyMeters,
            "userSvgPosition": {"x": clampedX, "y": clampedY},
        }
