# voice/voice_engine.py

import os
from gtts import gTTS

class VoiceEngine:
    def __init__(self, lang: str = "en"):
        self.lang = lang

    def text_to_speech(self, text: str, filename: str) -> str:
        """
        Generate an MP3 of `text` in the chosen language,
        save to `filename` (creating dirs as needed), and return the path.
        """
        tts = gTTS(text=text, lang=self.lang)
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        tts.save(filename)
        return filename
