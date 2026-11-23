"""
navigationService.py
High-level campus navigation, destination resolution, and query service.
Supports full internationalization (i18n) across English and Spanish.
All internal code and default strings are in English.
"""

import unicodedata
from typing import List, Optional
from .campusGraphBuilder import buildUamCampusGraph
from .dijkstraRouter import DijkstraRouter
from .geoUtils import CampusGeoUtils
from .i18n import t
from data.placesCatalog import PLACES_CATALOG


def _normalizeQuery(text: str) -> str:
    """Lowercases and strips diacritics so Spanish/English queries match reliably (e.g. 'Área' == 'area')."""
    if not text:
        return ""
    decomposed = unicodedata.normalize("NFD", text.strip().lower())
    return "".join(ch for ch in decomposed if unicodedata.category(ch) != "Mn")


class NavigationService:
    def __init__(self):
        self.graph = buildUamCampusGraph()
        self.router = DijkstraRouter(self.graph)

    def resolveQueryToDestination(self, queryText: str, lang: str = "eng") -> Optional[dict]:
        """
        Resolves free-form text or placeId to a destination payload containing:
        - targetNodeId (Macro node for Dijkstra)
        - placeDetails (Sub-room info, floor, notes, category)
        """
        if not queryText:
            return None

        cleaned = _normalizeQuery(queryText)

        # 1. Direct match with a macro nodeId or exact building/zone name (case- & accent-insensitive)
        for nodeId, node in self.graph.nodes.items():
            if cleaned in (_normalizeQuery(nodeId), _normalizeQuery(node.name), _normalizeQuery(node.getName(lang))):
                return {
                    "targetNodeId": node.nodeId,
                    "placeId": node.nodeId,
                    "displayName": node.getName(lang),
                    "category": node.category,
                    "floorLevel": node.floorLevel,
                    "locationNotes": t("navigation.main_building", lang=lang, default="Main building."),
                    "isSubPlace": False
                }

        # 2. Check placesCatalog for exact placeId/name first, then most specific (longest) keyword match
        bestMatch = None
        bestScore = 0
        for place in PLACES_CATALOG:
            if _normalizeQuery(place["placeId"]) == cleaned or _normalizeQuery(place["name"]) == cleaned:
                return {
                    "targetNodeId": place["parentBuildingId"],
                    "placeId": place["placeId"],
                    "displayName": place["name"],
                    "category": place["category"],
                    "floorLevel": place["floorLevel"],
                    "locationNotes": place["locationNotes"],
                    "isSubPlace": True
                }
            for kw in place["keywords"]:
                kwNorm = _normalizeQuery(kw)
                if kwNorm and (kwNorm in cleaned or (len(cleaned) >= 4 and cleaned in kwNorm)) and len(kwNorm) > bestScore:
                    bestScore = len(kwNorm)
                    bestMatch = place

        if bestMatch:
            return {
                "targetNodeId": bestMatch["parentBuildingId"],
                "placeId": bestMatch["placeId"],
                "displayName": bestMatch["name"],
                "category": bestMatch["category"],
                "floorLevel": bestMatch["floorLevel"],
                "locationNotes": bestMatch["locationNotes"],
                "isSubPlace": True
            }

        # 3. Fallback to building/zone search by letter or name (e.g. "edificio b", "jaguar jungle", "area de mesas")
        for nodeId, node in self.graph.nodes.items():
            nodeNorm = _normalizeQuery(nodeId)
            engNorm = _normalizeQuery(node.name)
            locNorm = _normalizeQuery(node.getName(lang))
            if (nodeNorm in cleaned or engNorm in cleaned or locNorm in cleaned
                    or (len(cleaned) >= 4 and (cleaned in engNorm or cleaned in locNorm))):
                return {
                    "targetNodeId": nodeId,
                    "placeId": nodeId,
                    "displayName": node.getName(lang),
                    "category": node.category,
                    "floorLevel": node.floorLevel,
                    "locationNotes": t("navigation.main_building", lang=lang, default="Main building."),
                    "isSubPlace": False
                }

        return None

    def calculateRoute(
        self,
        originQuery: str,
        destinationQuery: str,
        accessibleOnly: bool = False,
        lang: str = "eng"
    ) -> dict:
        """
        Calculates pedestrian route from origin to destination.
        Handles both macro-buildings and internal sub-rooms seamlessly.
        Supports internationalization (i18n) via the 'lang' parameter (e.g. 'eng', 'spa').
        """
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

        # Run Dijkstra
        pathNodes, distanceMeters, estimatedMinutes, instructions = self.router.findShortestPath(
            sourceNodeId, targetNodeId, accessibleOnly, lang=lang
        )

        if not pathNodes:
            err = t("navigation.no_route_found", lang=lang,
                    default="No walkable pedestrian route found between both locations with the requested restrictions.")
            return {"success": False, "error": err}

        # If destination is an internal sub-room (e.g. B-103 or water fountain), append final micro-instruction
        if targetDest["isSubPlace"]:
            subplaceMsg = t(
                "navigation.subplace_location",
                lang=lang,
                default=f"Building location: {targetDest['displayName']} (Floor {targetDest['floorLevel']}) - {targetDest['locationNotes']}",
                name=targetDest["displayName"],
                floor=targetDest["floorLevel"],
                notes=targetDest["locationNotes"]
            )
            instructions.append(subplaceMsg)

        # Collect SVG coordinates for polyline drawing
        pathCoordinates = [
            {
                "nodeId": nId,
                "name": self.graph.nodes[nId].getName(lang),
                "xPercent": self.graph.nodes[nId].xPercent,
                "yPercent": self.graph.nodes[nId].yPercent,
                "lat": self.graph.nodes[nId].latitude,
                "lng": self.graph.nodes[nId].longitude
            }
            for nId in pathNodes
        ]

        recommendedIndoorEntrance = None
        if targetNodeId == "buildingP":
            if accessibleOnly:
                recommendedIndoorEntrance = "F1-ENT-E"
            elif len(pathNodes) >= 2 and pathNodes[-2] in ("buildingO", "buildingH", "northeastGate", "jaguarJungle", "miRanchito"):
                recommendedIndoorEntrance = "F1-ENT-O"
            else:
                recommendedIndoorEntrance = "F1-ENT-W"

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
            "pathNodeIds": pathNodes,
            "pathCoordinates": pathCoordinates,
            "totalDistanceMeters": distanceMeters,
            "estimatedWalkingMinutes": estimatedMinutes,
            "stepInstructions": instructions,
            "isAccessibleRoute": accessibleOnly,
            "language": lang
        }

    def getPlacesByCategory(self, category: str) -> List[dict]:
        """Returns all points of interest belonging to a category."""
        return [p for p in PLACES_CATALOG if p["category"] == category]

    def findNearestGpsNode(self, userLat: float, userLng: float, lang: str = "eng") -> dict:
        """Finds nearest macro node to given GPS coordinates and validates campus perimeter."""
        isWithinCampus = CampusGeoUtils.isWithinCampusPerimeter(userLat, userLng, bufferMeters=25.0)
        nearestId, distMeters = CampusGeoUtils.findNearestNodeByGps(self.graph, userLat, userLng)
        node = self.graph.getNode(nearestId) if nearestId else None
        return {
            "isWithinCampus": isWithinCampus,
            "nearestNodeId": nearestId,
            "nodeName": node.getName(lang) if node else None,
            "distanceMeters": distMeters
        }


# Singleton instance for convenient import
globalNavigationService = NavigationService()
