from dotenv import load_dotenv

load_dotenv()

import os
import time

from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS

from agents.conversation_agent import ConversationAgent
from voice.voice_engine import VoiceEngine
from app_health import health_response, readiness_response
from config.settings import load_settings
from observability.run import finish_run, record_error, persist_run
from product.session_state import build_session_state
from product.memory_inspector import inspect_memory
from product.evaluation_lab import build_evaluation_lab
from product.failure_observatory import build_failure_observatory
from product.operations import build_operations

app = Flask(__name__, static_folder="static")
app.config["MAX_CONTENT_LENGTH"] = 16 * 1024
settings = load_settings(require_runtime=False)
CORS(app, resources={r"/*": {"origins": [origin.strip() for origin in settings.cors_origins.split(",") if origin.strip()]}})

@app.after_request
def security_headers(response):
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["Referrer-Policy"] = "no-referrer"
    response.headers["Cache-Control"] = "no-store"
    return response

@app.get("/health")
def health():
    return health_response()

@app.get("/ready")
def ready():
    return readiness_response()
agent = ConversationAgent()
voice = VoiceEngine(default_lang="en")

@app.get("/")
def index():
    return send_from_directory(app.static_folder, "index.html")

@app.get("/session/<session_id>/state")
def session_state(session_id):
    if not session_id.strip() or len(session_id) > 128:
        return jsonify({"error": "Invalid session ID."}), 400
    return jsonify(build_session_state(
        agent.interviewer,
        session_id,
        intake_enabled=agent.intake_enabled,
        assistant_name=agent.domain.assistant["name"],
    ))

@app.post("/session/<session_id>/start")
def start_session(session_id):
    if not session_id.strip() or len(session_id) > 128:
        return jsonify({"error": "Invalid session ID."}), 400
    data = request.get_json(silent=True) or {}
    lang = str(data.get("lang", "en")).strip().lower()
    if lang not in {"en", "ar"}:
        return jsonify({"error": "Language must be 'en' or 'ar'."}), 400
    try:
        reply = agent.start_session(session_id, lang)
        return jsonify({"reply": reply})
    except Exception:
        app.logger.exception("Session start failed")
        return jsonify({"error": "Unable to start the session."}), 500

@app.get("/session/<session_id>/memory")
def memory_inspector(session_id):
    query = request.args.get("q", "").strip()
    try:
        k = int(request.args.get("k", "3"))
        result = inspect_memory(agent.mem, session_id, query, k)
    except (ValueError, TypeError) as exc:
        return jsonify({"error": str(exc)}), 400
    except Exception:
        app.logger.exception("Memory inspection failed")
        return jsonify({"error": "Unable to inspect memory."}), 500
    return jsonify(result)

@app.get("/evaluation")
def evaluation_lab():
    try:
        return jsonify(build_evaluation_lab())
    except Exception:
        app.logger.exception("Evaluation lab failed")
        return jsonify({"error": "Unable to load evaluation data."}), 500

@app.get("/failures")
def failures():
    try:
        result = build_failure_observatory(
            category=request.args.get("category") or None,
            stage=request.args.get("stage") or None,
            severity=request.args.get("severity") or None,
            status=request.args.get("status") or None,
        )
        return jsonify(result)
    except Exception:
        app.logger.exception("Failure observatory failed")
        return jsonify({"error": "Unable to load failure data."}), 500

@app.get("/operations")
def operations():
    try:
        return jsonify(build_operations())
    except Exception:
        app.logger.exception("Operations dashboard failed")
        return jsonify({"error": "Unable to load operations data."}), 500

@app.get("/failures/<failure_id>")
def failure_detail(failure_id):
    from observability.failure_store import FailureStore
    failure = FailureStore().get_failure(failure_id)
    if failure is None:
        return jsonify({"error": "Failure not found."}), 404
    return jsonify(failure)

@app.post("/chat")
def chat():
    data = request.get_json(silent=True) or {}
    session_id = str(data.get("session", "")).strip()
    user_message = str(data.get("message", "")).strip()
    if len(session_id) > 128 or len(user_message) > 4000:
        return jsonify({"error": "Session ID or message exceeds the allowed size."}), 413
    if not session_id or not user_message:
        return jsonify({"error": "Session ID and message are required."}), 400
    request_started = time.perf_counter()
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
                run["metrics"]["total_latency_ms"] = round(
                    (time.perf_counter() - request_started) * 1000, 2
                )
                persist_run(run)
        except Exception:
            voice_latency_ms = round((time.perf_counter() - voice_started) * 1000, 2)
            if run is not None:
                run["metrics"]["voice"] = {
                    "voice_latency_ms": voice_latency_ms,
                    "voice_success": False,
                }
                run["metrics"]["total_latency_ms"] = round(
                    (time.perf_counter() - request_started) * 1000, 2
                )
                record_error(run, "voice", "TTS generation failed")
                finish_run(run, "failed")
            raise
        return jsonify({"reply": reply, "audio": f"/static/tts/{session_id}.mp3"})
    except Exception:
        run = getattr(agent, "last_run", None)
        if run is not None and run.get("status") == "started":
            run["metrics"]["total_latency_ms"] = round(
                (time.perf_counter() - request_started) * 1000, 2
            )
            record_error(run, "application", "Chat request failed")
            finish_run(run, "failed")
        app.logger.exception("Chat request failed")
        return jsonify({"error": "Unable to process the request."}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", "8000")), debug=False)
