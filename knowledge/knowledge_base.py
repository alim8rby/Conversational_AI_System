"""Build and query a domain knowledge base using Ollama embeddings."""

from __future__ import annotations

import os
from typing import Dict, List

from knowledge.document_loader import DocumentLoader
from knowledge.vector_store import LocalVectorStore
from providers.ollama_client import OllamaClient


class KnowledgeBase:
    """Coordinate document loading, embedding, indexing, and retrieval."""

    def __init__(
        self,
        store_path: str = "data/knowledge.json",
        embed_model: str | None = None,
    ):
        self.embed_model = embed_model or os.getenv(
            "EMBED_MODEL",
            "nomic-embed-text",
        )
        self.client = OllamaClient(
            base_url=os.getenv("OLLAMA_BASE_URL", "http://localhost:11434"),
            model=os.getenv("LLM_MODEL", "llama3.2:3b"),
            embed_model=self.embed_model,
        )
        self.loader = DocumentLoader()
        self.store = LocalVectorStore(store_path)

    def index_directory(self, path: str) -> int:
        chunks = self.loader.load_and_chunk(path)
        if not chunks:
            return 0

        embeddings = self.client.embed([chunk["text"] for chunk in chunks])

        records = []
        for chunk, vector in zip(chunks, embeddings):
            records.append(
                {
                    **chunk,
                    "vector": vector,
                    "embedding_model": self.embed_model,
                }
            )

        self.store.upsert(records)
        return len(records)

    def retrieve(self, query: str, k: int = 3) -> List[Dict]:
        query_vector = self.client.embed(query)[0]
        return self.store.search(query_vector, k=k)
