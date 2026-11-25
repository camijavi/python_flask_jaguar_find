"""
graph/i18n.py
Backward-compatible facade for the unified global i18n module (`backend.i18n`).
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
