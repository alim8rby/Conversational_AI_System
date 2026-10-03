"""Run a live retrieval evaluation against the local semantic memory."""

from __future__ import annotations

import argparse
import json

from config.settings import load_settings
from evaluation.run_retrieval_eval import precision_at_k, recall_at_k, reciprocal_rank
from memory.memory_manager import MemoryManager


def evaluate_retriever(manager: MemoryManager, session_id: str, query: str, relevant_ids: list[str], k: int = 3) -> dict:
    if k <= 0:
        raise ValueError("k must be greater than zero")
    results = manager.retrieve(session_id, query, k=k)
    retrieved_ids = [item["memory_id"] for item in results]
    relevant = set(relevant_ids)
    return {
        "query": query,
        "retrieved_memory_ids": retrieved_ids,
        "precision_at_k": precision_at_k(retrieved_ids, relevant, k),
        "recall_at_k": recall_at_k(retrieved_ids, relevant, k),
        "mrr": reciprocal_rank(retrieved_ids, relevant),
        "retrieval_count": len(results),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Evaluate local semantic retrieval.")
    parser.add_argument("--session-id", required=True)
    parser.add_argument("--query", required=True)
    parser.add_argument("--relevant-id", action="append", required=True, help="Repeat for multiple relevant IDs.")
    parser.add_argument("--k", type=int, default=3)
    args = parser.parse_args()

    settings = load_settings(require_runtime=True)
    manager = MemoryManager(embed_model=settings.embed_model, store_path=settings.memory_store_path)
    result = evaluate_retriever(manager, args.session_id, args.query, args.relevant_id, args.k)

    print(json.dumps({
        "evaluation_type": "local-runtime",
        "session_id": args.session_id,
        "embedding_model": settings.embed_model,
        "memory_store": settings.memory_store_path,
        "k": args.k,
        "result": result,
    }, indent=2))


if __name__ == "__main__":
    main()
