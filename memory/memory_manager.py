import os
from typing import List

from pinecone import Pinecone
from together import Together


class MemoryManager:
    """Session-scoped semantic memory backed by Pinecone."""

    def __init__(self, embed_model: str, index_name: str):
        together_api_key = os.getenv("TOGETHER_API_KEY")
        pinecone_api_key = os.getenv("PINECONE_API_KEY")
        if not together_api_key:
            raise RuntimeError("TOGETHER_API_KEY is not set")
        if not pinecone_api_key:
            raise RuntimeError("PINECONE_API_KEY is not set")
        self.client = Together(api_key=together_api_key)
        self.pinecone = Pinecone(api_key=pinecone_api_key)
        self.index = self.pinecone.Index(index_name)
        self.embed_model = embed_model

    def _embed(self, text: str) -> List[float]:
        response = self.client.embeddings.create(model=self.embed_model, input=text)
        return response.data[0].embedding

    def add(self, session_id: str, key: str, text: str) -> None:
        vector = self._embed(text)
        self.index.upsert(vectors=[{
            "id": key,
            "values": vector,
            "metadata": {"session": session_id, "text": text},
        }])

    def retrieve(self, session_id: str, query: str, k: int = 3) -> List[str]:
        qvec = self._embed(query)
        results = self.index.query(
            vector=qvec,
            top_k=k,
            include_values=False,
            include_metadata=True,
            filter={"session": {"$eq": session_id}},
        )
        return [
            match.metadata["text"]
            for match in results.matches
            if match.metadata and match.metadata.get("text")
        ]
