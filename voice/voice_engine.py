"""Text-to-speech adapter with explicit session-language control."""

from __future__ import annotations

from pathlib import Path

from gtts import gTTS


SUPPORTED_LANGUAGES = {"en", "ar"}


class VoiceEngine:
    def __init__(self, default_lang: str = "en"):
        if default_lang not in SUPPORTED_LANGUAGES:
            raise ValueError("default_lang must be 'en' or 'ar'")
        self.default_lang = default_lang

    def text_to_speech(
        self,
        text: str,
        filename: str,
        language: str | None = None,
    ) -> str:
        """Generate an MP3 using the explicit session language."""
        lang = language or self.default_lang
        if lang not in SUPPORTED_LANGUAGES:
            raise ValueError("language must be 'en' or 'ar'")

        path = Path(filename)
        path.parent.mkdir(parents=True, exist_ok=True)
        gTTS(text=text, lang=lang).save(path)
        return str(path)
