import math
import os
import re
from typing import Dict, List, Tuple

from together import Together

from interview_manager import InterviewManager
from memory.memory_manager import MemoryManager

MODEL_NAME = os.getenv("LLM_MODEL", "meta-llama/Meta-Llama-3.1-8B-Instruct-Turbo")
EMBED_MODEL = os.getenv("EMBED_MODEL", "togethercomputer/m2-bert-80M-8k-retrieval")
INDEX_NAME = os.getenv("PINECONE_INDEX", "conversation-memory")


def detect_language(text: str) -> str:
    if re.search(r"[\u0600-\u06FF]", text) or re.search(r"\d", text):
        return "ar"
    return "en"


def is_valid_answer(text: str) -> bool:
    normalized = text.strip().lower()
    if len(normalized) < 3:
        return False
    if re.fullmatch(r"(?:ha)+h?", normalized) or re.fullmatch(r"(?:heh)+", normalized):
        return False
    return len(normalized) >= 5


class ConversationAgent:
    """Stateful conversational agent combining structured intake and semantic memory."""

    def __init__(self, model_name: str = MODEL_NAME, embed_model: str = EMBED_MODEL, index_name: str = INDEX_NAME):
        self.client = Together(api_key=os.getenv("TOGETHER_API_KEY"))
        self.model = model_name
        self.mem = MemoryManager(embed_model, index_name)
        self.interviewer = InterviewManager()
        self.awaiting: Dict[str, Tuple[str, str]] = {}
        self.histories: Dict[str, List[dict]] = {}
        self.clarify_counts: Dict[Tuple[str, str, str], int] = {}

    def _semantic_similarity(self, question: str, answer: str) -> float:
        try:
            response = self.client.embeddings.create(
                model=self.mem.embed_model,
                input=[question, answer],
            )
            qvec, avec = response.data[0].embedding, response.data[1].embedding
            dot = sum(q * a for q, a in zip(qvec, avec))
            qmag = math.sqrt(sum(q * q for q in qvec))
            amag = math.sqrt(sum(a * a for a in avec))
            return dot / (qmag * amag) if qmag and amag else 0.0
        except Exception:
            return 0.0

    def _classify_answer(self, question: str, answer: str, lang: str) -> bool:
        system = "Does the answer address the question? Reply only YES or NO." if lang == "en" else "هل تجيب الإجابة على السؤال؟ أجب فقط بنعم أو لا."
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system},
                    {"role": "user", "content": f"Question: {question}\nAnswer: {answer}"},
                ],
                max_tokens=3,
                temperature=0.0,
            )
            result = response.choices[0].message.content.strip().lower()
            return result.startswith("yes") or result.startswith("نعم")
        except Exception:
            return False

    def _clarify(self, session: str, section: str, field: str, lang: str) -> str:
        key = (session, section, field)
        count = self.clarify_counts.get(key, 0)
        self.clarify_counts[key] = count + 1
        if lang == "ar":
            prompts = [
                "ممكن توضّح لي أكثر؟",
                "ماذا تلاحظ أو تشعر في هذا الموقف تحديداً؟",
                "كيف يرتبط ما ذكرته الآن بما تحدثنا عنه سابقاً؟",
            ]
        else:
            prompts = [
                "Could you tell me a little more?",
                "What do you notice or experience in this situation specifically?",
                "How does what you just mentioned connect with what you shared earlier?",
            ]
        return prompts[min(count, len(prompts) - 1)]

    def ask(self, session_id: str, user_message: str) -> str:
        lang = detect_language(user_message)
        if not is_valid_answer(user_message):
            current = self.awaiting.get(session_id)
            return self._clarify(session_id, *current, lang) if current else (
                "ممكن تحكي لي أكثر؟" if lang == "ar" else "Could you tell me a little more?"
            )

        self.interviewer.init_session(session_id)
        self.histories.setdefault(session_id, [])

        if not self.interviewer.is_complete(session_id):
            current = self.awaiting.get(session_id)
            if current:
                section, field = current
                question = self.interviewer.get_prompt(session_id, lang)
                similarity = self._semantic_similarity(question or "", user_message)
                relevant = self._classify_answer(question or "", user_message, lang)
                if similarity < 0.30 or not relevant:
                    return self._clarify(session_id, section, field, lang)
                self.interviewer.record_response(session_id, section, field, user_message)
                self.clarify_counts.pop((session_id, section, field), None)

            section, field = self.interviewer.next_field(session_id)
            prompt = self.interviewer.get_prompt(session_id, lang)
            self.awaiting[session_id] = (section, field)
            return prompt or ""

        sheet = self.interviewer.get_flat_sheet(session_id)
        memories = self.mem.retrieve(session_id, user_message, k=3)
        memory_context = "\n".join(memories)
        system = (
            "You are a concise conversational AI. Use the provided session information and relevant memory to maintain context. "
            "Do not claim to be a clinician, diagnose the user, or imply that this prototype replaces professional care."
        )
        messages = [
            {"role": "system", "content": system},
            {"role": "system", "content": "Session information:\n" + sheet},
        ]
        messages.extend(self.histories[session_id])
        if memory_context:
            messages.append({"role": "system", "content": "Relevant memory:\n" + memory_context})
        messages.append({"role": "user", "content": user_message})

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                max_tokens=250,
                temperature=0.7,
            )
            answer = response.choices[0].message.content.strip()
        except Exception:
            return "Sorry, something went wrong. Please try again."

        self.histories[session_id].extend([
            {"role": "user", "content": user_message},
            {"role": "assistant", "content": answer},
        ])
        memory_id = f"{session_id}-{len(self.histories[session_id])}"
        self.mem.add(session_id, memory_id, f"User: {user_message}\nAssistant: {answer}")
        return answer
