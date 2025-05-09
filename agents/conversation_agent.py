import os
from together import Together
from memory.memory_manager import MemoryManager

class ConversationAgent:
    def __init__(self, model_name: str, embed_model: str, index_name: str):
        self.client   = Together(api_key=os.getenv("TOGETHER_API_KEY"))
        self.model    = model_name
        self.mem      = MemoryManager(embed_model, index_name)
        # In-memory history so we don’t repeat the first reply
        self.histories = {}

        self.system_prompt = (
            "You are El Consulto, an empathic psychiatrist AI. "
            "Use your memory of this client’s journey to inform each reply, "
            "keeping responses concise (1–3 sentences) with an optional practical step. "
            "If the patient asks anything off-topic, gently refocus: "
            "\"We’re here in a therapy session—let’s focus on your feelings.\""
        )

    def ask(self, session_id: str, user_message: str) -> str:
        # initialize history list
        if session_id not in self.histories:
            self.histories[session_id] = []

        # retrieve relevant past notes
        past_notes = self.mem.retrieve(session_id, user_message, k=3)
        memory_block = "\n".join(past_notes) + "\n\n" if past_notes else ""

        # build message list with system + full history
        messages = [{"role":"system","content":self.system_prompt}]
        for m in self.histories[session_id]:
            messages.append(m)
        # add latest user turn
        messages.append({"role":"user","content":memory_block + user_message})

        # call the model
        resp = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            max_tokens_to_sample=250,
            temperature=0.7,
        )
        answer = resp.choices[0].message.content.strip()

        # update history: user + assistant
        self.histories[session_id].append({"role":"user","content":user_message})
        self.histories[session_id].append({"role":"assistant","content":answer})

        # store in RAG memory too
        self.mem.add(session_id, user_message, answer)
        return answer

if __name__ == "__main__":
    agent = ConversationAgent(
        model_name="meta-llama/Meta-Llama-3.1-8B-Instruct-Turbo",
        embed_model="togethercomputer/m2-bert-80M-8k-retrieval",
        index_name="wss-ai-memory"
    )
    print(agent.ask("test-session","I have an existential crisis"))
