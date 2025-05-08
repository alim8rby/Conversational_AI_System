import os
from pinecone import Pinecone
from together import Together

class MemoryManager:
    def __init__(self, embed_model: str, index_name: str):
        self.client = Together(api_key=os.getenv("TOGETHER_API_KEY"))
        self.pinecone = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))
        self.index = self.pinecone.Index(index_name)
        self.embed_model = embed_model

    def add(self, session_id: str, key: str, text: str):
        # 1) Embed the text
        resp = self.client.embeddings.create(
            model=self.embed_model, input=text
        )
        vector = resp.data[0].embedding
        # 2) Upsert with session metadata
        self.index.upsert(
            [(key, vector, {"session": session_id})]
        )

    def retrieve(self, session_id: str, query: str, k: int = 3):
        # 1) Embed the query
        resp = self.client.embeddings.create(
            model=self.embed_model, input=query
        )
        qvec = resp.data[0].embedding
        # 2) Query only this session’s items
        results = self.index.query(
            vector=qvec,
            top_k=k,
            include_values=False,
            include_metadata=True,
            filter={"session": session_id}
        )
        # 3) Return the keys
        return [match.id for match in results.matches]
