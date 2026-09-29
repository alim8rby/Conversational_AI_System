import os
import time

from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS

from agents.conversation_agent import ConversationAgent
from voice.voice_engine import VoiceEngine
from observability.run import finish_run, record_error, persist_run

app = Flask(__name__, static_folder="static")
CORS(app)
agent = ConversationAgent()
voice = VoiceEngine(default_lang="en")

@app.get("/")
def index():
    return send_from_directory(app.static_folder, "index.html")

@app.post("/chat")
def chat():
    data = request.get_json(silent=True) or {}
    session_id = str(data.get("session", "")).strip()
    user_message = str(data.get("message", "")).strip()
    if not session_id or not user_message:
        return jsonify({"error": "Session ID and message are required."}), 400
    try:
        reply = agent.ask(session_id, user_message)
        run = getattr(agent, "last_run", None)
        audio_path = os.path.join("static", "tts", f"{session_id}.mp3")
        voice_started = time.perf_counter()
        try:
            voice.text_to_speech(reply, audio_path)
            voice_latency_ms = round((time.perf_counter() - voice_started) * 1000, 2)
            if run is not None:
                run["metrics"]["voice"] = {
                    "voice_latency_ms": voice_latency_ms,
                    "voice_success": True,
                }
                persist_run(run)
        except Exception:
            voice_latency_ms = round((time.perf_counter() - voice_started) * 1000, 2)
            if run is not None:
                run["metrics"]["voice"] = {
                    "voice_latency_ms": voice_latency_ms,
                    "voice_success": False,
                }
                record_error(run, "voice", "TTS generation failed")
                finish_run(run, "failed")
            raise
        return jsonify({"reply": reply, "audio": f"/static/tts/{session_id}.mp3"})
    except Exception:
        app.logger.exception("Chat request failed")
        return jsonify({"error": "Unable to process the request."}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", "8000")), debug=False)
