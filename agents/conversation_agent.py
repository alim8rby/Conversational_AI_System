import os
from together import Together
from memory.memory_manager import MemoryManager
from interview_manager import InterviewManager

class ConversationAgent:
    def __init__(self,
                 model_name: str,
                 embed_model: str,
                 index_name: str):
        # LLM & Memory
        self.client   = Together(api_key=os.getenv("TOGETHER_API_KEY"))
        self.model    = model_name
        self.mem      = MemoryManager(embed_model, index_name)

        # Structured interview
        self.interviewer = InterviewManager()
        self.awaiting = {}  # session_id -> last asked section

        # Final therapy prompt
        self.system_prompt = (
            "You are El Consulto, an empathic psychiatrist AI. "
            "Use details from this client’s psychiatric sheet to inform each reply. "
            "Keep responses concise and offer practical steps. "
            "If the user goes off-topic, gently refocus: "
            "\"We’re here in a therapy session—let’s focus on your feelings.\""
        )

    def ask(self,
            session_id: str,
            user_message: str) -> str:
        # Initialize session in interviewer
        self.interviewer.init_session(session_id)

        # --- STRUCTURED CONVERSATION PHASE ---
        if not self.interviewer.is_complete(session_id):
            last_sec = self.awaiting.get(session_id)
            # 1) If we just asked a section, record the user’s answer
            if last_sec:
                self.interviewer.record_response(session_id, user_message)

            # 2) Find next section
            next_sec = self.interviewer.next_section(session_id)
            question = self.interviewer.get_question(session_id)

            # 3) Build a conversational transition
            if last_sec is None:
                # first question
                prompt = (
                    "Hello! I’m El Consulto, your virtual psychiatrist. "
                    f"{question}"
                )
            else:
                # acknowledge and transition
                # get a human-friendly title from the section key
                friendly = next_sec.replace("_", " ")
                prompt = (
                    "Thank you for sharing. "
                    f"{question}"
                )

            # 4) Mark that we're now waiting on this section
            self.awaiting[session_id] = next_sec
            return prompt

        # --- FREE-FORM THERAPY PHASE ---
        # 1) Build patient sheet context
        sheet = self.interviewer.get_sheet(session_id)
        sheet_text = "\n".join(f"{k.replace('_',' ').title()}: {v}"
                               for k, v in sheet.items())

        # 2) Retrieve up to 3 relevant past notes
        past_notes = self.mem.retrieve(session_id, user_message, k=3)
        mem_text = "\n".join(past_notes) + "\n\n" if past_notes else ""

        # 3) Build messages for the LLM
        messages = [
            {"role": "system",  "content": self.system_prompt},
            {"role": "system",  "content": "Patient Sheet:\n" + sheet_text},
            {"role": "user",    "content": mem_text + user_message}
        ]

        # 4) Query the LLM
        resp = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            max_tokens_to_sample=250,
            temperature=0.7,
        )
        answer = resp.choices[0].message.content.strip()

        # 5) Save this turn in memory
        self.mem.add(session_id, user_message, answer)
        return answer

if __name__ == "__main__":
    # Quick manual test
    agent = ConversationAgent(
        model_name="meta-llama/Meta-Llama-3.1-8B-Instruct-Turbo",
        embed_model="togethercomputer/m2-bert-80M-8k-retrieval",
        index_name="wss-ai-memory"
    )
    sid = "demo-session"
    # Simulate a short interview
    while not agent.interviewer.is_complete(sid):
        q = agent.ask(sid, "")
        print("AI asks:", q)
        a = input("You: ")
        # Loop back into ask to record and get the next
    print("Structured portion complete. Now therapy mode kicks in.")
