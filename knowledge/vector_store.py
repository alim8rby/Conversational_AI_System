"""Local semantic vector store for domain knowledge."""

from __future__ import annotations

import json
import math
from pathlib import Path
from typing import Dict, List


class LocalVectorStore:
    """Persist embedded knowledge chunks in a local JSON file."""

    def __init__(self, path: str):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)

    def _load(self) -> List[Dict]:
        if not self.path.exists():
            return []
        return json.loads(self.path.read_text(encoding="utf-8"))

    def _save(self, records: List[Dict]) -> None:
        self.path.write_text(
            json.dumps(records, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )

    def upsert(self, records: List[Dict]) -> None:
        existing = {record["id"]: record for record in self._load()}
        existing.update({record["id"]: record for record in records})
        self._save(list(existing.values()))

    @staticmethod
    def cosine_similarity(left: List[float], right: List[float]) -> float:
        dot = sum(a * b for a, b in zip(left, right))
        left_mag = math.sqrt(sum(value * value for value in left))
        right_mag = math.sqrt(sum(value * value for value in right))

        if not left_mag or not right_mag:
            return 0.0

        return dot / (left_mag * right_mag)

    def search(
        self,
        query_vector: List[float],
        k: int = 3,
        source_prefix: str | None = None,
    ) -> List[Dict]:
        if k <= 0:
            return []

        matches = []
        for record in self._load():
            if source_prefix and not record["source"].startswith(source_prefix):
                continue

            score = self.cosine_similarity(query_vector, record["vector"])
            matches.append(
                {
                    "id": record["id"],
                    "source": record["source"],
                    "text": record["text"],
                    "score": score,
                }
            )

        matches.sort(key=lambda item: item["score"], reverse=True)

        return [
            {**match, "rank": rank}
            for rank, match in enumerate(matches[:k], start=1)
        ]
