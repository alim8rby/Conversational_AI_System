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
        # LLM & RAG
        self.client   = Together(api_key=os.getenv("TOGETHER_API_KEY"))
        self.model    = model_name
        self.mem      = MemoryManager(embed_model, index_name)

        # Structured interview
        self.interviewer = InterviewManager()
        self.awaiting    = {}      # session_id -> last section asked
        self.histories   = {}      # session_id -> conversation history

    def ask(self, session_id: str, user_message: str) -> str:
        # --- 1) Language detection & fallback strings ---
        lang = detect_language(user_message)
        if lang == 'ar':
            clarifier = "أسمع ضحكتك، هل تشعر بالراحة أم أنك متوتر؟ شاركني ما يدور في بالك."
        elif lang == 'franco':
            clarifier = "Basma3 d7ktak—enta mabsout aw motawater? 2ol lyya aktar 3an elli 3ala balak."
        else:
            clarifier = (
                "I hear your laughter—sometimes that’s a way of coping. "
                "Would you like to tell me more about what you’re feeling right now?"
            )

        # --- 2) Detect non-answers (e.g. "hahah", "lol") ---
        # simple regex to catch repeated "ha" or "heh"
        if re.fullmatch(r'\s*(?:ha)+h?\s*', user_message.lower()) or \
           re.fullmatch(r'\s*(?:heh)+\s*', user_message.lower()) or \
           len(user_message.strip()) < 2:
            return clarifier

        # --- 3) Ensure session data exists ---
        if session_id not in self.histories:
            self.histories[session_id] = []
        self.interviewer.init_session(session_id)

        # --- 4) STRUCTURED INTERVIEW PHASE ---
        if not self.interviewer.is_complete(session_id):
            last_sec = self.awaiting.get(session_id)
            # record the previous valid answer
            if last_sec:
                self.interviewer.record_response(session_id, user_message)

            # ask the next section
            next_sec = self.interviewer.next_section(session_id)
            question = self.interviewer.get_question(session_id)

            # build a natural transition
            if last_sec is None:
                prompt = f"Hello! I’m El Consulto, your virtual psychiatrist. {question}"
            else:
                prompt = f"Thank you for sharing. {question}"

            # mark which section we’re awaiting
            self.awaiting[session_id] = next_sec
            return prompt

        # --- 5) FREE-FORM THERAPY PHASE ---
        # assemble patient sheet
        sheet = self.interviewer.get_sheet(session_id)
        sheet_text = "\n".join(f"{k.replace('_',' ').title()}: {v}"
                               for k, v in sheet.items())

        # retrieve relevant memory
        past_notes = self.mem.retrieve(session_id, user_message, k=3)
        memory_block = ("\n".join(past_notes) + "\n\n") if past_notes else ""

        # build the chat messages
        sys_base = (
            "You are El Consulto, an empathic psychiatrist AI. "
            "Use details from this client’s psychiatric sheet to inform each reply. "
            "Keep responses concise, offer practical steps, and maintain warmth. "
            "If the user goes off-topic, gently refocus on their feelings."
        )
        messages = [
            {"role": "system",   "content": sys_base},
            {"role": "system",   "content": "Patient Sheet:\n" + sheet_text},
        ]
        messages.extend(self.histories[session_id])
        messages.append({"role": "user", "content": memory_block + user_message})

        # call the LLM with error handling
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
            if lang == 'ar':
                return "عذرًا، حدث خطأ مؤقت. هل يمكنك المحاولة مرة أخرى؟"
            elif lang == 'franco':
                return "M3lesh, fe moshkela tecnyia. 7awel tani law sama7t."
            else:
                return "Sorry, something went wrong. Could you try again?"

        # record history & memory
        self.histories[session_id].append({"role":"user",    "content":user_message})
        self.histories[session_id].append({"role":"assistant","content":answer})
        self.mem.add(session_id, user_message, answer)

        return answer

if __name__ == "__main__":
    # Quick test
    agent = ConversationAgent(
        model_name="meta-llama/Meta-Llama-3.1-8B-Instruct-Turbo",
        embed_model="togethercomputer/m2-bert-80M-8k-retrieval",
        index_name="wss-ai-memory"
    )
    print(agent.ask("test-session", "hahaha"))        # clarifier
    print(agent.ask("test-session", "I feel sad."))  # structured Q1
