"""
config.py
================================================================================
CENTRAL CONFIGURATION FOR JAGUARFIND & JAGUARMAPS
================================================================================
"""

import os
from pathlib import Path

try:
    from dotenv import load_dotenv
except ImportError:
    def load_dotenv(*args, **kwargs):
        return False

# Base project directory
BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")

class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "uam-jaguarfind-secret-key-2026")
    DATABASE_PATH = os.environ.get("DATABASE_PATH", str(BASE_DIR / "jaguarFind.db"))
    LANGUAGES_DIR = os.environ.get("LANGUAGES_DIR", str(BASE_DIR / "backend" / "languages"))
    DEFAULT_LANGUAGE = "spa"
    VISITOR_INACTIVITY_DAYS = 180
    AZURE_SPEECH_ENDPOINT = os.environ.get(
        "AZURE_SPEECH_ENDPOINT",
        "https://jaguar-find-speech-services.cognitiveservices.azure.com/",
    )
    AZURE_SPEECH_REGION = os.environ.get("AZURE_SPEECH_REGION", "westus")
    AZURE_SPEECH_RESOURCE_ID = os.environ.get(
        "AZURE_SPEECH_RESOURCE_ID",
        "/subscriptions/6b13b2aa-a56b-41ad-a767-a0647121fd1b/resourceGroups/jaguar-find-rg/providers/Microsoft.CognitiveServices/accounts/jaguar-find-speech-services",
    )
    AZURE_MANAGED_IDENTITY_CLIENT_ID = os.environ.get(
        "AZURE_MANAGED_IDENTITY_CLIENT_ID"
    )
