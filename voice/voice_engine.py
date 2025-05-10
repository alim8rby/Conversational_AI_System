# voice/voice_engine.py

import os
import re
from gtts import gTTS

class VoiceEngine:
    def __init__(self, default_lang: str = "en"):
        self.default_lang = default_lang

    def _detect_lang(self, text: str) -> str:
        """
        If the text contains Arabic letters → 'ar'.
        Else if it contains digits (Franco-Arab) → 'ar' (so romanized Arabic still uses Arabic TTS).
        Otherwise → use the default (usually 'en').
        """
        if re.search(r'[\u0600-\u06FF]', text):
            return 'ar'
        if re.search(r'\d', text):
            return 'ar'
        return self.default_lang

    def text_to_speech(self, text: str, filename: str) -> str:
        """
        Generate an MP3 of `text` in the detected language,
        save to `filename`, and return the path.
        """
        lang = self._detect_lang(text)
        tts = gTTS(text=text, lang=lang)
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        tts.save(filename)
        return filename
