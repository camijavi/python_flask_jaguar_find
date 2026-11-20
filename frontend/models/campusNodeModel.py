"""
campusNodeModel.py
================================================================================
CAMPUS NODE & WAYPOINT DATA MODEL (PYTHON DATACLASS)
================================================================================
"""

from dataclasses import dataclass
from typing import Optional


@dataclass
class CampusNodeModel:
    nodeId: str
    name: str
    category: str
    xPercent: float                   # 0.0% to 100.0% X position on campus SVG map
    yPercent: float                   # 0.0% to 100.0% Y position on campus SVG map
    lat: float                        # GPS latitude
    lng: float                        # GPS longitude
    floorLevel: int = 1
    accessLevel: str = "public"       # "public" | "restricted" | "facultyOnly"
    accessNotice: Optional[str] = None
    isOutdoorAccessPoint: bool = True
