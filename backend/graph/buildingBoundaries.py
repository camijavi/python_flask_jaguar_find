"""
buildingBoundaries.py
================================================================================
DEFINED UAM CAMPUS BUILDING COORDINATE BOUNDARIES (POLYGONS & RADIUS CHECKS)
================================================================================
Defines explicit WGS84 geographic footprints for every UAM campus building,
sports facility, plaza, pavilion, and access gate:
  - Polygon boundaries (`boundaryType="polygon"`) calibrated to real field-measured
    WGS84 coordinates (`coordenadas.txt` & indoor building subgraphs), supporting
    both primary building footprints and named annex polygons.
  - Circular radius boundaries (`boundaryType="radius"`) for compact pavilions,
    outdoor terraces, and perimeter access gates.
  - Floor metadata, calibrated ground elevation (`baseAltitudeMeters`) and
    story height (`floorHeightMeters`) for optional barometric/altitude floor
    inference, plus an indoor beacon registry (`BEACON_REGISTRY`) for BLE/Wi-Fi
    floor resolution when beacon data is available.
================================================================================
"""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple
import math

from .geoUtils import CampusGeoUtils


# Default UAM Managua campus elevation above sea level (meters) and story height
DEFAULT_CAMPUS_BASE_ALTITUDE_M = 135.0
DEFAULT_FLOOR_HEIGHT_M = 3.5


def _paddedRectPolygon(
    minLat: float,
    maxLat: float,
    minLng: float,
    maxLng: float,
    padMeters: float = 4.0,
) -> List[Tuple[float, float]]:
    """
    Constructs a clockwise WGS84 bounding polygon around [minLat..maxLat] x [minLng..maxLng]
    expanded outward by `padMeters` on each side to cover exterior walls and walkways.
    """
    midLatRad = math.radians((minLat + maxLat) / 2.0)
    dLat = padMeters / 111132.0
    dLng = padMeters / (111320.0 * math.cos(midLatRad))
    south = round(minLat - dLat, 6)
    north = round(maxLat + dLat, 6)
    west = round(minLng - dLng, 6)
    east = round(maxLng + dLng, 6)
    return [
        (north, west),
        (north, east),
        (south, east),
        (south, west),
    ]


