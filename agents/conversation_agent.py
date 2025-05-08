import os
from together import Together
from memory.memory_manager import MemoryManager

class ConversationAgent:
    def __init__(self, model_name, embed_model, index_name):
        self.client = Together(api_key=os.getenv("TOGETHER_API_KEY"))
        self.model = model_name
        self.memory = MemoryManager(embed_model, index_name)
        self.system_prompt = (
            "You are El Consulto’s empathetic psychiatrist AI. "
            "Reply as the therapist only—no follow-up questions to yourself."
            "When given a patient’s message (and any prior context), " 
            "respond only with your next therapeutic reply—never ask the patient to respond. " 
            "Keep it warm, compassionate, and frank."
        )

    def ask(self, session_id: str, user_message: str) -> str:
        # 1) Retrieve session-scoped memory
        keys = self.memory.retrieve(session_id, user_message, k=3)
        context = ""
        if keys:
            context = "Context from this session: " + "; ".join(keys) + "\n\n"

        # 2) Build the chat
        messages = [
            {"role":"system", "content": self.system_prompt},
            {"role":"user",   "content": context + user_message}
        ]
        resp = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            max_tokens_to_sample=300,
            temperature=0.7,
        )
        answer = resp.choices[0].message.content

        # 3) Save this turn under this session
        self.memory.add(session_id, user_message, answer)
        return answer
