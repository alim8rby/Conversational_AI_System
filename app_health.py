"""Health and readiness helpers kept separate from model request handling."""

from urllib.error import URLError
from urllib.request import urlopen

from flask import jsonify

from config.settings import load_settings


def health_response():
    return jsonify({"status": "ok"}), 200


def readiness_response():
    try:
        settings = load_settings(require_runtime=True)
        with urlopen(f"{settings.ollama_base_url.rstrip('/')}/api/tags", timeout=2):
            pass
    except (RuntimeError, OSError, URLError) as exc:
        return jsonify({"status": "not_ready", "reason": str(exc)}), 503
    return jsonify({"status": "ready"}), 200
