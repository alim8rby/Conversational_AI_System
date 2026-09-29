"""Health and readiness helpers kept separate from model request handling."""

from flask import jsonify

from config.settings import load_settings


def health_response():
    return jsonify({"status": "ok"}), 200


def readiness_response():
    try:
        load_settings(require_providers=True)
    except RuntimeError as exc:
        return jsonify({"status": "not_ready", "reason": str(exc)}), 503
    return jsonify({"status": "ready"}), 200
