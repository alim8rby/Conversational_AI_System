# memory/memory_manager.py
import os
from together import Together

class MemoryManager:
    def __init__(self, embed_model: str):
        self.client = Together(api_key=os.getenv("TOGETHER_API_KEY"))
        self.embed_model = embed_model

    def add(self, key: str, text: str):
        # Generate an embedding for `text`
        resp = self.client.embeddings.create(
            model=self.embed_model,    # e.g. "togethercomputer/m2-bert-80M-8k-retrieval"
            input=text
        )
        vector = resp.data[0].embedding
        # TODO: store `vector` in your vector DB under `key`

    def retrieve(self, query: str, k: int = 3):
        # Create query embedding
        resp = self.client.embeddings.create(
            model=self.embed_model,
            input=query
        )
        qvec = resp.data[0].embedding
        # TODO: use your vector DB to find the top-k most similar entries to qvec
        return []  # return retrieved items

if __name__ == "__main__":
    mm = MemoryManager("togethercomputer/m2-bert-80M-8k-retrieval")
    mm.add("session1", "Patient’s childhood fear of small rooms.")
    print("Retrieve stub:", mm.retrieve("small rooms fear"))
