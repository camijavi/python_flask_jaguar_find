"""
categoryModel.py
================================================================================
CATEGORY METADATA & PLACE CATALOG ITEM MODELS (PYTHON DATACLASS)
================================================================================
"""

from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class CategoryMetadata:
    category: str
    labelSpanish: str
    labelEnglish: str
    icon: str                         # FontAwesome / Lucide icon name
    badgeColor: str                   # UI color class (e.g. "blue", "emerald")


@dataclass
class PlaceCatalogItem:
    placeId: str
    name: str
    category: str
    parentBuildingId: str
    floorLevel: int = 1
    isAccessible: bool = True
    locationNotes: str = ""
    keywords: List[str] = field(default_factory=list)
