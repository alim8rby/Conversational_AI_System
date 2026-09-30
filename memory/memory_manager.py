import json
import math
import os
from pathlib import Path
from typing import Dict, List

from providers.ollama_client import OllamaClient


class MemoryManager:
    """Session-scoped semantic memory backed by a local JSON vector store."""

    def __init__(self, embed_model: str, index_name: str):
        self.embed_model = embed_model
        self.store_path = Path(
            os.getenv("MEMORY_STORE_PATH", "data/memory.json")
        )
        self.ollama = OllamaClient(
            base_url=os.getenv("OLLAMA_BASE_URL", "http://localhost:11434"),
            model=os.getenv(
                "LLM_MODEL", "llama3.2:3b"
            ),
            embed_model=embed_model,
        )
        self.store_path.parent.mkdir(parents=True, exist_ok=True)

    def _load(self) -> List[Dict]:
        if not self.store_path.exists():
            return []
        return json.loads(self.store_path.read_text(encoding="utf-8"))

    def _save(self, records: List[Dict]) -> None:
        self.store_path.write_text(
            json.dumps(records, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )

    def _embed(self, text: str) -> List[float]:
        return self.ollama.embed(text)[0]

    @staticmethod
    def _cosine_similarity(left: List[float], right: List[float]) -> float:
        dot = sum(a * b for a, b in zip(left, right))
        left_mag = math.sqrt(sum(value * value for value in left))
        right_mag = math.sqrt(sum(value * value for value in right))
        if not left_mag or not right_mag:
            return 0.0
        return dot / (left_mag * right_mag)

    def add(self, session_id: str, key: str, text: str) -> None:
        vector = self._embed(text)
        records = self._load()
        records = [record for record in records if record["id"] != key]
        records.append(
            {
                "id": key,
                "session": session_id,
                "text": text,
                "vector": vector,
            }
        )
        self._save(records)

    def retrieve(self, session_id: str, query: str, k: int = 3) -> List[Dict]:
        if k <= 0:
            return []

        query_vector = self._embed(query)
        matches = []
        for record in self._load():
            if record.get("session") != session_id:
                continue
            score = self._cosine_similarity(query_vector, record["vector"])
            matches.append(
                {
                    "text": record["text"],
                    "score": score,
                    "memory_id": record["id"],
                }
            )

        matches.sort(key=lambda item: item["score"], reverse=True)
        return [
            {**match, "rank": rank}
            for rank, match in enumerate(matches[:k], start=1)
        ]
