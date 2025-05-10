# -*- coding: utf-8 -*-
import os
import re
from together import Together, error as ta_errors
from memory.memory_manager import MemoryManager
from interview_manager import InterviewManager, SECTION_QUESTIONS

def detect_language(text: str) -> str:
    if re.search(r'[\u0600-\u06FF]', text):
        return 'ar'
    if re.search(r'\d', text):
        return 'franco'
    return 'en'

def is_valid_answer(text: str) -> bool:
    """Return False for very short, single-letter, or repeated laughter answers."""
    t = text.strip().lower()
    # catch pure laughter or single letters
    if re.fullmatch(r'(ha)+h?', t) or re.fullmatch(r'(heh)+', t) or len(t) <= 2:
        return False
    # require at least 10 chars to count as an “answer”
    if len(t) < 10:
        return False
    return True

class ConversationAgent:
    def __init__(self,
                 model_name: str,
                 embed_model: str,
                 index_name: str):
        # LLM & memory
        self.client   = Together(api_key=os.getenv("TOGETHER_API_KEY"))
        self.model    = model_name
        self.mem      = MemoryManager(embed_model, index_name)

        # Structured interview
        self.interviewer = InterviewManager()
        self.awaiting    = {}     # session_id → last asked section
        self.histories   = {}     # session_id → list of past messages

    def _clarify(self, session_id: str, last_sec: str, user_msg: str, lang: str) -> str:
        """Use the LLM to generate a clarifying, empathic follow-up to the last question."""
        last_q = SECTION_QUESTIONS[last_sec]
        # Build a system prompt that instructs a clarifier
        if lang == 'ar':
            sys = (
                "أنت طبيب نفسي افتراضي. عندما تكون إجابة المريض غير واضحة أو قصيرة، "
                "ابدأ بالتعبير عن التعاطف ثم اطلب توضيحًا يتعلق بالسؤال السابق."
            )
            default = "عذرًا، لم أفهم تمامًا. هل يمكنك توضيح أكثر؟"
        elif lang == 'franco':
            sys = (
                "You are a virtual psychiatrist. If the user’s reply is unclear or too brief, "
                "respond empathetically then ask a focused follow-up about the previous question."
            )
            default = "Sorry, I didn’t catch that—could you explain a bit more?"
        else:
            sys = (
                "You are a virtual psychiatrist. When a client’s reply is unclear or very brief, "
                "first empathize and then ask a clarifying follow-up based on their last answer."
            )
            default = "I’m sorry, I didn’t quite catch that. Could you tell me more?"

        messages = [
            {"role": "system",  "content": sys},
            {"role": "user",    "content": f"Question: {last_q}\nAnswer: {user_msg}"}
        ]

        try:
            resp = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                max_tokens_to_sample=150,
                temperature=0.7,
            )
            return resp.choices[0].message.content.strip()
        except Exception:
            return default

    def ask(self, session_id: str, user_message: str) -> str:
        lang = detect_language(user_message)

        # --- 1) Check for non-answers & clarify ---
        if not is_valid_answer(user_message):
            # If we have a last section, clarify that; else a generic empathic prompt
            last_sec = self.awaiting.get(session_id)
            if last_sec:
                return self._clarify(session_id, last_sec, user_message, lang)
            # No last section yet—just a warm opener
            if lang == 'ar':
                return "أسمع صوتك لكنه قصير، هل يمكنك مشاركتي المزيد عن شعورك الآن؟"
            elif lang == 'franco':
                return "I hear you, but it’s short—could you share more about how you feel right now?"
            else:
                return "I’m listening, but I’d like to hear more—how are you feeling in your own words?"

        # --- 2) Ensure session data exists ---
        if session_id not in self.histories:
            self.histories[session_id] = []
        self.interviewer.init_session(session_id)

        # --- 3) Structured interview phase ---
        if not self.interviewer.is_complete(session_id):
            last_sec = self.awaiting.get(session_id)

            # If we just got a valid answer, record it
            if last_sec:
                self.interviewer.record_response(session_id, user_message)

            # Move on to next section
            next_sec  = self.interviewer.next_section(session_id)
            question  = self.interviewer.get_question(session_id)

            # Build the conversational prompt
            if last_sec is None:
                prompt = f"Hello! I’m El Consulto, your virtual psychiatrist. {question}"
            else:
                prompt = f"Thank you for sharing. {question}"

            # Mark we’re awaiting this section’s answer
            self.awaiting[session_id] = next_sec
            return prompt

        # --- 4) Free-form therapy phase ---
        # Build patient sheet context
        sheet = self.interviewer.get_sheet(session_id)
        sheet_text = "\n".join(f"{k.replace('_',' ').title()}: {v}"
                               for k, v in sheet.items())

        # Retrieve up to 3 relevant memories
        past_notes = self.mem.retrieve(session_id, user_message, k=3)
        memory_block = "\n".join(past_notes) + "\n\n" if past_notes else ""

        # System prompt for therapy
        sys_prompt = (
            "You are El Consulto, an empathic psychiatrist AI. Use the patient sheet and "
            "their history to respond warmly and offer practical steps. "
            "If the user drifts off-topic, gently bring them back to their feelings."
        )

        # Assemble messages
        messages = [
            {"role": "system",   "content": sys_prompt},
            {"role": "system",   "content": "Patient Sheet:\n" + sheet_text},
        ]
        messages.extend(self.histories[session_id])
        messages.append({"role": "user", "content": memory_block + user_message})

        # Call the LLM
        try:
            resp = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                max_tokens_to_sample=250,
                temperature=0.7,
            )
            answer = resp.choices[0].message.content.strip()
        except Exception:
            if lang == 'ar':
                return "عذرًا، حدث خطأ. هل يمكنك المحاولة مرة أخرى؟"
            elif lang == 'franco':
                return "M3lesh, fe moshkela. 7awel tani law sama7t."
            else:
                return "Sorry, I ran into an error. Could you try again?"

        # Save history and RAG memory
        self.histories[session_id].append({"role":"user",    "content":user_message})
        self.histories[session_id].append({"role":"assistant","content":answer})
        self.mem.add(session_id, user_message, answer)

        return answer


if __name__ == "__main__":
    # Quick smoke test
    agent = ConversationAgent(
        model_name="meta-llama/Meta-Llama-3.1-8B-Instruct-Turbo",
        embed_model="togethercomputer/m2-bert-80M-8k-retrieval",
        index_name="wss-ai-memory"
    )
    for inp in ["hahaha", "k", "I feel sad today"]:
        print("User:", inp)
        print("Bot :", agent.ask("demo", inp))
        print("---")
