"""
geoUtils.py
Geolocation utilities: Haversine distance formula, perimeter boundary checking (Ray-Casting),
and nearest campus node finder.
"""

import math
from typing import Optional, Tuple, List, Dict
from .directedGraph import DirectedGraph


class CampusGeoUtils:
    EARTH_RADIUS_METERS = 6371000

    # Calibrated Affine Projection: Real UAM WGS84 GPS <-> Official 1200x850 SVG Space
    # Fitted via least-squares from field-measured coordinates in coordenadas.txt.
    # Official UAM Campus Map is oriented South-Up (true compass bearing of SVG UP = 181.4 deg).
    CALIB_LAT0 = 12.1085
    CALIB_LNG0 = -86.2573
    CALIB_M_PER_DEG_LAT = 111132.0
    CALIB_M_PER_DEG_LNG = 111320.0 * math.cos(math.radians(12.1085))
    # x = CX0 + CX_N * mNorth + CX_E * mEast
    # y = CY0 + CY_N * mNorth + CY_E * mEast
    CALIB_CX0 = 529.03
    CALIB_CX_N = 0.0778
    CALIB_CX_E = -3.2168
    CALIB_CY0 = 441.96
    CALIB_CY_N = 2.5386
    CALIB_CY_E = -0.0374
    MAP_UP_TRUE_BEARING_DEG = 181.4
    AVG_SVG_PX_PER_METER = 2.88

    # Official UAM Campus Perimeter Polygon coordinates (Lat, Lng)
    # Order follows boundary vertices around UAM campus
    UAM_CAMPUS_PERIMETER: List[Tuple[float, float]] = [
        (12.109617, -86.259097),
        (12.109665, -86.256455),
        (12.108771, -86.255659),
        (12.107598, -86.255665),
        (12.107639, -86.256172),
        (12.107263, -86.256262),
        (12.106934, -86.256302),
        (12.106324, -86.258762),
    ]

    @staticmethod
    def gpsToSvg(lat: float, lng: float) -> Tuple[float, float]:
        """Projects real WGS84 (lat, lng) onto the official 1200x850 UAM SVG canvas."""
        mNorth = (lat - CampusGeoUtils.CALIB_LAT0) * CampusGeoUtils.CALIB_M_PER_DEG_LAT
        mEast = (lng - CampusGeoUtils.CALIB_LNG0) * CampusGeoUtils.CALIB_M_PER_DEG_LNG
        x = CampusGeoUtils.CALIB_CX0 + CampusGeoUtils.CALIB_CX_N * mNorth + CampusGeoUtils.CALIB_CX_E * mEast
        y = CampusGeoUtils.CALIB_CY0 + CampusGeoUtils.CALIB_CY_N * mNorth + CampusGeoUtils.CALIB_CY_E * mEast
        return round(x, 1), round(y, 1)

    @staticmethod
    def svgToGps(x: float, y: float) -> Tuple[float, float]:
        """Inverse-projects 1200x850 SVG coordinates to calibrated WGS84 (lat, lng)."""
        dx = x - CampusGeoUtils.CALIB_CX0
        dy = y - CampusGeoUtils.CALIB_CY0
        det = (CampusGeoUtils.CALIB_CX_N * CampusGeoUtils.CALIB_CY_E
               - CampusGeoUtils.CALIB_CX_E * CampusGeoUtils.CALIB_CY_N)
        mNorth = (dx * CampusGeoUtils.CALIB_CY_E - CampusGeoUtils.CALIB_CX_E * dy) / det
        mEast = (CampusGeoUtils.CALIB_CX_N * dy - dx * CampusGeoUtils.CALIB_CY_N) / det
        lat = CampusGeoUtils.CALIB_LAT0 + (mNorth / CampusGeoUtils.CALIB_M_PER_DEG_LAT)
        lng = CampusGeoUtils.CALIB_LNG0 + (mEast / CampusGeoUtils.CALIB_M_PER_DEG_LNG)
        return round(lat, 6), round(lng, 6)

    @staticmethod
    def svgDistanceToMeters(x1: float, y1: float, x2: float, y2: float) -> float:
        """Converts an SVG walkway segment length into calibrated real-world meters."""
        lat1, lng1 = CampusGeoUtils.svgToGps(x1, y1)
        lat2, lng2 = CampusGeoUtils.svgToGps(x2, y2)
        return round(max(1.0, CampusGeoUtils.calculateHaversineDistance(lat1, lng1, lat2, lng2)), 1)

    @staticmethod
    def calculateCompassBearing(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        """Returns initial true compass bearing in degrees [0, 360) from point 1 to point 2."""
        phi1 = math.radians(lat1)
        phi2 = math.radians(lat2)
        dLon = math.radians(lon2 - lon1)
        y = math.sin(dLon) * math.cos(phi2)
        x = math.cos(phi1) * math.sin(phi2) - math.sin(phi1) * math.cos(phi2) * math.cos(dLon)
        return (math.degrees(math.atan2(y, x)) + 360.0) % 360.0

    @staticmethod
    def getCalibrationMetadata() -> Dict[str, object]:
        """Exports GPS<->SVG affine calibration, campus perimeter, and true map heading offset for the frontend."""
        return {
            "lat0": CampusGeoUtils.CALIB_LAT0,
            "lng0": CampusGeoUtils.CALIB_LNG0,
            "mPerDegLat": CampusGeoUtils.CALIB_M_PER_DEG_LAT,
            "mPerDegLng": CampusGeoUtils.CALIB_M_PER_DEG_LNG,
            "cx0": CampusGeoUtils.CALIB_CX0,
            "cxN": CampusGeoUtils.CALIB_CX_N,
            "cxE": CampusGeoUtils.CALIB_CX_E,
            "cy0": CampusGeoUtils.CALIB_CY0,
            "cyN": CampusGeoUtils.CALIB_CY_N,
            "cyE": CampusGeoUtils.CALIB_CY_E,
            "mapUpTrueBearingDeg": CampusGeoUtils.MAP_UP_TRUE_BEARING_DEG,
            "avgSvgPxPerMeter": CampusGeoUtils.AVG_SVG_PX_PER_METER,
            "svgWidth": 1200.0,
            "svgHeight": 850.0,
            "perimeter": CampusGeoUtils.getCampusPerimeter(),
        }

    @staticmethod
    def calculateHaversineDistance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        """Calculates Great-Circle distance in meters between two lat/lon points."""
        dLat = math.radians(lat2 - lat1)
        dLon = math.radians(lon2 - lon1)
        a = (math.sin(dLat / 2) ** 2 +
             math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dLon / 2) ** 2)
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        return CampusGeoUtils.EARTH_RADIUS_METERS * c

    @staticmethod
    def pointToSegmentDistanceMeters(lat: float, lng: float, lat1: float, lng1: float, lat2: float, lng2: float) -> float:
        """Calculates perpendicular or edge distance in meters from a point to a line segment."""
        latMid = math.radians((lat1 + lat2) / 2.0)
        mPerDegLat = 111132.954 - 559.822 * math.cos(2 * latMid)
        mPerDegLng = 111412.84 * math.cos(latMid)

        px = (lng - lng1) * mPerDegLng
        py = (lat - lat1) * mPerDegLat

        dx = (lng2 - lng1) * mPerDegLng
        dy = (lat2 - lat1) * mPerDegLat

        segLenSq = dx * dx + dy * dy
        if segLenSq == 0:
            return math.hypot(px, py)

        t = max(0.0, min(1.0, (px * dx + py * dy) / segLenSq))
        projX = t * dx
        projY = t * dy
        return math.hypot(px - projX, py - projY)

    @staticmethod
    def isPointInPolygon(lat: float, lng: float, polygon: Optional[List[Tuple[float, float]]] = None) -> bool:
        """
        Ray-Casting algorithm to determine if a (lat, lng) point is geometrically inside a polygon.
        Returns True if the point is within the polygon, False otherwise.
        """
        if polygon is None:
            polygon = CampusGeoUtils.UAM_CAMPUS_PERIMETER

        n = len(polygon)
        inside = False
        p1_lat, p1_lng = polygon[0]
        for i in range(1, n + 1):
            p2_lat, p2_lng = polygon[i % n]
            if min(p1_lat, p2_lat) < lat <= max(p1_lat, p2_lat):
                if p1_lat != p2_lat:
                    xinters = (lat - p1_lat) * (p2_lng - p1_lng) / (p2_lat - p1_lat) + p1_lng
                    if p1_lng == p2_lng or lng <= xinters:
                        inside = not inside
            p1_lat, p1_lng = p2_lat, p2_lng
        return inside

    @staticmethod
    def isWithinCampusPerimeter(
        lat: float,
        lng: float,
        bufferMeters: float = 25.0,
        polygon: Optional[List[Tuple[float, float]]] = None
    ) -> bool:
        """
        Validates if coordinates are within the official UAM campus perimeter.
        Includes a buffer distance in meters to accommodate real-world GPS inaccuracy/jitter
        when users are standing at campus gates, perimeter sidewalks, or exterior parking.
        """
        if polygon is None:
            polygon = CampusGeoUtils.UAM_CAMPUS_PERIMETER

        # 1. Direct interior check
        if CampusGeoUtils.isPointInPolygon(lat, lng, polygon):
            return True

        # 2. Buffer tolerance check
        if bufferMeters > 0:
            n = len(polygon)
            for i in range(n):
                p1 = polygon[i]
                p2 = polygon[(i + 1) % n]
                dist = CampusGeoUtils.pointToSegmentDistanceMeters(lat, lng, p1[0], p1[1], p2[0], p2[1])
                if dist <= bufferMeters:
                    return True

        return False

    @staticmethod
    def getCampusPerimeter() -> List[Dict[str, float]]:
        """Returns the perimeter coordinates formatted as a list of dicts for JSON APIs."""
        return [{"lat": pt[0], "lng": pt[1]} for pt in CampusGeoUtils.UAM_CAMPUS_PERIMETER]

    @staticmethod
    def findNearestNodeByGps(graph: DirectedGraph, userLat: float, userLng: float) -> Tuple[Optional[str], float]:
        """Finds nearest outdoor access node in the graph using Haversine distance."""
        nearestNodeId = None
        minDistance = float("inf")

        for nodeId, node in graph.nodes.items():
            if not getattr(node, "isOutdoorAccessPoint", True):
                continue
            distance = CampusGeoUtils.calculateHaversineDistance(userLat, userLng, node.latitude, node.longitude)
            if distance < minDistance:
                minDistance = distance
                nearestNodeId = nodeId

        return nearestNodeId, round(minDistance, 1)
