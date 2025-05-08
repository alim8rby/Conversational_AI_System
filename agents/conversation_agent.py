import os
from together import Together
from memory.memory_manager import MemoryManager

class ConversationAgent:
    def __init__(self, model_name: str, embed_model: str, index_name: str):
        self.client = Together(api_key=os.getenv("TOGETHER_API_KEY"))
        self.model = model_name
        self.memory = MemoryManager(embed_model=embed_model, index_name=index_name)

        # Our fixed system instruction
        self.system_prompt = (
            "You are WsS AI, an empathic psychiatrist. "
            "When given a patient’s message (and any prior context), "
            "respond only with your next therapeutic reply—never ask the patient to respond. "
            "Keep it warm, compassionate, and frank."
        )

    def ask(self, user_message: str) -> str:
        # 1) Retrieve prior memory keys
        keys = self.memory.retrieve(user_message, k=3)
        # 2) Build a single “context” string from those memories
        context = ""
        if keys:
            context = "Previous notes: " + "; ".join(keys) + "\n\n"

        # 3) Build the chat message list
        messages = [
            {"role": "system",  "content": self.system_prompt},
            {"role": "user",    "content": context + user_message}
        ]

        # 4) Call the model
        resp = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            max_tokens_to_sample=300,
            temperature=0.7,
        )
        answer = resp.choices[0].message.content

        # 5) Save this turn into memory
        self.memory.add(user_message, answer)
        return answer

if __name__ == "__main__":
    agent = ConversationAgent(
        model_name="meta-llama/Meta-Llama-3.1-8B-Instruct-Turbo",
        embed_model="togethercomputer/m2-bert-80M-8k-retrieval",
        index_name="wss-ai-memory"
    )
    print(">>", agent.ask("Patient: I feel afraid of hospitals."))
