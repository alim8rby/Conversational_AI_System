import os
from together import Together
from memory.memory_manager import MemoryManager

class ConversationAgent:
    def __init__(self, model_name: str, embed_model: str, index_name: str):
        # Initialize the LLM client
        self.client = Together(api_key=os.getenv("TOGETHER_API_KEY"))
        self.model  = model_name
        # Initialize session-scoped memory
        self.mem    = MemoryManager(embed_model, index_name)

        # A single, rich system prompt:
        self.system_prompt = (
            "You are El Consulto, an empathic and professional psychiatrist AI. "
            "In each reply, combine warmth and mental-health expertise with the specific details "
            "you know about this client’s journey—past challenges, fears, and goals—"
            "without ever labeling sessions or using technical headings. "
            "Keep your responses concise (1–3 sentences) and, if helpful, offer a simple practical step. "
            "If the user’s message is off-topic or asks for non-therapeutic content (code samples, API advice, "
            "business strategy, etc.), please gently remind them: "
            "\"We’re here in a therapy session—let’s refocus on how you’re feeling right now.\""
        )

    def ask(self, session_id: str, user_message: str) -> str:
        # 1) Retrieve up to 3 relevant past notes for this session
        past_notes = self.mem.retrieve(session_id, user_message, k=3)
        # Join them into a short memory block
        memory_block = ""
        if past_notes:
            memory_block = "Your earlier notes: " + "; ".join(past_notes) + "\n\n"

        # 2) Build the messages with the system prompt + user
        messages = [
            {"role": "system", "content": self.system_prompt},
            {"role": "user",   "content": memory_block + user_message}
        ]

        # 3) Query the model
        resp = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            max_tokens_to_sample=250,
            temperature=0.7,
        )
        answer = resp.choices[0].message.content.strip()

        # 4) Save this exchange into memory for future context
        self.mem.add(session_id, user_message, answer)

        return answer

if __name__ == "__main__":
    # Quick manual test
    agent = ConversationAgent(
        model_name="meta-llama/Meta-Llama-3.1-8B-Instruct-Turbo",
        embed_model="togethercomputer/m2-bert-80M-8k-retrieval",
        index_name="wss-ai-memory"
    )
    print(agent.ask("test-session", "I have an existential crisis"))
