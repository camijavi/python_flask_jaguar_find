"""
Azure Speech text-to-speech service using Microsoft Entra ID.
"""

from __future__ import annotations

import time
from typing import Optional
from xml.sax.saxutils import escape

from azure.identity import DefaultAzureCredential
import requests


class AzureSpeechService:
    VOICES = {
        "es-MX": "es-MX-DaliaNeural",
        "en-US": "en-US-CoraMultilingualNeural",
    }

    def __init__(
        self,
        endpoint: str,
        region: str,
        resource_id: str,
        managed_identity_client_id: Optional[str] = None,
    ) -> None:
        self.endpoint = endpoint.rstrip("/") + "/"
        self.region = region
        self.resource_id = resource_id
        self._credential = DefaultAzureCredential(
            managed_identity_client_id=managed_identity_client_id
        )
        self._access_token = None

    def _getAccessToken(self) -> str:
        now = time.time()
        if (
            self._access_token is None
            or getattr(self._access_token, "expires_on", 0) <= now + 300
        ):
            self._access_token = self._credential.get_token(
                "https://cognitiveservices.azure.com/.default"
            )
        return f"aad#{self.resource_id}#{self._access_token.token}"

    def synthesize(self, text: str, language: str = "es-MX") -> bytes:
        cleanText = str(text or "").strip()
        if not cleanText:
            raise ValueError("api.speech_text_required")
        if len(cleanText) > 2000:
            raise ValueError("api.speech_text_too_long")

        normalizedLanguage = "en-US" if str(language).lower().startswith("en") else "es-MX"
        voiceName = self.VOICES[normalizedLanguage]

        if not self.resource_id:
            raise RuntimeError("api.speech_not_configured")

        synthesisEndpoint = (
            f"https://{self.region}.tts.speech.microsoft.com/cognitiveservices/v1"
        )

        ssml = (
            '<speak version="1.0" xmlns="http://www.w3.org/2001/10/synthesis" '
            f'xml:lang="{normalizedLanguage}">'
            f'<voice xml:lang="{normalizedLanguage}" name="{voiceName}">'
            f"{escape(cleanText)}"
            "</voice></speak>"
        )

        response = requests.post(
            synthesisEndpoint,
            headers={
                "Authorization": f"Bearer {self._getAccessToken()}",
                "Content-Type": "application/ssml+xml",
                "X-Microsoft-OutputFormat": "riff-24khz-16bit-mono-pcm",
                "User-Agent": "JaguarFind",
            },
            data=ssml.encode("utf-8"),
            timeout=30,
        )

        if not response.ok:
            raise RuntimeError(
                f"Azure Speech REST returned HTTP {response.status_code}: "
                f"{response.text[:500]}"
            )

        if not response.content:
            raise RuntimeError("Azure Speech returned an empty audio response.")

        return response.content
