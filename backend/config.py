"""
config.py
================================================================================
CENTRAL CONFIGURATION FOR JAGUARFIND & JAGUARMAPS
================================================================================
"""

import os
from pathlib import Path

# Base project directory
BASE_DIR = Path(__file__).resolve().parent.parent

class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "uam-jaguarfind-secret-key-2026")
    DATABASE_PATH = os.environ.get("DATABASE_PATH", str(BASE_DIR / "jaguarFind.db"))
    LANGUAGES_DIR = os.environ.get("LANGUAGES_DIR", str(BASE_DIR / "backend" / "languages"))
    DEFAULT_LANGUAGE = "spa"
    VISITOR_INACTIVITY_DAYS = 180
