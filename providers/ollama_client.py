"""Local Ollama provider client.

Keeps LLM and embedding calls behind one small provider interface so the
application does not depend on a paid hosted AI provider for development.
"""

from __future__ import annotations

import json
import urllib.error
import urllib.request
from typing import Any, Dict, List


class OllamaClient:
    def __init__(self, base_url: str, model: str, embed_model: str, timeout: int = 120):
        self.base_url = base_url.rstrip("/")
        self.model = model
        self.embed_model = embed_model
        self.timeout = timeout

    def _post(self, path: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        body = json.dumps(payload).encode("utf-8")
        request = urllib.request.Request(
            f"{self.base_url}{path}",
            data=body,
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        try:
            with urllib.request.urlopen(request, timeout=self.timeout) as response:
                return json.loads(response.read().decode("utf-8"))
        except urllib.error.URLError as exc:
            raise RuntimeError(
                f"Ollama request failed at {self.base_url}{path}. "
                "Make sure Ollama is running and the requested model is installed."
            ) from exc

    def chat(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
        max_tokens: int = 250,
        format: str | None = None,
    ) -> Dict[str, Any]:
        payload = {
            "model": self.model,
            "messages": messages,
            "stream": False,
            "options": {
                "temperature": temperature,
                "num_predict": max_tokens,
            },
        }
        if format is not None:
            payload["format"] = format

        result = self._post("/api/chat", payload)
        return {
            "content": result.get("message", {}).get("content", "").strip(),
            "usage": {
                "prompt_tokens": result.get("prompt_eval_count"),
                "completion_tokens": result.get("eval_count"),
                "total_tokens": (
                    (result.get("prompt_eval_count") or 0)
                    + (result.get("eval_count") or 0)
                ),
            },
        }

    def embed(self, inputs: str | List[str]) -> List[List[float]]:
        values = [inputs] if isinstance(inputs, str) else inputs
        result = self._post(
            "/api/embed",
            {"model": self.embed_model, "input": values},
        )
        embeddings = result.get("embeddings")
        if not embeddings:
            raise RuntimeError("Ollama returned no embeddings.")
        return embeddings
