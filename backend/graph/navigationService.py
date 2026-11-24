"""
navigationService.py
================================================================================
HIGH-LEVEL HIERARCHICAL CAMPUS NAVIGATION, WALKWAY ROUTING & GPS MATCHING SERVICE
================================================================================
Orchestrates Dijkstra shortest-path routing across the full Weighted, Directed,
Non-Complete Graph hierarchy of UAM Campus:
  1. Indoor Origin Subgraph (if starting from a specific room/office/floor)
  2. Real Pedestrian Walkway Graph (sidewalks, doors, crosswalks, ramps, 2P bridges)
  3. Indoor Destination Subgraph (door-to-room multi-floor guidance)

Translates optimal paths into natural human landmark & relative-turn instructions
with ZERO metric step counts ("camina 40m") and ZERO cardinal directions.
Supports full bilingual i18n ('spa' and 'eng').
================================================================================
"""

import math
import unicodedata
from typing import Dict, List, Optional, Tuple, Any

from .campusGraphBuilder import buildUamCampusGraph
from .dijkstraRouter import DijkstraRouter
from .geoUtils import CampusGeoUtils
from .gpsMatcher import GlobalGpsMatcher
from .humanInstructions import (
    buildHumanWalkwaySteps,
    buildHumanIndoorSteps,
    formatHumanWalkingTime,
)
from .pedestrianWalkwayGraph import (
    globalPedestrianWalkwayGraph,
    MACRO_TO_MICRO_NODE,
    BUILDING_PORTALS,
    WALKWAY_LANDMARKS,
)
from .i18n import t
from data.placesCatalog import PLACES_CATALOG


def _normalizeQuery(text: str) -> str:
    """Lowercases and strips diacritics so Spanish/English queries match reliably."""
    if not text:
        return ""
    decomposed = unicodedata.normalize("NFD", str(text).strip().lower())
    return "".join(ch for ch in decomposed if unicodedata.category(ch) != "Mn")


