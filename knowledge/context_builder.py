"""Build controlled LLM context from retrieved domain knowledge."""

from __future__ import annotations

from typing import Dict, List


class KnowledgeContextBuilder:
    """Turn ranked retrieval results into bounded, traceable model context."""

    def build(
        self,
        results: List[Dict],
        max_chars: int = 4000,
    ) -> Dict:
        if max_chars <= 0:
            raise ValueError("max_chars must be greater than zero.")

        selected = []
        total_chars = 0

        for result in results:
            text = str(result.get("text", "")).strip()
            if not text:
                continue

            remaining = max_chars - total_chars
            if remaining <= 0:
                break

            excerpt = text[:remaining]
            selected.append(
                {
                    "id": result.get("id"),
                    "source": result.get("source"),
                    "rank": result.get("rank"),
                    "score": result.get("score"),
                    "text": excerpt,
                    "truncated": len(excerpt) < len(text),
                }
            )
            total_chars += len(excerpt)

            if len(excerpt) < len(text):
                break

        context_blocks = []
        for item in selected:
            context_blocks.append(
                "[Source {rank}] {source}\n{excerpt}".format(
                    rank=item["rank"],
                    source=item["source"],
                    excerpt=item["text"],
                )
            )

        return {
            "context": "\n\n".join(context_blocks),
            "sources": selected,
            "retrieved_count": len(results),
            "included_count": len(selected),
            "context_chars": total_chars,
        }
