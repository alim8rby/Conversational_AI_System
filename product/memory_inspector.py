"""Read-only memory inspection projection."""

from __future__ import annotations

from memory.memory_manager import MemoryManager


def inspect_memory(manager: MemoryManager, session_id: str, query: str, k: int = 3) -> dict:
    if not session_id or len(session_id) > 128:
        raise ValueError("Invalid session ID.")
    if not query or len(query) > 4000:
        raise ValueError("Invalid query.")
    if k < 1 or k > 20:
        raise ValueError("k must be between 1 and 20.")

    results = manager.retrieve(session_id, query, k=k)
    memories = [
        {
            "memory_id": item["memory_id"],
            "rank": item["rank"],
            "score": item["score"],
            "text": item["text"],
        }
        for item in results
    ]

    return {
        "schema_version": "memory-inspector-v1",
        "session_id": session_id,
        "query": query,
        "k": k,
        "retrieved_count": len(memories),
        "memories": memories,
    }
