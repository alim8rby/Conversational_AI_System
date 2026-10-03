"""Smoke-test the running local ShopAssist runtime."""

from __future__ import annotations

import argparse
import json
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


def request_json(url: str, method: str = "GET", payload: dict | None = None) -> dict:
    data = None
    headers = {}
    if payload is not None:
        data = json.dumps(payload).encode("utf-8")
        headers["Content-Type"] = "application/json"

    request = Request(url, data=data, headers=headers, method=method)
    with urlopen(request, timeout=60) as response:
        return json.loads(response.read().decode("utf-8"))


def main() -> None:
    parser = argparse.ArgumentParser(description="Verify the local Flask + Ollama ShopAssist runtime.")
    parser.add_argument("--base-url", default="http://localhost:8000")
    parser.add_argument("--session", default="runtime-smoke")
    parser.add_argument("--language", choices=("en", "ar"), default="en")
    args = parser.parse_args()

    base_url = args.base_url.rstrip("/")

    try:
        health = request_json(f"{base_url}/health")
        readiness = request_json(f"{base_url}/ready")
        started = request_json(
            f"{base_url}/session/{args.session}/start",
            method="POST",
            payload={"lang": args.language},
        )
        chat = request_json(
            f"{base_url}/chat",
            method="POST",
            payload={"session": args.session, "message": "What is the price of TrailRunner X1?"},
        )
    except (HTTPError, URLError, TimeoutError) as exc:
        raise SystemExit(f"Runtime smoke test failed: {exc}") from exc

    if health.get("status") != "ok":
        raise SystemExit(f"Health check failed: {health}")
    if readiness.get("status") != "ready":
        raise SystemExit(f"Readiness check failed: {readiness}")

    initial_reply = str(started.get("reply", "")).strip()
    reply = str(chat.get("reply", "")).strip()
    audio = str(chat.get("audio", "")).strip()

    if not initial_reply:
        raise SystemExit("Session start returned an empty assistant message.")
    if not reply:
        raise SystemExit("Chat endpoint returned an empty reply.")

    print("Runtime smoke test passed.")
    print(f"Assistant start: {initial_reply}")
    print(f"Business response: {reply}")
    print(f"Voice artifact: {audio or 'not returned'}")
    print("Business scenario: product pricing → ShopAssist")
    print("Inspectable surfaces: /session/<id>/memory, /evaluation, /failures, /operations")


if __name__ == "__main__":
    main()
