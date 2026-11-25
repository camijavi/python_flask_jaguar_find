"""
placesCatalog.py
Re-exports the canonical campus places catalog from backend.data.placesCatalog.
"""

from backend.data.placesCatalog import (
    PLACES_CATALOG,
    getPlacesByCategory,
    getPlacesByBuilding,
)

__all__ = ["PLACES_CATALOG", "getPlacesByCategory", "getPlacesByBuilding"]
