from langchain.vectorstores import Pinecone # type: ignore
from langchain.embeddings.openai import OpenAIEmbeddings # type: ignore

class MemoryManager:
    def __init__(self, index_name: str, api_key: str):
        # initialize embeddings + Pinecone store
        self.embeddings = OpenAIEmbeddings(openai_api_key=api_key)
        self.store = Pinecone.from_existing_index(index_name, self.embeddings)

    def add(self, key: str, text: str):
        # store a new memory
        self.store.add_texts([text], metadatas=[{"key": key}])

    def retrieve(self, query: str, k: int = 3):
        # fetch similar memories
        return self.store.similarity_search(query, k)
