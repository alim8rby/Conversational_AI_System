"""Provider-backed retrieval evaluation.

Runs the retrieval evaluator against the existing MemoryManager.
Requires Together AI and Pinecone credentials plus a populated session.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from agents.conversation_agent import EMBED_MODEL, INDEX_NAME
from memory.memory_manager import MemoryManager
from run_retrieval_eval import precision_at_k, recall_at_k, reciprocal_rank


def evaluate_retriever(manager, session_id: str, query: str, relevant_ids: list[str], k: int = 3) -> dict:
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
    parser = argparse.ArgumentParser()
    parser.add_argument("--session-id", required=True)
    parser.add_argument("--query", required=True)
    parser.add_argument("--relevant-id", action="append", required=True)
    parser.add_argument("--k", type=int, default=3)
    args = parser.parse_args()

    if not os.getenv("TOGETHER_API_KEY") or not os.getenv("PINECONE_API_KEY"):
        raise RuntimeError("TOGETHER_API_KEY and PINECONE_API_KEY are required for live retrieval evaluation.")

    manager = MemoryManager(embed_model=EMBED_MODEL, index_name=INDEX_NAME)
    result = evaluate_retriever(
        manager,
        args.session_id,
        args.query,
        args.relevant_id,
        args.k,
    )
    print(json.dumps({
        "evaluation_type": "provider-backed",
        "session_id": args.session_id,
        "embedding_model": EMBED_MODEL,
        "index_name": INDEX_NAME,
        "k": args.k,
        "result": result,
    }, indent=2))


if __name__ == "__main__":
    main()