@dataclass
class BuildingBoundary:
    """Geographic boundary specification (polygon or radius) for a campus building/zone."""

    buildingId: str
    boundaryType: str  # "polygon" | "radius"
    center: Tuple[float, float]
    radiusMeters: float
    floors: List[int] = field(default_factory=lambda: [1])
    polygon: List[Tuple[float, float]] = field(default_factory=list)
    annexPolygons: List[Tuple[str, List[Tuple[float, float]]]] = field(default_factory=list)
    bufferMeters: float = 8.0
    baseAltitudeMeters: float = DEFAULT_CAMPUS_BASE_ALTITUDE_M
    floorHeightMeters: float = DEFAULT_FLOOR_HEIGHT_M

    def evaluatePoint(self, lat: float, lng: float) -> Dict[str, Any]:
        """
        Tests whether (lat, lng) falls inside this building's defined polygon(s)
        or circular radius, returning exact boundary distance and buffer status.
        """
        distToCenter = round(
            CampusGeoUtils.calculateHaversineDistance(lat, lng, self.center[0], self.center[1]),
            2,
        )

        if self.boundaryType == "polygon" and self.polygon:
            bestDist = CampusGeoUtils.distanceToPolygonMeters(lat, lng, self.polygon)
            matchedZone = "main" if bestDist == 0.0 else None

            for zoneLabel, annexPoly in self.annexPolygons:
                annexDist = CampusGeoUtils.distanceToPolygonMeters(lat, lng, annexPoly)
                if annexDist < bestDist:
                    bestDist = annexDist
                    matchedZone = zoneLabel if annexDist == 0.0 else None
                elif annexDist == 0.0 and matchedZone is None:
                    bestDist = 0.0
                    matchedZone = zoneLabel

            isInside = bestDist == 0.0
            withinBuffer = bestDist <= self.bufferMeters
            return {
                "buildingId": self.buildingId,
                "boundaryType": "polygon",
                "isInsideBoundary": isInside,
                "withinBuffer": withinBuffer,
                "distanceToBoundaryMeters": round(bestDist, 2),
                "distanceToCenterMeters": distToCenter,
                "matchedZone": matchedZone,
                "radiusMeters": self.radiusMeters,
                "bufferMeters": self.bufferMeters,
                "floors": list(self.floors),
            }

        # Circular radius boundary check
        isInside, _ = CampusGeoUtils.isPointInRadius(
            lat, lng, self.center[0], self.center[1], self.radiusMeters
        )
        distToEdge = round(max(0.0, distToCenter - self.radiusMeters), 2)
        withinBuffer = distToCenter <= (self.radiusMeters + self.bufferMeters)
        return {
            "buildingId": self.buildingId,
            "boundaryType": "radius",
            "isInsideBoundary": isInside,
            "withinBuffer": withinBuffer,
            "distanceToBoundaryMeters": distToEdge,
            "distanceToCenterMeters": distToCenter,
            "matchedZone": "radius" if isInside else None,
            "radiusMeters": self.radiusMeters,
            "bufferMeters": self.bufferMeters,
            "floors": list(self.floors),
        }

    def inferFloorFromAltitude(
        self,
        altitudeMeters: Optional[float],
        altitudeAccuracyMeters: Optional[float],
    ) -> Dict[str, Any]:
        """
        Safely attempts floor inference from altitude ONLY when vertical accuracy
        is reliable enough indoors (<= 4.0m). Standard browser GPS altitude is
        typically null or > 10m inaccurate indoors and will be rejected cleanly.
        """
        if len(self.floors) <= 1:
            return {
                "inferredFloor": self.floors[0] if self.floors else 1,
                "confidence": "high",
                "rejectedReason": None,
            }

        if altitudeMeters is None:
            return {
                "inferredFloor": None,
                "confidence": "low",
                "rejectedReason": "altitude_unavailable",
            }

        if altitudeAccuracyMeters is None or altitudeAccuracyMeters > 4.0:
            return {
                "inferredFloor": None,
                "confidence": "low",
                "rejectedReason": "unreliable_indoor_altitude",
            }

        relativeHeight = altitudeMeters - self.baseAltitudeMeters
        estimatedFloat = (relativeHeight / self.floorHeightMeters) + 1.0
        nearestFloor = int(round(estimatedFloat))

        if nearestFloor not in self.floors:
            return {
                "inferredFloor": None,
                "confidence": "low",
                "rejectedReason": "out_of_building_range",
            }

        # Reject ambiguous mid-stairwell readings (> 1.4m from floor slab)
        expectedHeight = (nearestFloor - 1) * self.floorHeightMeters
        if abs(relativeHeight - expectedHeight) > 1.4:
            return {
                "inferredFloor": None,
                "confidence": "low",
                "rejectedReason": "between_floors",
            }

        conf = "high" if altitudeAccuracyMeters <= 2.0 else "medium"
        return {
            "inferredFloor": nearestFloor,
            "confidence": conf,
            "rejectedReason": None,
        }

    def toDict(self) -> Dict[str, Any]:
        return {
            "buildingId": self.buildingId,
            "boundaryType": self.boundaryType,
            "center": {"lat": self.center[0], "lng": self.center[1]},
            "radiusMeters": self.radiusMeters,
            "bufferMeters": self.bufferMeters,
            "floors": list(self.floors),
            "baseAltitudeMeters": self.baseAltitudeMeters,
            "floorHeightMeters": self.floorHeightMeters,
            "polygon": [{"lat": pt[0], "lng": pt[1]} for pt in self.polygon],
            "annexPolygons": [
                {
                    "label": label,
                    "polygon": [{"lat": pt[0], "lng": pt[1]} for pt in poly],
                }
                for label, poly in self.annexPolygons
            ],
        }


# =============================================================================
# OFFICIAL UAM CAMPUS BUILDING BOUNDARIES REGISTRY (WGS84 POLYGONS & RADII)
# =============================================================================
# Calibrated directly against field-measured coordinates in coordenadas.txt and
# all 18 indoor building subgraphs so every room falls inside its parent polygon.