class NavigationService:
    def __init__(self):
        self.graph = buildUamCampusGraph()
        self.router = DijkstraRouter(self.graph)
        self.walkwayGraph = globalPedestrianWalkwayGraph
        self.walkwayRouter = DijkstraRouter(self.walkwayGraph)
        self.gpsMatcher = GlobalGpsMatcher(self.graph, self.walkwayGraph)

    def _resolveSubgraphNode(self, buildingId: str, *candidates: str) -> Optional[str]:
        from backend.subgraphs import getBuildingSubgraph
        sg = getBuildingSubgraph(buildingId)
        if not sg:
            return None
        for cand in candidates:
            if not cand:
                continue
            found = sg.resolveRoomQuery(cand)
            if found:
                return found
        return None

    def resolveQueryToDestination(self, queryText: str, lang: str = "eng") -> Optional[dict]:
        """
        Resolves free-form text, placeId, macro nodeId, walkway nodeId, or indoor
        subgraph room/alias to a rich destination payload.
        """
        if not queryText:
            return None

        raw = str(queryText).strip()
        cleaned = _normalizeQuery(raw)

        # 1. Direct match with a macro nodeId or exact building/zone name
        for nodeId, node in self.graph.nodes.items():
            if cleaned in (_normalizeQuery(nodeId), _normalizeQuery(node.name), _normalizeQuery(node.getName(lang))):
                return {
                    "targetNodeId": node.nodeId,
                    "placeId": node.nodeId,
                    "subgraphNodeId": None,
                    "walkwayNodeId": MACRO_TO_MICRO_NODE.get(node.nodeId),
                    "displayName": node.getName(lang),
                    "category": node.category,
                    "floorLevel": node.floorLevel,
                    "locationNotes": t("navigation.main_building", lang=lang, default="Main building."),
                    "isSubPlace": False,
                }

        # 2. Direct match with an outdoor pedestrian walkway node (e.g. from GPS snap)
        if raw in self.walkwayGraph.nodes:
            wNode = self.walkwayGraph.nodes[raw]
            macroId = wNode.buildingId if (wNode.buildingId in self.graph.nodes) else "mainParking"
            return {
                "targetNodeId": macroId,
                "placeId": wNode.nodeId,
                "subgraphNodeId": None,
                "walkwayNodeId": wNode.nodeId,
                "displayName": wNode.getName(lang),
                "category": wNode.category,
                "floorLevel": wNode.floorLevel,
                "locationNotes": "",
                "isSubPlace": False,
            }

        # 3. Exact nodeId or registered alias match across all 18 building subgraphs
        from backend.subgraphs import getAllBuildingSubgraphs
        subgraphs = getAllBuildingSubgraphs()
        compactCleaned = cleaned.replace(" ", "").replace("-", "").replace("_", "")
        for buildingId, sg in subgraphs.items():
            # Exact node ID
            if raw in sg.graph.nodes:
                sNode = sg.graph.nodes[raw]
                return {
                    "targetNodeId": sg.macroNodeId,
                    "placeId": sNode.nodeId,
                    "subgraphNodeId": sNode.nodeId,
                    "walkwayNodeId": MACRO_TO_MICRO_NODE.get(sg.macroNodeId),
                    "displayName": sNode.name,
                    "category": sNode.category,
                    "floorLevel": sNode.floorLevel,
                    "locationNotes": f"{sg.name} (Piso {sNode.floorLevel})" if lang == "spa" else f"{sg.name} (Floor {sNode.floorLevel})",
                    "isSubPlace": True,
                }
            # Exact registered alias
            for alias, targetRoomId in sg.roomAliases.items():
                aliasCompact = _normalizeQuery(alias).replace(" ", "").replace("-", "").replace("_", "")
                if aliasCompact == compactCleaned and targetRoomId in sg.graph.nodes:
                    sNode = sg.graph.nodes[targetRoomId]
                    return {
                        "targetNodeId": sg.macroNodeId,
                        "placeId": sNode.nodeId,
                        "subgraphNodeId": sNode.nodeId,
                        "walkwayNodeId": MACRO_TO_MICRO_NODE.get(sg.macroNodeId),
                        "displayName": sNode.name,
                        "category": sNode.category,
                        "floorLevel": sNode.floorLevel,
                        "locationNotes": f"{sg.name} (Piso {sNode.floorLevel})" if lang == "spa" else f"{sg.name} (Floor {sNode.floorLevel})",
                        "isSubPlace": True,
                    }

        # 4. Check PLACES_CATALOG for exact placeId/name first, then best keyword match
        bestMatch = None
        bestScore = 0
        for place in PLACES_CATALOG:
            if _normalizeQuery(place["placeId"]) == cleaned or _normalizeQuery(place["name"]) == cleaned:
                sgNodeId = self._resolveSubgraphNode(
                    place["parentBuildingId"],
                    place["placeId"],
                    place["name"],
                    *place.get("keywords", []),
                )
                return {
                    "targetNodeId": place["parentBuildingId"],
                    "placeId": place["placeId"],
                    "subgraphNodeId": sgNodeId,
                    "walkwayNodeId": MACRO_TO_MICRO_NODE.get(place["parentBuildingId"]),
                    "displayName": place["name"],
                    "category": place["category"],
                    "floorLevel": place["floorLevel"],
                    "locationNotes": place["locationNotes"],
                    "isSubPlace": True,
                }
            for kw in place["keywords"]:
                kwNorm = _normalizeQuery(kw)
                if kwNorm and (kwNorm in cleaned or (len(cleaned) >= 4 and cleaned in kwNorm)) and len(kwNorm) > bestScore:
                    bestScore = len(kwNorm)
                    bestMatch = place

        if bestMatch:
            sgNodeId = self._resolveSubgraphNode(
                bestMatch["parentBuildingId"],
                bestMatch["placeId"],
                bestMatch["name"],
                *bestMatch.get("keywords", []),
            )
            return {
                "targetNodeId": bestMatch["parentBuildingId"],
                "placeId": bestMatch["placeId"],
                "subgraphNodeId": sgNodeId,
                "walkwayNodeId": MACRO_TO_MICRO_NODE.get(bestMatch["parentBuildingId"]),
                "displayName": bestMatch["name"],
                "category": bestMatch["category"],
                "floorLevel": bestMatch["floorLevel"],
                "locationNotes": bestMatch["locationNotes"],
                "isSubPlace": True,
            }

        # 5. Partial room name match inside building subgraphs
        if len(compactCleaned) >= 3:
            for buildingId, sg in subgraphs.items():
                foundRoom = sg.resolveRoomQuery(raw)
                if foundRoom and foundRoom in sg.graph.nodes:
                    sNode = sg.graph.nodes[foundRoom]
                    return {
                        "targetNodeId": sg.macroNodeId,
                        "placeId": sNode.nodeId,
                        "subgraphNodeId": sNode.nodeId,
                        "walkwayNodeId": MACRO_TO_MICRO_NODE.get(sg.macroNodeId),
                        "displayName": sNode.name,
                        "category": sNode.category,
                        "floorLevel": sNode.floorLevel,
                        "locationNotes": f"{sg.name} (Piso {sNode.floorLevel})" if lang == "spa" else f"{sg.name} (Floor {sNode.floorLevel})",
                        "isSubPlace": True,
                    }

        # 6. Fallback to building/zone search by letter or name
        for nodeId, node in self.graph.nodes.items():
            nodeNorm = _normalizeQuery(nodeId)
            engNorm = _normalizeQuery(node.name)
            locNorm = _normalizeQuery(node.getName(lang))
            if (nodeNorm in cleaned or engNorm in cleaned or locNorm in cleaned
                    or (len(cleaned) >= 4 and (cleaned in engNorm or cleaned in locNorm))):
                return {
                    "targetNodeId": nodeId,
                    "placeId": nodeId,
                    "subgraphNodeId": None,
                    "walkwayNodeId": MACRO_TO_MICRO_NODE.get(nodeId),
                    "displayName": node.getName(lang),
                    "category": node.category,
                    "floorLevel": node.floorLevel,
                    "locationNotes": t("navigation.main_building", lang=lang, default="Main building."),
                    "isSubPlace": False,
                }

        return None

    def _findBestWalkwayPath(
        self,
        originDest: dict,
        targetDest: dict,
        accessibleOnly: bool,
    ) -> Tuple[List[str], float, Dict[Tuple[str, str], Any]]:
        """
        Runs Dijkstra on the Weighted, Directed, Non-Complete Pedestrian Walkway Graph
        evaluating valid building portals to pick the true shortest walkable route.
        """
        originPortals = []
        if originDest.get("walkwayNodeId") and originDest["walkwayNodeId"] in self.walkwayGraph.nodes:
            originPortals.append(originDest["walkwayNodeId"])
        for p in BUILDING_PORTALS.get(originDest["targetNodeId"], []):
            if p not in originPortals and p in self.walkwayGraph.nodes:
                originPortals.append(p)

        destPortals = []
        if targetDest.get("walkwayNodeId") and targetDest["walkwayNodeId"] in self.walkwayGraph.nodes:
            destPortals.append(targetDest["walkwayNodeId"])
        for p in BUILDING_PORTALS.get(targetDest["targetNodeId"], []):
            if p not in destPortals and p in self.walkwayGraph.nodes:
                destPortals.append(p)

        bestPath: List[str] = []
        bestDist = float("inf")
        bestEdges: Dict[Tuple[str, str], Any] = {}

        for uPortal in originPortals:
            for vPortal in destPortals:
                path, dist, _, edges = self.walkwayRouter.findShortestPathWithEdges(
                    uPortal, vPortal, accessibleOnly=accessibleOnly
                )
                if path and dist < bestDist:
                    bestDist = dist
                    bestPath = path
                    bestEdges = edges

        return bestPath, bestDist, bestEdges

    def _findBestIndoorLeg(
        self,
        subgraph,
        roomNodeId: str,
        portalRefLat: float,
        portalRefLng: float,
        isExiting: bool,
        accessibleOnly: bool,
    ) -> Tuple[List[str], float]:
        """Finds shortest Dijkstra path between a room and the best accessible entrance of its building."""
        if not subgraph or not roomNodeId or roomNodeId not in subgraph.graph.nodes:
            return [], 0.0

        entrances = [eid for eid in subgraph.entranceNodeIds if eid in subgraph.graph.nodes]
        if not entrances:
            return [], 0.0

        bestPath: List[str] = []
        bestScore = float("inf")
        bestIndoorDist = 0.0

        for entId in entrances:
            u, v = (roomNodeId, entId) if isExiting else (entId, roomNodeId)
            path, dist, _, _ = subgraph.router.findShortestPathWithEdges(
                u, v, accessibleOnly=accessibleOnly
            )
            if not path:
                continue
            entNode = subgraph.graph.nodes[entId]
            extPenalty = 0.0
            if portalRefLat and portalRefLng and entNode.latitude and entNode.longitude:
                extPenalty = CampusGeoUtils.calculateHaversineDistance(
                    portalRefLat, portalRefLng, entNode.latitude, entNode.longitude
                ) * 0.35
            score = dist + extPenalty
            if score < bestScore:
                bestScore = score
                bestPath = path
                bestIndoorDist = dist

        return bestPath, bestIndoorDist

    def calculateRoute(
        self,
        originQuery: str,
        destinationQuery: str,
        accessibleOnly: bool = False,
        lang: str = "eng"
    ) -> dict:
        """
        Calculates a door-to-door pedestrian route combining indoor subgraphs and
        the real pedestrian walkway graph, returning human landmark instructions.
        """
        from backend.subgraphs import getBuildingSubgraph

        originDest = self.resolveQueryToDestination(originQuery, lang=lang)
        targetDest = self.resolveQueryToDestination(destinationQuery, lang=lang)

        if not originDest:
            err = t("navigation.origin_not_found", lang=lang, default=f"Origin not found: '{originQuery}'", query=originQuery)
            return {"success": False, "error": err}
        if not targetDest:
            err = t("navigation.destination_not_found", lang=lang, default=f"Destination not found: '{destinationQuery}'", query=destinationQuery)
            return {"success": False, "error": err}

        sourceNodeId = originDest["targetNodeId"]
        targetNodeId = targetDest["targetNodeId"]
        originSg = getBuildingSubgraph(sourceNodeId)
        targetSg = getBuildingSubgraph(targetNodeId)

        # ------------------------------------------------------------------
        # CASE A: SAME BUILDING / INDOOR-ONLY ROUTE
        # ------------------------------------------------------------------
        if sourceNodeId == targetNodeId:
            macroNode = self.graph.nodes[sourceNodeId]
            macroAnchor = (macroNode.xSvg, macroNode.ySvg)
            originRoom = originDest.get("subgraphNodeId")
            destRoom = targetDest.get("subgraphNodeId")

            if originSg and (originRoom or destRoom):
                startIndoorId = originRoom or (originSg.entranceNodeIds[0] if originSg.entranceNodeIds else None)
                endIndoorId = destRoom or (originSg.entranceNodeIds[0] if originSg.entranceNodeIds else None)
                if startIndoorId and endIndoorId:
                    indoorPath, indoorDist, indoorMins, _ = originSg.router.findShortestPathWithEdges(
                        startIndoorId, endIndoorId, accessibleOnly=accessibleOnly
                    )
                    if not indoorPath:
                        err = t("navigation.no_route_found", lang=lang,
                                default="No walkable indoor route found with the requested accessibility restrictions.")
                        return {"success": False, "error": err}
                    humanSteps = buildHumanIndoorSteps(
                        originSg, indoorPath, lang=lang, mode="standalone", buildingAnchorSvg=macroAnchor
                    )
                    return {
                        "success": True,
                        "origin": originDest["displayName"],
                        "destination": targetDest["displayName"],
                        "originNodeId": sourceNodeId,
                        "destinationNodeId": targetNodeId,
                        "originPlaceId": originDest.get("placeId"),
                        "destinationPlaceId": targetDest.get("placeId"),
                        "isSubPlace": targetDest.get("isSubPlace", False),
                        "isIndoorOnly": True,
                        "recommendedIndoorEntrance": "F1-ENT-E" if (targetNodeId == "buildingP" and accessibleOnly) else ("F1-ENT-W" if targetNodeId == "buildingP" else None),
                        "category": targetDest["category"],
                        "floorLevel": targetDest["floorLevel"],
                        "pathNodeIds": [sourceNodeId],
                        "pathCoordinates": [{
                            "nodeId": sourceNodeId,
                            "name": macroNode.getName(lang),
                            "xPercent": macroNode.xPercent,
                            "yPercent": macroNode.yPercent,
                            "x": macroNode.xSvg,
                            "y": macroNode.ySvg,
                            "lat": macroNode.latitude,
                            "lng": macroNode.longitude,
                        }],
                        "walkwayPath": [],
                        "indoorPathNodeIds": indoorPath,
                        "totalDistanceMeters": round(indoorDist, 1),
                        "estimatedWalkingMinutes": max(1, indoorMins) if indoorDist > 0 else 0,
                        "humanDuration": formatHumanWalkingTime(indoorDist, lang=lang),
                        "steps": humanSteps,
                        "stepInstructions": [s["instruction"] for s in humanSteps],
                        "isAccessibleRoute": accessibleOnly,
                        "language": lang,
                    }

        # ------------------------------------------------------------------
        # CASE B: OUTDOOR / MULTI-BUILDING ROUTE OVER REAL PEDESTRIAN WALKWAYS
        # ------------------------------------------------------------------
        macroPathNodes, macroDist, _, _ = self.router.findShortestPathWithEdges(
            sourceNodeId, targetNodeId, accessibleOnly=accessibleOnly
        )
        walkwayPathIds, walkwayDist, walkwayEdges = self._findBestWalkwayPath(
            originDest, targetDest, accessibleOnly=accessibleOnly
        )

        if not walkwayPathIds and not macroPathNodes:
            err = t("navigation.no_route_found", lang=lang,
                    default="No walkable pedestrian route found between both locations with the requested restrictions.")
            return {"success": False, "error": err}

        allSteps: List[Dict[str, Any]] = []
        totalDistMeters = 0.0

        # 1. Indoor Exit Leg (if origin is a room inside a building with subgraph)
        originIndoorPath: List[str] = []
        if originSg and originDest.get("subgraphNodeId"):
            firstWNode = self.walkwayGraph.nodes[walkwayPathIds[0]] if walkwayPathIds else self.graph.nodes[sourceNodeId]
            originIndoorPath, exitDist = self._findBestIndoorLeg(
                originSg,
                originDest["subgraphNodeId"],
                firstWNode.latitude,
                firstWNode.longitude,
                isExiting=True,
                accessibleOnly=accessibleOnly,
            )
            if len(originIndoorPath) >= 2:
                exitSteps = buildHumanIndoorSteps(
                    originSg,
                    originIndoorPath,
                    lang=lang,
                    mode="exit_origin",
                    buildingAnchorSvg=(firstWNode.xSvg, firstWNode.ySvg),
                )
                allSteps.extend(exitSteps)
                totalDistMeters += exitDist

        # 2. Outdoor Pedestrian Walkway Leg (uses user's exact sidewalks, doors, bridges & crosswalks!)
        hasDestIndoorLeg = False
        destIndoorPath: List[str] = []
        destIndoorDist = 0.0
        if targetSg and targetDest.get("subgraphNodeId"):
            lastWNode = self.walkwayGraph.nodes[walkwayPathIds[-1]] if walkwayPathIds else self.graph.nodes[targetNodeId]
            destIndoorPath, destIndoorDist = self._findBestIndoorLeg(
                targetSg,
                targetDest["subgraphNodeId"],
                lastWNode.latitude,
                lastWNode.longitude,
                isExiting=False,
                accessibleOnly=accessibleOnly,
            )
            if destIndoorPath:
                hasDestIndoorLeg = True
            elif accessibleOnly and targetDest.get("floorLevel", 1) > 1:
                # Target room is on an upper floor unreachable by wheelchair without elevator
                err = (
                    f"{targetDest['displayName']} se encuentra en el Piso {targetDest['floorLevel']} y actualmente solo cuenta con acceso por escaleras."
                    if lang == "spa"
                    else f"{targetDest['displayName']} is on Floor {targetDest['floorLevel']} and currently only has stair access."
                )
                return {"success": False, "error": err}

        if walkwayPathIds:
            destOutdoorName = (
                self.graph.nodes[targetNodeId].getName(lang)
                if hasDestIndoorLeg
                else targetDest["displayName"]
            )
            originOutdoorName = (
                self.graph.nodes[sourceNodeId].getName(lang)
                if originIndoorPath
                else originDest["displayName"]
            )
            outdoorSteps = buildHumanWalkwaySteps(
                self.walkwayGraph,
                walkwayPathIds,
                walkwayEdges,
                originDisplayName=originOutdoorName,
                destDisplayName=destOutdoorName,
                lang=lang,
                includeStartStep=(len(allSteps) == 0),
                includeArrivalStep=(not hasDestIndoorLeg),
            )
            allSteps.extend(outdoorSteps)
            totalDistMeters += walkwayDist
        else:
            totalDistMeters += macroDist

        # 3. Indoor Entry Leg (if destination is an internal room/office in a building with subgraph)
        if hasDestIndoorLeg and targetSg:
            lastWNode = self.walkwayGraph.nodes[walkwayPathIds[-1]] if walkwayPathIds else self.graph.nodes[targetNodeId]
            entrySteps = buildHumanIndoorSteps(
                targetSg,
                destIndoorPath,
                lang=lang,
                mode="enter_destination",
                buildingAnchorSvg=(lastWNode.xSvg, lastWNode.ySvg),
            )
            allSteps.extend(entrySteps)
            totalDistMeters += destIndoorDist
        elif targetDest.get("isSubPlace") and targetDest.get("locationNotes"):
            # Fallback descriptive indoor hint for any subplace not mapped in a subgraph
            lastStep = allSteps[-1] if allSteps else {}
            subMsg = (
                f"Dentro del edificio, busca {targetDest['displayName']} (Piso {targetDest['floorLevel']}): {targetDest['locationNotes']}"
                if lang == "spa"
                else f"Inside the building, look for {targetDest['displayName']} (Floor {targetDest['floorLevel']}): {targetDest['locationNotes']}"
            )
            allSteps.append({
                "index": len(allSteps),
                "instruction": subMsg,
                "headline": "Ubicación interior" if lang == "spa" else "Indoor location",
                "maneuver": "arrive",
                "landmark": targetDest["displayName"],
                "passedLandmarks": [],
                "environment": "indoor",
                "floorLevel": targetDest["floorLevel"],
                "x": lastStep.get("x", 600),
                "y": lastStep.get("y", 425),
                "lat": lastStep.get("lat"),
                "lng": lastStep.get("lng"),
                "nextBearingDeg": None,
                "buildingId": targetNodeId,
                "isIndoor": True,
                "nodeIds": [],
            })

        # Append macro access notice (e.g., Building N clinics biosecurity) if not already appended
        destMacroNode = self.graph.nodes[targetNodeId]
        macroNotice = destMacroNode.getAccessNotice(lang)
        if macroNotice and not any("aviso de acceso" in s["instruction"].lower() or "access notice" in s["instruction"].lower() for s in allSteps):
            lastStep = allSteps[-1] if allSteps else {}
            allSteps.append({
                "index": len(allSteps),
                "instruction": f"Aviso de acceso: {macroNotice}" if lang == "spa" else f"Access notice: {macroNotice}",
                "headline": "Aviso de acceso" if lang == "spa" else "Access notice",
                "maneuver": "arrive",
                "landmark": destMacroNode.getName(lang),
                "passedLandmarks": [],
                "environment": "ground",
                "floorLevel": 1,
                "x": lastStep.get("x", destMacroNode.xSvg),
                "y": lastStep.get("y", destMacroNode.ySvg),
                "lat": destMacroNode.latitude,
                "lng": destMacroNode.longitude,
                "nextBearingDeg": None,
                "buildingId": targetNodeId,
                "isIndoor": False,
                "nodeIds": [],
            })

        # Re-index steps sequentially
        for idx, st in enumerate(allSteps):
            st["index"] = idx

        # Serialize walkway polyline points directly from backend Dijkstra!
        walkwayPath = []
        for wId in walkwayPathIds:
            wn = self.walkwayGraph.nodes[wId]
            walkwayPath.append({
                "nodeId": wId,
                "name": wn.getName(lang),
                "x": round(wn.xSvg),
                "y": round(wn.ySvg),
                "lat": wn.latitude,
                "lng": wn.longitude,
                "portalKind": wn.portalKind,
                "buildingId": wn.buildingId,
            })

        # Macro pathCoordinates (kept for full API & 2D/2.5D compatibility)
        if not macroPathNodes:
            macroPathNodes = [sourceNodeId, targetNodeId]
        pathCoordinates = [
            {
                "nodeId": nId,
                "name": self.graph.nodes[nId].getName(lang),
                "xPercent": self.graph.nodes[nId].xPercent,
                "yPercent": self.graph.nodes[nId].yPercent,
                "x": self.graph.nodes[nId].xSvg,
                "y": self.graph.nodes[nId].ySvg,
                "lat": self.graph.nodes[nId].latitude,
                "lng": self.graph.nodes[nId].longitude,
            }
            for nId in macroPathNodes
        ]

        recommendedIndoorEntrance = None
        if targetNodeId == "buildingP":
            if accessibleOnly:
                recommendedIndoorEntrance = "F1-ENT-E"
            elif walkwayPathIds and walkwayPathIds[-1] == "p_front_east":
                recommendedIndoorEntrance = "F1-ENT-O"
            elif len(macroPathNodes) >= 2 and macroPathNodes[-2] in ("buildingO", "buildingH", "northeastGate", "jaguarJungle", "miRanchito"):
                recommendedIndoorEntrance = "F1-ENT-O"
            else:
                recommendedIndoorEntrance = "F1-ENT-W"

        totalDistMeters = round(totalDistMeters, 1)
        estimatedMinutes = max(1, math.ceil(totalDistMeters / 72.0)) if totalDistMeters > 0 else 0

        return {
            "success": True,
            "origin": originDest["displayName"],
            "destination": targetDest["displayName"],
            "originNodeId": sourceNodeId,
            "destinationNodeId": targetNodeId,
            "originPlaceId": originDest.get("placeId"),
            "destinationPlaceId": targetDest.get("placeId"),
            "isSubPlace": targetDest.get("isSubPlace", False),
            "recommendedIndoorEntrance": recommendedIndoorEntrance,
            "category": targetDest["category"],
            "floorLevel": targetDest["floorLevel"],
            "pathNodeIds": macroPathNodes,
            "pathCoordinates": pathCoordinates,
            "walkwayNodeIds": walkwayPathIds,
            "walkwayPath": walkwayPath,
            "originIndoorPathIds": originIndoorPath,
            "destinationIndoorPathIds": destIndoorPath,
            "totalDistanceMeters": totalDistMeters,
            "estimatedWalkingMinutes": estimatedMinutes,
            "humanDuration": formatHumanWalkingTime(totalDistMeters, lang=lang),
            "steps": allSteps,
            "stepInstructions": [s["instruction"] for s in allSteps],
            "isAccessibleRoute": accessibleOnly,
            "language": lang,
        }

    def getPlacesByCategory(self, category: str) -> List[dict]:
        """Returns all points of interest belonging to a category."""
        return [p for p in PLACES_CATALOG if p["category"] == category]

    def findNearestGpsNode(
        self,
        userLat: float,
        userLng: float,
        lang: str = "eng",
        accuracyMeters: Optional[float] = None,
        floorHint: Optional[int] = None,
        altitudeMeters: Optional[float] = None,
        altitudeAccuracyMeters: Optional[float] = None,
        beaconId: Optional[str] = None,
        beaconFloor: Optional[int] = None,
    ) -> dict:
        """
        Matches user GPS coordinates against defined campus building boundaries
        (polygons & radius checks), multi-floor inference, and the full graph hierarchy.
        """
        return self.gpsMatcher.matchLocation(
            userLat,
            userLng,
            accuracyMeters=accuracyMeters,
            floorHint=floorHint,
            lang=lang,
            altitudeMeters=altitudeMeters,
            altitudeAccuracyMeters=altitudeAccuracyMeters,
            beaconId=beaconId,
            beaconFloor=beaconFloor,
        )

    def getBuildingLocations(
        self,
        buildingId: str,
        userLat: Optional[float] = None,
        userLng: Optional[float] = None,
        floor: Optional[int] = None,
        lang: str = "spa",
    ) -> dict:
        """Returns all manual location options for a campus building grouped by floor."""
        return self.gpsMatcher.getBuildingLocations(
            buildingId=buildingId,
            userLat=userLat,
            userLng=userLng,
            floor=floor,
            lang=lang,
        )

    def getCampusEntranceOptions(self, lang: str = "spa") -> List[dict]:
        """Returns quick-pick campus entrances and central hubs for fallback selection."""
        return self.gpsMatcher.getCampusEntranceOptions(lang=lang)


# Singleton instance for convenient import
globalNavigationService = NavigationService()
