"""
i18n.py
================================================================================
GLOBAL INTERNATIONALIZATION (i18n) ENGINE FOR JAGUARFIND & JAGUARMAPS
================================================================================
Centralizes multi-language support (English 'eng' and Spanish 'spa') across all
system modules:
- Flask Web Templates (Jinja2 context processor 't(key)')
- RESTful Web APIs (/api/ruta, /api/puntos, /api/idioma)
- Navigation Engine & Dijkstra Router (graph package)
- Authentication & Lost & Found feedback / flash messages
================================================================================
"""

import json
import os
from pathlib import Path
from typing import Any, Dict, List, Optional


def normalize_language(lang: Optional[str], default: str = "eng") -> str:
    """Normalizes language identifiers (e.g. 'es', 'es-NI', 'spa' -> 'spa'; 'en', 'eng' -> 'eng')."""
    if not lang:
        return default
    clean = str(lang).strip().lower()
    if clean.startswith("sp") or clean.startswith("es"):
        return "spa"
    if clean.startswith("en"):
        return "eng"
    return default


class I18nManager:
    """
    Singleton service managing translation dictionaries, language detection,
    and string formatting for both backend logic and Jinja2 templates.
    """
    _instance: Optional["I18nManager"] = None

    def __init__(self, languagesDir: Optional[str] = None):
        self.translations: Dict[str, Dict[str, Any]] = {}
        self.defaultLang: str = "eng"
        self.supportedLanguages: List[str] = ["eng", "spa"]
        self.languagesDir: Path = self._resolveLanguagesDir(languagesDir)
        self.loadDictionaries()

    @classmethod
    def getInstance(cls) -> "I18nManager":
        if cls._instance is None:
            cls._instance = I18nManager()
        return cls._instance

    def _resolveLanguagesDir(self, customPath: Optional[str] = None) -> Path:
        if customPath and os.path.isdir(customPath):
            return Path(customPath)

        backendRoot = Path(__file__).resolve().parent
        projectRoot = backendRoot.parent
        candidates = [
            backendRoot / "languages",
            projectRoot / "backend" / "languages",
            projectRoot / "languages",
            Path.cwd() / "backend" / "languages",
            Path.cwd() / "languages",
        ]
        for candidate in candidates:
            if candidate.is_dir() and (candidate / "eng.json").exists():
                return candidate

        return backendRoot / "languages"

    def loadDictionaries(self) -> None:
        """Loads all supported language JSON files into memory."""
        for lang in self.supportedLanguages:
            filePath = self.languagesDir / f"{lang}.json"
            if filePath.exists():
                try:
                    with open(filePath, "r", encoding="utf-8") as f:
                        self.translations[lang] = json.load(f)
                except Exception:
                    self.translations[lang] = {}
            else:
                self.translations[lang] = {}

    def getCurrentLanguage(self) -> str:
        """
        Determines current language:
        1. Checks Flask user session ('session["idioma"]' or 'session["lang"]') if inside request context.
        2. Falls back to self.defaultLang ('eng').
        """
        try:
            from flask import session, has_request_context
            if has_request_context():
                lang = session.get("idioma") or session.get("lang")
                if lang:
                    return normalize_language(lang, default=self.defaultLang)
        except ImportError:
            pass

        return self.defaultLang

    def getRaw(self, keyPath: str, lang: Optional[str] = None, default: Any = None) -> Any:
        """Returns the raw nested translation entry (string, dict, or list) for a key path."""
        activeLang = normalize_language(lang, default=self.getCurrentLanguage()) if lang else self.getCurrentLanguage()
        dictForLang = self.translations.get(activeLang, {})
        val = self._nestedLookup(dictForLang, keyPath)
        if val is None and activeLang != self.defaultLang:
            val = self._nestedLookup(self.translations.get(self.defaultLang, {}), keyPath)
        return val if val is not None else default

    def get(
        self,
        keyPath: str,
        lang: Optional[str] = None,
        default: Optional[str] = None,
        **kwargs
    ) -> str:
        """
        Translates a dotted key path (e.g. 'nav.home', 'map.steps', 'navigation.start_route').
        Supports:
        - Dot notation traversal across nested JSON structures.
        - Dynamic session-based language resolution if lang is omitted.
        - Fallback to English if key is missing in target language.
        - Safe keyword argument formatting with {param}.
        """
        activeLang = normalize_language(lang, default=self.getCurrentLanguage()) if lang else self.getCurrentLanguage()
        dictForLang = self.translations.get(activeLang, {})

        val = self._nestedLookup(dictForLang, keyPath)

        # Fallback to default language if missing in active language
        if val is None and activeLang != self.defaultLang:
            val = self._nestedLookup(self.translations.get(self.defaultLang, {}), keyPath)

        if val is None:
            val = default if default is not None else keyPath

        if kwargs and isinstance(val, str):
            try:
                return val.format(**kwargs)
            except (KeyError, IndexError, ValueError):
                return val

        return str(val)

    def _nestedLookup(self, d: Dict[str, Any], keyPath: str) -> Optional[Any]:
        keys = keyPath.split(".")
        current = d
        for k in keys:
            if isinstance(current, dict) and k in current:
                current = current[k]
            else:
                return None
        return current

    def getNodeName(self, nodeId: str, lang: Optional[str] = None, fallbackName: str = "") -> str:
        return self.get(f"nodes.{nodeId}", lang=lang, default=fallbackName or nodeId)

    def getWalkwayInstruction(self, u: str, v: str, lang: Optional[str] = None, fallback: str = "") -> str:
        edgeKey = f"{u}_{v}"
        return self.get(f"walkways.{edgeKey}", lang=lang, default=fallback)

    def getAccessNotice(self, nodeId: str, lang: Optional[str] = None, fallback: Optional[str] = None) -> Optional[str]:
        notice = self.get(f"access_notices.{nodeId}", lang=lang, default="")
        if notice:
            return notice
        return fallback


# Global shorthand translation function
def t(keyPath: str, lang: Optional[str] = None, default: Optional[str] = None, **kwargs) -> str:
    """
    Global translation helper function.
    Can be called from anywhere: Python files, services, routes, or Jinja2 templates.
    """
    return I18nManager.getInstance().get(keyPath, lang=lang, default=default, **kwargs)


def get_current_language() -> str:
    """Returns the currently active language code ('eng' or 'spa')."""
    return I18nManager.getInstance().getCurrentLanguage()


def t_raw(keyPath: str, lang: Optional[str] = None, default: Any = None) -> Any:
    """Returns the raw nested translation object (dict/list/str) for a dotted key path."""
    return I18nManager.getInstance().getRaw(keyPath, lang=lang, default=default)


def init_i18n(app) -> None:
    """
    Flask extension registration helper:
    Injects 't(key)', 't_raw(key)', and 'current_language' into all Jinja2 template contexts.
    """
    @app.context_processor
    def inject_i18n():
        return {
            "t": t,
            "t_raw": t_raw,
            "current_language": get_current_language(),
            "available_languages": I18nManager.getInstance().supportedLanguages
        }
