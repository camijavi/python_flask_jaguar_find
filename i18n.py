"""
i18n.py
================================================================================
Backward-compatible root facade for the unified backend internationalization
engine (`backend.i18n`). Ensures a single I18nManager singleton and dictionary
source (`backend/languages/`) across all modules.
================================================================================
"""

from backend.i18n import (
    I18nManager,
    normalize_language,
    t,
    t_raw,
    get_current_language,
    init_i18n,
)

__all__ = [
    "I18nManager",
    "normalize_language",
    "t",
    "t_raw",
    "get_current_language",
    "init_i18n",
]
