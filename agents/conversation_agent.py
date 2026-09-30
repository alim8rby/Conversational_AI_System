import math
import os
import re
import time
from typing import Dict, List, Tuple

from providers.ollama_client import OllamaClient

from interview_manager import InterviewManager
from memory.memory_manager import MemoryManager
from observability.run import new_run, finish_run, record_error

MODEL_NAME = os.getenv("LLM_MODEL", "llama3.2:3b")
EMBED_MODEL = os.getenv("EMBED_MODEL", "nomic-embed-text")
MEMORY_STORE_PATH = os.getenv("MEMORY_STORE_PATH", "data/memory.json")
APP_VERSION = os.getenv("APP_VERSION", os.getenv("GIT_COMMIT", "unknown"))
PROMPT_VERSION = os.getenv("PROMPT_VERSION", "v1")
RETRIEVAL_K = 3
GENERATION_TEMPERATURE = 0.7
GENERATION_MAX_TOKENS = 250

# Initial empirical gate from EXP002. This is a measured prototype threshold,
# not a production-calibrated classifier boundary.
ANSWER_RELEVANCE_THRESHOLD = 0.46


def detect_language(text: str) -> str:
    """Detect Arabic by script presence, not by numeric content."""
    if re.search(r"[؀-ۿ]", text):
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

    def __init__(
        self,
        model_name: str = MODEL_NAME,
        embed_model: str = EMBED_MODEL,
        store_path: str = MEMORY_STORE_PATH,
    ):
        self.client = OllamaClient(
            base_url=os.getenv("OLLAMA_BASE_URL", "http://localhost:11434"),
            model=model_name,
            embed_model=embed_model,
        )
        self.model = model_name
        self.mem = MemoryManager(embed_model, store_path)
        self.interviewer = InterviewManager()
        self.awaiting: Dict[str, Tuple[str, str]] = {}
        self.histories: Dict[str, List[dict]] = {}
        self.clarify_counts: Dict[Tuple[str, str, str], int] = {}

    def start_session(self, session_id: str, lang: str = "en") -> str:
        """Initialize an intake session and return its first question."""
        self.interviewer.init_session(session_id)
        self.histories.setdefault(session_id, [])
        section, field = self.interviewer.next_field(session_id)
        if not section:
            self.awaiting.pop(session_id, None)
            return ""
        self.awaiting[session_id] = (section, field)
        return self.interviewer.get_prompt(session_id, lang) or ""

    def _semantic_similarity(self, question: str, answer: str) -> float:
        try:
            embeddings = self.client.embed([question, answer])
            qvec, avec = embeddings[0], embeddings[1]
            dot = sum(q * a for q, a in zip(qvec, avec))
            qmag = math.sqrt(sum(q * q for q in qvec))
            amag = math.sqrt(sum(a * a for a in avec))
            return dot / (qmag * amag) if qmag and amag else 0.0
        except Exception:
            return 0.0

    def _classify_answer(
        self,
        question: str,
        answer: str,
        lang: str,
        similarity: float | None = None,
    ) -> bool:
        """Validate intake relevance using the measured embedding signal.

        The local 3B LLM was tested as a binary relevance classifier in EXP002
        and incorrectly rejected clearly relevant answers. The embedding model
        showed measurable separation, so it is the current deterministic gate.
        lang is retained for call compatibility and future language-specific
        validation.
        """
        del lang
        score = (
            self._semantic_similarity(question, answer)
            if similarity is None
            else similarity
        )
        return score >= ANSWER_RELEVANCE_THRESHOLD

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
        run = new_run(
            session_id,
            user_message,
            lang,
            metadata={
                "application_version": APP_VERSION,
                "model": self.model,
                "embedding_model": self.mem.embed_model,
                "memory_store": MEMORY_STORE_PATH,
                "prompt_version": PROMPT_VERSION,
                "retrieval_k": RETRIEVAL_K,
                "temperature": GENERATION_TEMPERATURE,
                "max_tokens": GENERATION_MAX_TOKENS,
            },
        )
        self.last_run = run
        run["metrics"]["dialogue"] = {"input_valid": is_valid_answer(user_message)}
        if not run["metrics"]["dialogue"]["input_valid"]:
            current = self.awaiting.get(session_id)
            finish_run(run)
            return self._clarify(session_id, *current, lang) if current else (
                "ممكن تحكي لي أكثر؟" if lang == "ar" else "Could you tell me a little more?"
            )

        self.interviewer.init_session(session_id)
        self.histories.setdefault(session_id, [])

        if not self.interviewer.is_complete(session_id):
            current = self.awaiting.get(session_id)
            if current:
                section, field = current
                question = (
                    self.interviewer.get_prompt(session_id, lang)
                    if field == "main"
                    else self.interviewer.get_section_prompt(section, lang)
                )
                similarity_started = time.perf_counter()
                similarity = self._semantic_similarity(question or "", user_message)
                similarity_latency_ms = round((time.perf_counter() - similarity_started) * 1000, 2)
                classification_started = time.perf_counter()
                relevant = self._classify_answer(
                    question or "",
                    user_message,
                    lang,
                    similarity=similarity,
                )
                classification_latency_ms = round(
                    (time.perf_counter() - classification_started) * 1000,
                    2,
                )
                run["metrics"]["classification"] = {
                    "semantic_similarity": similarity,
                    "semantic_similarity_threshold": ANSWER_RELEVANCE_THRESHOLD,
                    "semantic_similarity_latency_ms": similarity_latency_ms,
                    "classification_relevant": relevant,
                    "classification_method": "embedding_threshold",
                    "classification_latency_ms": classification_latency_ms,
                }
                self.last_turn_metrics = run["metrics"]["classification"]
                if similarity < 0.30 or not relevant:
                    finish_run(run)
                    return self._clarify(session_id, section, field, lang)
                self.interviewer.record_response(session_id, section, field, user_message)
                self.clarify_counts.pop((session_id, section, field), None)

            section, field = self.interviewer.next_field(session_id)
            if section:
                prompt = self.interviewer.get_prompt(session_id, lang)
                self.awaiting[session_id] = (section, field)
            else:
                prompt = ""
                self.awaiting.pop(session_id, None)
            run["metrics"]["dialogue"]["next_section"] = section
            run["metrics"]["dialogue"]["next_field"] = field
            finish_run(run)
            return prompt or ""

        sheet = self.interviewer.get_flat_sheet(session_id)
        retrieval_started = time.perf_counter()
        memories = self.mem.retrieve(session_id, user_message, k=RETRIEVAL_K)
        retrieval_latency_ms = round((time.perf_counter() - retrieval_started) * 1000, 2)
        run["metrics"]["retrieval"] = {
            "retrieval_latency_ms": retrieval_latency_ms,
            "retrieved_count": len(memories),
        }
        self.last_turn_metrics = run["metrics"]["retrieval"]
        memory_context = "\n".join(item["text"] if isinstance(item, dict) else item for item in memories)
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

        generation_started = time.perf_counter()
        try:
            response = self.client.chat(
                messages=messages,
                max_tokens=GENERATION_MAX_TOKENS,
                temperature=GENERATION_TEMPERATURE,
            )
            answer = response["content"]
            usage = response.get("usage")
        except Exception:
            latency = round((time.perf_counter() - generation_started) * 1000, 2)
            run["metrics"]["generation"] = {
                "generation_latency_ms": latency,
                "generation_error": True,
            }
            record_error(run, "generation", "LLM generation failed")
            finish_run(run, "failed")
            self.last_turn_metrics = run["metrics"]["generation"]
            return "Sorry, something went wrong. Please try again."

        run["metrics"]["generation"] = {
            "generation_latency_ms": round((time.perf_counter() - generation_started) * 1000, 2),
            "generation_error": False,
        }
        if usage is not None:
            run["metrics"]["generation"]["token_usage"] = {
                "prompt_tokens": usage.get("prompt_tokens"),
                "completion_tokens": usage.get("completion_tokens"),
                "total_tokens": usage.get("total_tokens"),
            }
        self.last_turn_metrics = {
            **getattr(self, "last_turn_metrics", {}),
            **run["metrics"]["generation"],
        }
        finish_run(run)

        self.histories[session_id].extend([
            {"role": "user", "content": user_message},
            {"role": "assistant", "content": answer},
        ])
        memory_id = f"{session_id}-{len(self.histories[session_id])}"
        self.mem.add(session_id, memory_id, f"User: {user_message}\nAssistant: {answer}")
        return answer
