# memory/memory_manager.py
import os
from pinecone import Pinecone
from together import Together

class MemoryManager:
    def __init__(self, embed_model: str, index_name: str):
        # Initialize Together for embeddings
        self.client = Together(api_key=os.getenv("TOGETHER_API_KEY"))

        # Initialize Pinecone client (reads your env var for key)
        self.pinecone = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))
        # Connect to your existing index
        self.index = self.pinecone.Index(index_name)

        self.embed_model = embed_model

    def add(self, key: str, text: str):
        # 1) Get embedding from Together
        resp = self.client.embeddings.create(
            model=self.embed_model,
            input=text
        )
        vector = resp.data[0].embedding
        # 2) Upsert into your Pinecone index
        self.index.upsert([(key, vector)])

    def retrieve(self, query: str, k: int = 3):
        # 1) Embed the query
        resp = self.client.embeddings.create(
            model=self.embed_model,
            input=query
        )
        qvec = resp.data[0].embedding
        # 2) Query Pinecone
        results = self.index.query(
            vector=qvec,
            top_k=k,
            include_values=False,
            include_metadata=False
        )
        # 3) Return the stored keys
        return [match.id for match in results.matches]

if __name__ == "__main__":
    mm = MemoryManager(
        embed_model="togethercomputer/m2-bert-80M-8k-retrieval",
        index_name="wss-ai-memory"
    )
    mm.add("session1", "Patient described fear of small rooms.")
    print("Retrieved keys:", mm.retrieve("small rooms fear"))
