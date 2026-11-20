"""
graph/i18n.py
Backward-compatible facade for the global i18n module.
Re-exports I18nManager, t, get_current_language, and init_i18n from the root i18n module.
"""

from i18n import I18nManager, t, get_current_language, init_i18n

__all__ = ["I18nManager", "t", "get_current_language", "init_i18n"]
