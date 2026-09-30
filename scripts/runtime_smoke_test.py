"""Smoke-test the running local conversational AI application."""

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
    with urlopen(request, timeout=30) as response:
        return json.loads(response.read().decode("utf-8"))


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Verify the local Flask + Ollama conversational runtime."
    )
    parser.add_argument("--base-url", default="http://localhost:8000")
    parser.add_argument("--session", default="runtime-smoke")
    args = parser.parse_args()

    base_url = args.base_url.rstrip("/")

    try:
        health = request_json(f"{base_url}/health")
        readiness = request_json(f"{base_url}/ready")
        request_json(
            f"{base_url}/session/{args.session}/start",
            method="POST",
            payload={"lang": "en"},
        )
        chat = request_json(
            f"{base_url}/chat",
            method="POST",
            payload={
                "session": args.session,
                "message": "What is the price of TrailRunner X1?",
            },
        )
    except (HTTPError, URLError, TimeoutError) as exc:
        raise SystemExit(f"Runtime smoke test failed: {exc}") from exc

    if not isinstance(health, dict):
        raise SystemExit("Health endpoint returned an invalid response.")

    if not isinstance(readiness, dict):
        raise SystemExit("Readiness endpoint returned an invalid response.")

    reply = str(chat.get("reply", "")).strip()
    if not reply:
        raise SystemExit("Chat endpoint returned an empty reply.")

    print("Runtime smoke test passed.")
    print(f"Health: {health}")
    print(f"Readiness: {readiness}")
    print(f"Reply: {reply}")


if __name__ == "__main__":
    main()
