import os
from together import Together
from memory.memory_manager import MemoryManager

class ConversationAgent:
    def __init__(self, model_name: str, embed_model: str, index_name: str):
        # LLM client
        self.client = Together(api_key=os.getenv("TOGETHER_API_KEY"))
        self.model = model_name
        # RAG memory
        self.memory = MemoryManager(
            embed_model=embed_model,
            index_name=index_name
        )

    def ask(self, user_message: str) -> str:
        # 1) Retrieve past keys
        keys = self.memory.retrieve(user_message, k=3)
        # 2) Build context string
        context = ""
        if keys:
            context = "Previous notes: " + "; ".join(keys) + "\n"
        # 3) Send combined prompt
        messages = [
            {"role": "user", "content": context + user_message}
        ]
        resp = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            max_tokens_to_sample=300,
            temperature=0.7,
        )
        answer = resp.choices[0].message.content
        # 4) Store this turn in memory
        self.memory.add(user_message, answer)
        return answer

if __name__ == "__main__":
    agent = ConversationAgent(
        model_name="meta-llama/Meta-Llama-3.1-8B-Instruct-Turbo",
        embed_model="togethercomputer/m2-bert-80M-8k-retrieval",
        index_name="wss-ai-memory"
    )
    # First ask (will upsert memory)
    print(">>", agent.ask("Patient: I feel scared in hospitals."))
    # Second ask (should retrieve and reference prior)
    print(">>", agent.ask("Patient: Why do I feel scared in hospitals?"))
