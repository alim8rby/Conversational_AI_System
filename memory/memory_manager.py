# memory/memory_manager.py
import os
import pinecone
from together import Together

class MemoryManager:
    def __init__(self, embed_model: str, index_name: str):
        # Init Together for embeddings
        self.client = Together(api_key=os.getenv("TOGETHER_API_KEY"))
        # Init Pinecone
        pinecone.init(
            api_key=os.getenv("PINECONE_API_KEY"),
            environment=os.getenv("PINECONE_ENV")
        )
        self.index = pinecone.Index(index_name)
        self.embed_model = embed_model

    def add(self, key: str, text: str):
        # 1) Get embedding from Together
        resp = self.client.embeddings.create(
            model=self.embed_model,
            input=text
        )
        vector = resp.data[0].embedding
        # 2) Upsert into Pinecone
        self.index.upsert([(key, vector)])

    def retrieve(self, query: str, k: int = 3):
        # 1) Embed the query
        resp = self.client.embeddings.create(
            model=self.embed_model,
            input=query
        )
        qvec = resp.data[0].embedding
        # 2) Query Pinecone
        results = self.index.query(qvec, top_k=k, include_metadata=True)
        # 3) Return the texts or IDs
        return [match['id'] for match in results['matches']]

if __name__ == "__main__":
    mm = MemoryManager(
        embed_model="togethercomputer/m2-bert-80M-8k-retrieval",
        index_name="wss-ai-memory"
    )
    mm.add("session1", "Patient described fear of small rooms.")
    print("Retrieved keys:", mm.retrieve("small rooms fear"))