BUILDING_BOUNDARIES: Dict[str, BuildingBoundary] = {
    # --- Main Academic & Administrative Buildings (A - P) ---
    "buildingA": BuildingBoundary(
        buildingId="buildingA",
        boundaryType="polygon",
        center=(12.108458, -86.256657),
        radiusMeters=22.0,
        floors=[1, 2, 3],
        polygon=_paddedRectPolygon(12.108412, 12.108560, -86.256709, -86.256496, padMeters=4.0),
        bufferMeters=8.0,
    ),
    "buildingB": BuildingBoundary(
        buildingId="buildingB",
        boundaryType="polygon",
        center=(12.108554, -86.257025),
        radiusMeters=36.0,
        floors=[1, 2],
        polygon=_paddedRectPolygon(12.108507, 12.108610, -86.257332, -86.256730, padMeters=3.5),
        bufferMeters=7.0,
    ),
    "buildingC": BuildingBoundary(
        buildingId="buildingC",
        boundaryType="polygon",
        center=(12.108468, -86.257013),
        radiusMeters=37.0,
        floors=[1, 2, 3],
        polygon=_paddedRectPolygon(12.108376, 12.108583, -86.257316, -86.256697, padMeters=3.5),
        bufferMeters=7.0,
    ),
    "buildingD": BuildingBoundary(
        buildingId="buildingD",
        boundaryType="polygon",
        center=(12.108092, -86.256913),
        radiusMeters=14.0,
        floors=[1],
        polygon=_paddedRectPolygon(12.108029, 12.108128, -86.256945, -86.256819, padMeters=3.5),
        bufferMeters=7.0,
    ),
    "buildingE": BuildingBoundary(
        buildingId="buildingE",
        boundaryType="polygon",
        center=(12.109047, -86.257270),
        radiusMeters=40.0,
        floors=[1, 2],
        # Custom non-convex footprint covering Medicine Wing (east) + South DIE + West DVE Restrooms
        # without swallowing Building F's courtyard northwest of E
        polygon=[
            (12.108700, -86.257320),
            (12.108700, -86.257050),
            (12.109375, -86.257050),
            (12.109375, -86.257420),
            (12.109120, -86.257420),
            (12.109120, -86.257630),
            (12.109020, -86.257630),
            (12.109020, -86.257320),
        ],
        bufferMeters=8.0,
    ),
    "buildingF": BuildingBoundary(
        buildingId="buildingF",
        boundaryType="polygon",
        center=(12.108989, -86.257449),
        radiusMeters=26.0,
        floors=[1],
        polygon=_paddedRectPolygon(12.108908, 12.109078, -86.257713, -86.257347, padMeters=3.5),
        bufferMeters=7.0,
    ),
    "buildingG": BuildingBoundary(
        buildingId="buildingG",
        boundaryType="polygon",
        center=(12.108694, -86.257507),
        radiusMeters=20.0,
        floors=[1, 2],
        polygon=_paddedRectPolygon(12.108630, 12.108801, -86.257600, -86.257410, padMeters=4.0),
        bufferMeters=8.0,
    ),
    "buildingH": BuildingBoundary(
        buildingId="buildingH",
        boundaryType="polygon",
        center=(12.108226, -86.257648),
        radiusMeters=22.0,
        floors=[1, 2],
        polygon=_paddedRectPolygon(12.108156, 12.108304, -86.257812, -86.257529, padMeters=4.0),
        bufferMeters=8.0,
    ),
    "buildingI": BuildingBoundary(
        buildingId="buildingI",
        boundaryType="polygon",
        center=(12.109283, -86.258005),
        radiusMeters=48.0,
        floors=[1],
        polygon=_paddedRectPolygon(12.108893, 12.109603, -86.258323, -86.257858, padMeters=5.0),
        bufferMeters=10.0,
    ),
    "buildingJ": BuildingBoundary(
        buildingId="buildingJ",
        boundaryType="polygon",
        center=(12.108089, -86.256792),
        radiusMeters=11.0,
        floors=[1],
        polygon=_paddedRectPolygon(12.108030, 12.108126, -86.256830, -86.256756, padMeters=3.0),
        bufferMeters=6.0,
    ),
    "buildingK": BuildingBoundary(
        buildingId="buildingK",
        boundaryType="polygon",
        center=(12.108762, -86.256736),
        radiusMeters=28.0,
        floors=[1, 2],
        polygon=_paddedRectPolygon(12.108585, 12.108815, -86.256785, -86.256576, padMeters=4.5),
        bufferMeters=8.0,
    ),
    "buildingL": BuildingBoundary(
        buildingId="buildingL",
        boundaryType="polygon",
        center=(12.109042, -86.258520),
        radiusMeters=18.0,
        floors=[1],
        polygon=_paddedRectPolygon(12.108905, 12.109123, -86.258551, -86.258504, padMeters=4.5),
        bufferMeters=7.0,
    ),
    "buildingM": BuildingBoundary(
        buildingId="buildingM",
        boundaryType="polygon",
        center=(12.108436, -86.257570),
        radiusMeters=20.0,
        floors=[1, 2, 3],
        polygon=_paddedRectPolygon(12.108331, 12.108525, -86.257612, -86.257453, padMeters=4.0),
        bufferMeters=8.0,
    ),
    "buildingN": BuildingBoundary(
        buildingId="buildingN",
        boundaryType="polygon",
        center=(12.107852, -86.256951),
        radiusMeters=24.0,
        floors=[1, 2],
        polygon=_paddedRectPolygon(12.107741, 12.108000, -86.257105, -86.256842, padMeters=4.0),
        bufferMeters=8.0,
    ),
    "buildingO": BuildingBoundary(
        buildingId="buildingO",
        boundaryType="polygon",
        center=(12.107600, -86.257560),
        radiusMeters=32.0,
        floors=[1, 2],
        polygon=_paddedRectPolygon(12.107478, 12.107741, -86.257761, -86.257388, padMeters=4.5),
        annexPolygons=[
            (
                "north_annex",
                _paddedRectPolygon(12.108151, 12.108229, -86.257948, -86.257888, padMeters=4.0),
            ),
        ],
        bufferMeters=8.0,
    ),
    "buildingP": BuildingBoundary(
        buildingId="buildingP",
        boundaryType="polygon",
        center=(12.107452, -86.257043),
        radiusMeters=44.0,
        floors=[1, 2, 3, 4, 5],
        polygon=_paddedRectPolygon(12.107402, 12.107584, -86.257431, -86.256717, padMeters=5.0),
        bufferMeters=10.0,
    ),

    # --- Sports Complexes ---
    "jaguarCenter": BuildingBoundary(
        buildingId="jaguarCenter",
        boundaryType="polygon",
        center=(12.109269, -86.258719),
        radiusMeters=34.0,
        floors=[1],
        polygon=_paddedRectPolygon(12.109111, 12.109332, -86.258882, -86.258508, padMeters=5.0),
        bufferMeters=9.0,
    ),
    "sportsZone": BuildingBoundary(
        buildingId="sportsZone",
        boundaryType="polygon",
        center=(12.108046, -86.258212),
        radiusMeters=85.0,
        floors=[1],
        # Primary polygon: Soccer Field + Sports Warehouse + Kiosko Jaguarcito
        polygon=_paddedRectPolygon(12.108083, 12.108580, -86.258680, -86.257861, padMeters=6.0),
        # Annex polygon: Jaguar Baseball Stadium (north sports complex)
        annexPolygons=[
            (
                "baseball_stadium",
                _paddedRectPolygon(12.107020, 12.107720, -86.258720, -86.257900, padMeters=6.0),
            ),
        ],
        bufferMeters=12.0,
    ),

    # --- Outdoor Plazas, Pavilions & Access Gates (Polygons & Radius Checks) ---
    "chilamatesPlaza": BuildingBoundary(
        buildingId="chilamatesPlaza",
        boundaryType="polygon",
        center=(12.108027, -86.256705),
        radiusMeters=16.0,
        floors=[1],
        polygon=_paddedRectPolygon(12.107910, 12.108110, -86.256750, -86.256610, padMeters=3.0),
        bufferMeters=7.0,
    ),
    "jaguarJungle": BuildingBoundary(
        buildingId="jaguarJungle",
        boundaryType="polygon",
        center=(12.108073, -86.257787),
        radiusMeters=18.0,
        floors=[1],
        polygon=_paddedRectPolygon(12.107980, 12.108140, -86.257855, -86.257660, padMeters=3.5),
        bufferMeters=7.0,
    ),
    "areaDeMesas": BuildingBoundary(
        buildingId="areaDeMesas",
        boundaryType="radius",
        center=(12.108195, -86.257314),
        radiusMeters=14.0,
        floors=[1],
        bufferMeters=7.0,
    ),
    "miRanchito": BuildingBoundary(
        buildingId="miRanchito",
        boundaryType="radius",
        center=(12.108058, -86.257323),
        radiusMeters=12.0,
        floors=[1],
        bufferMeters=6.0,
    ),
    "labDigitalFia": BuildingBoundary(
        buildingId="labDigitalFia",
        boundaryType="radius",
        center=(12.108110, -86.257290),
        radiusMeters=10.0,
        floors=[1],
        bufferMeters=6.0,
    ),
    "mainParking": BuildingBoundary(
        buildingId="mainParking",
        boundaryType="radius",
        center=(12.109617, -86.256553),
        radiusMeters=32.0,
        floors=[1],
        bufferMeters=12.0,
    ),
    "northGate": BuildingBoundary(
        buildingId="northGate",
        boundaryType="radius",
        center=(12.107223, -86.256261),
        radiusMeters=24.0,
        floors=[1],
        bufferMeters=10.0,
    ),
    "northeastGate": BuildingBoundary(
        buildingId="northeastGate",
        boundaryType="radius",
        center=(12.106364, -86.258808),
        radiusMeters=30.0,
        floors=[1],
        bufferMeters=12.0,
    ),
}


