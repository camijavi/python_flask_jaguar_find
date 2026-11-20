"""
geoUtils.py
Geolocation utilities: Haversine distance formula and nearest campus node finder.
"""

import math
from typing import Optional, Tuple
from .directedGraph import DirectedGraph


class CampusGeoUtils:
    EARTH_RADIUS_METERS = 6371000

    @staticmethod
    def calculateHaversineDistance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        dLat = math.radians(lat2 - lat1)
        dLon = math.radians(lon2 - lon1)
        a = (math.sin(dLat / 2) ** 2 +
             math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dLon / 2) ** 2)
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        return CampusGeoUtils.EARTH_RADIUS_METERS * c

    @staticmethod
    def findNearestNodeByGps(graph: DirectedGraph, userLat: float, userLng: float) -> Tuple[Optional[str], float]:
        nearestNodeId = None
        minDistance = float("inf")

        for nodeId, node in graph.nodes.items():
            if not node.isOutdoorAccessPoint:
                continue
            distance = CampusGeoUtils.calculateHaversineDistance(userLat, userLng, node.latitude, node.longitude)
            if distance < minDistance:
                minDistance = distance
                nearestNodeId = nodeId

        return nearestNodeId, round(minDistance, 1)
