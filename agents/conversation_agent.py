import os
from together import Together
from memory.memory_manager import MemoryManager
from interview_manager import InterviewManager

class ConversationAgent:
    def __init__(self,
                 model_name: str,
                 embed_model: str,
                 index_name: str):
        # LLM and memory clients
        self.client   = Together(api_key=os.getenv("TOGETHER_API_KEY"))
        self.model    = model_name
        self.mem      = MemoryManager(embed_model, index_name)

        # Structured interview manager
        self.interviewer = InterviewManager()
        # Track which section was just asked, per session
        self.awaiting = {}

        # Final therapy prompt once structured phase is done
        self.system_prompt = (
            "You are El Consulto, an empathic psychiatrist AI. "
            "Use details from this client’s psychiatric sheet to inform each reply. "
            "Keep responses concise and offer practical steps. "
            "If the user goes off-topic, gently refocus to their emotions."
        )

    def ask(self,
            session_id: str,
            user_message: str) -> str:

        # --- STRUCTURED INTERVIEW FLOW ---
        # 1) If we’re still filling the sheet:
        if not self.interviewer.is_complete(session_id):
            # a) If we have a section we asked previously, record the answer
            last_sec = self.awaiting.get(session_id)
            if last_sec:
                self.interviewer.sessions[session_id][last_sec] = user_message

            # b) Get next question
            next_sec = self.interviewer.next_section(session_id)
            question = self.interviewer.get_question(session_id)
            # c) Mark as awaiting this section
            self.awaiting[session_id] = next_sec
            return question

        # --- FREE-FORM THERAPY ---
        # 2) Now that structured sheet is complete, load it:
        sheet = self.interviewer.get_sheet(session_id)
        sheet_text = "\n".join(f"{k.replace('_',' ').title()}: {v}"
                               for k,v in sheet.items())

        # 3) Retrieve up to 3 relevant past notes
        past_notes = self.mem.retrieve(session_id, user_message, k=3)
        mem_text = "\n".join(past_notes) + "\n\n" if past_notes else ""

        # 4) Build chat messages
        messages = [
            {"role":"system", "content": self.system_prompt},
            {"role":"system", "content": "Patient Sheet:\n" + sheet_text},
            {"role":"user",   "content": mem_text + user_message}
        ]

        # 5) Query the LLM
        resp = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            max_tokens_to_sample=250,
            temperature=0.7,
        )
        answer = resp.choices[0].message.content.strip()

        # 6) Save in Pinecone for future retrieval
        self.mem.add(session_id, user_message, answer)

        return answer

if __name__ == "__main__":
    # Quick manual structured-interview test
    agent = ConversationAgent(
        model_name="meta-llama/Meta-Llama-3.1-8B-Instruct-Turbo",
        embed_model="togethercomputer/m2-bert-80M-8k-retrieval",
        index_name="wss-ai-memory"
    )
    sid = "demo-session"
    # simulate QA rounds
    while True:
        q = agent.ask(sid, "")
        print("AI asks>", q)
        a = input("Your answer> ")
        r = agent.ask(sid, a)
        # once sheet complete, break
        from interview_manager import InterviewManager
        if agent.interviewer.is_complete(sid):
            print("Structured sheet complete.")
            break
