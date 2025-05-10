# -*- coding: utf-8 -*-
import os
import re
from together import Together, error as ta_errors
from memory.memory_manager import MemoryManager
from interview_manager import InterviewManager

def detect_language(text: str) -> str:
    """
    Return 'ar' for Arabic script, 'franco' for digit-heavy Franco-Arab,
    else 'en'.
    """
    if re.search(r'[\u0600-\u06FF]', text):
        return 'ar'
    if re.search(r'\d', text):
        return 'franco'
    return 'en'

class ConversationAgent:
    def __init__(self,
                 model_name: str,
                 embed_model: str,
                 index_name: str):
        # LLM & RAG memory
        self.client   = Together(api_key=os.getenv("TOGETHER_API_KEY"))
        self.model    = model_name
        self.mem      = MemoryManager(embed_model, index_name)

        # Structured interview
        self.interviewer = InterviewManager()
        self.awaiting    = {}  # session_id -> last asked section

        # In-memory history to prevent repeats
        self.histories   = {}

    def ask(self, session_id: str, user_message: str) -> str:
        # --- 1) Language detection & prompts setup ---
        lang = detect_language(user_message)
        if lang == 'ar':
            sys_base = (
                "أنت El Consulto، الطبيب النفسي الافتراضي باللهجة المصرية العامية. "
                "استخدم ما تعرفه عن المريض—تجاربه، مخاوفه وطموحاته—في كل رد، "
                "بدون ذكر عدد الجلسات أو القوائم. "
                "إذا واجهت خطأ تقنيًّا، اعتذر واطلب إعادة المحاولة."
            )
            greet_first = "أهلاً! أنا El Consulto، طبيبك الافتراضي."
            thank_you   = "شكرًا لمشاركتك."
            error_reply = "عذرًا، حصلت مشكلة فنية. هل يمكنك المحاولة مرة أخرى؟"
        elif lang == 'franco':
            sys_base = (
                "Enta El Consulto, el doctor ennafsy el AI el byetkallem Franco-Arab. "
                "Weave fi ay tafaseel 3arafna 3anha men el mareed—"
                "experiences, fears, ambitions—men gheir ma tsmaa el sessions. "
                "Law feh moshkela, et2ezir we 7awel tani."
            )
            greet_first = "Hey! Ana El Consulto, el doctor ennafsy beta3ak."
            thank_you   = "Shokran 3ala el mosharaka."
            error_reply = "M3lesh, fe moshkela tehnia. Momken t7awel tani?"
        else:
            sys_base = (
                "You are El Consulto, an empathic psychiatrist AI. "
                "In each reply, combine warmth and professional insight with the specific details "
                "you know about this client’s journey—past challenges, fears, and hopes—"
                "without ever labeling sessions. "
                "If anything goes wrong, apologize briefly and ask them to try again."
            )
            greet_first = "Hello! I’m El Consulto, your virtual psychiatrist."
            thank_you   = "Thank you for sharing."
            error_reply = "Sorry, I ran into an issue. Could you please try again?"

        # --- 2) Ensure history & interviewer state exist ---
        if session_id not in self.histories:
            self.histories[session_id] = []
        self.interviewer.init_session(session_id)

        # --- 3) Structured interview phase ---
        if not self.interviewer.is_complete(session_id):
            last_sec = self.awaiting.get(session_id)
            # a) record prior answer
            if last_sec:
                self.interviewer.record_response(session_id, user_message)

            # b) get next question
            next_sec = self.interviewer.next_section(session_id)
            question = self.interviewer.get_question(session_id)

            # c) build conversational prompt
            if last_sec is None:
                # very first turn
                prompt = f"{greet_first} {question}"
            else:
                prompt = f"{thank_you} {question}"

            # d) mark as awaiting this section
            self.awaiting[session_id] = next_sec
            return prompt

        # --- 4) Free-form therapy phase ---
        # a) assemble the patient sheet
        sheet = self.interviewer.get_sheet(session_id)
        sheet_text = "\n".join(f"{k.replace('_',' ').title()}: {v}"
                               for k, v in sheet.items())

        # b) retrieve relevant memory
        past_notes = self.mem.retrieve(session_id, user_message, k=3)
        memory_block = ("\n".join(past_notes) + "\n\n") if past_notes else ""

        # c) build the message sequence
        messages = [
            {"role": "system",   "content": sys_base},
            {"role": "system",   "content": "Patient Sheet:\n" + sheet_text},
        ]
        messages.extend(self.histories[session_id])
        messages.append({"role": "user", "content": memory_block + user_message})

        # d) call the LLM with error handling
        try:
            resp = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                max_tokens_to_sample=250,
                temperature=0.7,
            )
            answer = resp.choices[0].message.content.strip()
        except (ta_errors.AuthenticationError,
                ta_errors.InvalidRequestError,
                Exception):
            return error_reply

        # e) record history & memory
        self.histories[session_id].append({"role":"user",    "content":user_message})
        self.histories[session_id].append({"role":"assistant","content":answer})
        self.mem.add(session_id, user_message, answer)

        return answer

if __name__ == "__main__":
    agent = ConversationAgent(
        model_name="meta-llama/Meta-Llama-3.1-8B-Instruct-Turbo",
        embed_model="togethercomputer/m2-bert-80M-8k-retrieval",
        index_name="wss-ai-memory"
    )
    # Example test
    print(agent.ask("test-session", "أنا حسيت بتوتر من قلبي"))
