"""
routeModel.py
================================================================================
CAMPUS ROUTE & NAVIGATION DTO MODELS (PYTHON DATACLASS)
================================================================================
"""

from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class RouteCoordinate:
    nodeId: str
    name: str
    xPercent: float
    yPercent: float
    lat: float
    lng: float


@dataclass
class RouteRequest:
    origin: str                       # Macro nodeId or POI search string
    destination: str
    accessibleOnly: bool = False      # Wheelchair accessibility (bypasses stairs)
    lang: str = "spa"


@dataclass
class RouteResult:
    success: bool
    origin: str = ""
    destination: str = ""
    category: str = ""
    floorLevel: int = 1
    pathNodeIds: List[str] = field(default_factory=list)
    pathCoordinates: List[RouteCoordinate] = field(default_factory=list)
    totalDistanceMeters: float = 0.0
    estimatedWalkingMinutes: int = 0
    stepInstructions: List[str] = field(default_factory=list)
    isAccessibleRoute: bool = False
    error: Optional[str] = None
