from __future__ import annotations

from dotenv import load_dotenv

load_dotenv()

import os
import re
import time
from pathlib import Path

from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS

from agents.conversation_agent import ConversationAgent
from app_health import health_response, readiness_response
from config.settings import load_settings
from observability.run import finish_run, persist_run, record_error
from product.evaluation_lab import build_evaluation_lab
from product.failure_observatory import build_failure_observatory
from product.memory_inspector import inspect_memory
from product.operations import build_operations
from product.session_state import build_session_state
from voice.voice_engine import VoiceEngine


SESSION_ID_PATTERN = re.compile(r"^[A-Za-z0-9_-]{1,128}$")
SAFE_AUDIO_ROOT = (Path("static") / "tts").resolve()

app = Flask(__name__, static_folder="static")
app.config["MAX_CONTENT_LENGTH"] = 16 * 1024

settings = load_settings(require_runtime=False)
CORS(
    app,
    resources={
        r"/*": {
            "origins": [
                origin.strip()
                for origin in settings.cors_origins.split(",")
                if origin.strip()
            ]
        }
    },
)

agent = ConversationAgent()
voice = VoiceEngine(default_lang="en")


@app.after_request
def security_headers(response):
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["Referrer-Policy"] = "no-referrer"
    response.headers["Cache-Control"] = "no-store"
    return response


def _valid_session_id(session_id: str) -> bool:
    return bool(SESSION_ID_PATTERN.fullmatch(session_id.strip()))


def _audio_path(session_id: str) -> tuple[Path, str]:
    if not _valid_session_id(session_id):
        raise ValueError("Invalid session ID.")

    path = (SAFE_AUDIO_ROOT / f"{session_id}.mp3").resolve()
    if path.parent != SAFE_AUDIO_ROOT:
        raise ValueError("Invalid audio path.")

    path.parent.mkdir(parents=True, exist_ok=True)
    return path, path.relative_to(Path("static")).as_posix()


@app.get("/health")
def health():
    return health_response()


@app.get("/ready")
def ready():
    return readiness_response()


@app.get("/")
def index():
    return send_from_directory(app.static_folder, "index.html")


@app.get("/session/<session_id>/state")
def session_state(session_id):
    if not _valid_session_id(session_id):
        return jsonify({"error": "Invalid session ID."}), 400

    return jsonify(
        build_session_state(
            agent.interviewer,
            session_id,
            intake_enabled=agent.intake_enabled,
            assistant_name=agent.domain.assistant["name"],
        )
    )


@app.post("/session/<session_id>/start")
def start_session(session_id):
    if not _valid_session_id(session_id):
        return jsonify({"error": "Invalid session ID."}), 400

    data = request.get_json(silent=True) or {}
    lang = str(data.get("lang", "en")).strip().lower()
    if lang not in {"en", "ar"}:
        return jsonify({"error": "Language must be 'en' or 'ar'."}), 400

    try:
        reply = agent.start_session(session_id, lang)
        return jsonify({"reply": reply, "language": lang})
    except Exception:
        app.logger.exception("Session start failed")
        return jsonify({"error": "Unable to start the session."}), 500


@app.get("/session/<session_id>/memory")
def memory_inspector(session_id):
    if not _valid_session_id(session_id):
        return jsonify({"error": "Invalid session ID."}), 400

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
        return jsonify(
            build_failure_observatory(
                category=request.args.get("category") or None,
                stage=request.args.get("stage") or None,
                severity=request.args.get("severity") or None,
                status=request.args.get("status") or None,
            )
        )
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

    if not _valid_session_id(session_id):
        return jsonify({"error": "Invalid session ID."}), 400
    if not user_message:
        return jsonify({"error": "Session ID and message are required."}), 400
    if len(user_message) > 4000:
        return jsonify({"error": "Message exceeds the allowed size."}), 413

    request_started = time.perf_counter()

    try:
        reply = agent.ask(session_id, user_message)
        run = getattr(agent, "last_run", None)
        language = (
            run.get("language", "en")
            if run is not None
            else agent.session_languages.get(session_id, "en")
        )

        audio_path, audio_url_path = _audio_path(session_id)

        try:
            voice_started = time.perf_counter()
            voice.text_to_speech(reply, str(audio_path), language=language)
            voice_latency_ms = round((time.perf_counter() - voice_started) * 1000, 2)

            if run is not None:
                run["metrics"]["voice"] = {
                    "voice_latency_ms": voice_latency_ms,
                    "voice_success": True,
                    "language": language,
                }
                run["metrics"]["total_latency_ms"] = round(
                    (time.perf_counter() - request_started) * 1000, 2
                )
                persist_run(run)
        except Exception:
            if run is not None:
                run["metrics"]["voice"] = {
                    "voice_latency_ms": round((time.perf_counter() - request_started) * 1000, 2),
                    "voice_success": False,
                    "language": language,
                }
                record_error(
                    run,
                    "voice",
                    "TTS generation failed",
                    expected_behavior="TTS output is generated in the selected session language.",
                )
                finish_run(run, "failed")
            raise

        return jsonify(
            {
                "reply": reply,
                "audio": f"/static/{audio_url_path}",
                "language": language,
            }
        )

    except Exception:
        run = getattr(agent, "last_run", None)
        if run is not None and run.get("status") == "started":
            record_error(
                run,
                "application",
                "Chat request failed",
                expected_behavior="Chat request completes with a valid response.",
            )
            finish_run(run, "failed")

        app.logger.exception("Chat request failed")
        return jsonify({"error": "Unable to process the request."}), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", "8000")), debug=False)