# =============================================================================
# INDOOR BEACON REGISTRY (OPTIONAL BLE / WI-FI / NFC FLOOR RESOLUTION)
# =============================================================================
# When an indoor beacon identifier is available alongside GPS, it immediately
# resolves the exact floor (and optionally the nearest anchor room) without
# relying on noisy indoor GPS altitude.

def _buildBeaconRegistry() -> Dict[str, Dict[str, Any]]:
    registry: Dict[str, Dict[str, Any]] = {}
    letterBuildings = {
        f"building{letter}": letter for letter in "ABCDEFGHIJKLMNOP"
    }
    for buildingId, boundary in BUILDING_BOUNDARIES.items():
        shortCode = letterBuildings.get(buildingId, buildingId.upper())
        for fl in boundary.floors:
            code = f"UAM-{shortCode}-F{fl}"
            registry[code] = {
                "beaconId": code,
                "buildingId": buildingId,
                "floorLevel": fl,
                "nodeId": None,
            }
    return registry


BEACON_REGISTRY: Dict[str, Dict[str, Any]] = _buildBeaconRegistry()


def resolveBeacon(beaconId: Optional[str]) -> Optional[Dict[str, Any]]:
    """Looks up an indoor beacon ID (case-insensitive) to resolve building and floor."""
    if not beaconId:
        return None
    normalized = str(beaconId).strip().upper().replace("_", "-")
    return BEACON_REGISTRY.get(normalized)


def getBuildingBoundary(buildingId: str) -> Optional[BuildingBoundary]:
    """Returns the defined BuildingBoundary for a given macro building ID."""
    return BUILDING_BOUNDARIES.get(buildingId)


def getAllBuildingBoundaries() -> Dict[str, BuildingBoundary]:
    """Returns a shallow copy of all defined campus building boundaries."""
    return dict(BUILDING_BOUNDARIES)


def evaluateAllBuildingBoundaries(lat: float, lng: float) -> List[Dict[str, Any]]:
    """
    Evaluates (lat, lng) against every defined building polygon and radius check,
    returning results sorted by (inside first, boundary distance, center distance).
    """
    results = [boundary.evaluatePoint(lat, lng) for boundary in BUILDING_BOUNDARIES.values()]
    results.sort(
        key=lambda r: (
            0 if r["isInsideBoundary"] else (1 if r["withinBuffer"] else 2),
            r["distanceToBoundaryMeters"],
            r["distanceToCenterMeters"],
        )
    )
    return results
