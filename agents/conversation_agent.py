import math
import os
import re
import time
from typing import Dict, List, Tuple

from providers.ollama_client import OllamaClient

from agents.answer_classifier import AnswerClassifier
from domains.domain_config import DomainConfig
from interview_manager import InterviewManager
from knowledge.context_builder import KnowledgeContextBuilder
from knowledge.knowledge_base import KnowledgeBase
from workflows.workflow_manager import WorkflowManager
from tools.tool_manager import ToolManager
from tools.domain_tool_registry import register_domain_tools
from memory.memory_manager import MemoryManager
from observability.run import new_run, finish_run, record_error
from policies.policy_engine import PolicyEngine

MODEL_NAME = os.getenv("LLM_MODEL", "llama3.2:3b")
EMBED_MODEL = os.getenv("EMBED_MODEL", "nomic-embed-text")
MEMORY_STORE_PATH = os.getenv("MEMORY_STORE_PATH", "data/memory.json")
DOMAIN_CONFIG_PATH = os.getenv(
    "DOMAIN_CONFIG_PATH",
    "domains/demo_ecommerce/domain.json",
)
APP_VERSION = os.getenv("APP_VERSION", os.getenv("GIT_COMMIT", "unknown"))
PROMPT_VERSION = os.getenv("PROMPT_VERSION", "v1")
RETRIEVAL_K = 3
KNOWLEDGE_CONTEXT_MAX_CHARS = 4000
TOOL_TIMEOUT_SECONDS = float(os.getenv("TOOL_TIMEOUT_SECONDS", "5.0"))
GENERATION_TEMPERATURE = 0.7
GENERATION_MAX_TOKENS = 250

# Retained as an observability reference for the historical EXP002 experiment.
# It is no longer used as the intake decision boundary.
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
        domain_config_path: str = DOMAIN_CONFIG_PATH,
    ):
        self.client = OllamaClient(
            base_url=os.getenv("OLLAMA_BASE_URL", "http://localhost:11434"),
            model=model_name,
            embed_model=embed_model,
        )
        self.classifier = AnswerClassifier(self.client)
        self.model = model_name
        self.domain = DomainConfig(domain_config_path)
        self.policy_engine = PolicyEngine(
            self.domain.policies,
            allowed_tools=[tool["id"] for tool in self.domain.tools],
        )
        self.mem = MemoryManager(embed_model, store_path)
        self.knowledge = KnowledgeBase(embed_model=embed_model)
        self.context_builder = KnowledgeContextBuilder()
        self.workflow_manager = WorkflowManager(self.domain, self.client)
        self.tools = ToolManager(default_timeout_seconds=TOOL_TIMEOUT_SECONDS)
        register_domain_tools(self.tools, self.domain.tools)
        # Structured intake is optional; the active domain decides whether it is enabled.
        self.intake_enabled = self.domain.intake_enabled
        self.interviewer = InterviewManager()
        self.awaiting: Dict[str, Tuple[str, str]] = {}
        self.histories: Dict[str, List[dict]] = {}
        self.session_languages: Dict[str, str] = {}
        self.clarify_counts: Dict[Tuple[str, str, str], int] = {}

    def start_session(self, session_id: str, lang: str = "en") -> str:
        """Initialize a session and persist its selected response language."""
        lang = lang if lang in {"en", "ar"} else "en"
        self.session_languages[session_id] = lang
        self.histories.setdefault(session_id, [])

        if not self.intake_enabled:
            self.awaiting.pop(session_id, None)
            assistant_name = self.domain.assistant["name"]
            purpose = self.domain.assistant["purpose"]
            if lang == "ar":
                return f"أهلاً، أنا {assistant_name}. {purpose}"
            return f"Hi, I'm {assistant_name}. {purpose}"

        self.interviewer.init_session(session_id)
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
    ) -> Dict[str, str]:
        """Classify the conversational role of an intake response.

        The LLM classifier is the decision-maker. Semantic similarity is retained
        only as an observability signal so we can measure how well it correlates
        with the richer conversational classification.
        """
        del similarity
        return self.classifier.classify(question, answer, lang)

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

    def _handle_meta(self, section: str, field: str, lang: str) -> str:
        """Acknowledge meta/test input without consuming the current intake field."""
        if lang == "ar":
            acknowledgement = "تمام، فهمت إنك بتختبر النظام. "
        else:
            acknowledgement = "Understood. I see that you are testing the system. "
        if field == "main":
            question = self.interviewer.get_section_prompt(section, lang)
        else:
            question = self.interviewer.get_section_prompt(section, lang)
        return acknowledgement + (question or "")

    def ask(self, session_id: str, user_message: str) -> str:
        # A started session owns its language. Detection is only a fallback for
        # callers that bypass the explicit session-start endpoint.
        lang = self.session_languages.get(session_id)
        if lang is None:
            lang = detect_language(user_message)
            self.session_languages[session_id] = lang
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
                "domain_id": self.domain.domain_id,
                "domain_version": self.domain.data["version"],
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

        self.histories.setdefault(session_id, [])

        policy_decision = self.policy_engine.evaluate(user_message)
        run["metrics"]["policy"] = policy_decision.as_dict()
        if policy_decision.decision == "blocked":
            record_error(
                run,
                "dialogue",
                f"Policy blocked request: {policy_decision.policy}",
            )
            finish_run(run)
            self.last_turn_metrics = run["metrics"]["policy"]
            return (
                "لا أستطيع المساعدة في طلبات تهدف إلى تجاوز ضوابط أمان النظام."
                if lang == "ar"
                else "I can't help with requests that attempt to bypass system safeguards."
            )

        if self.intake_enabled:
            self.interviewer.init_session(session_id)

        if self.intake_enabled and not self.interviewer.is_complete(session_id):
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
                classification = self._classify_answer(
                    question or "",
                    user_message,
                    lang,
                    similarity=similarity,
                )
                classification_latency_ms = round(
                    (time.perf_counter() - classification_started) * 1000,
                    2,
                )
                label = classification["label"]
                run["metrics"]["classification"] = {
                    "semantic_similarity": similarity,
                    "semantic_similarity_threshold": ANSWER_RELEVANCE_THRESHOLD,
                    "semantic_similarity_latency_ms": similarity_latency_ms,
                    "classification_label": label,
                    "classification_reason": classification["reason"],
                    "classification_method": "llm_structured",
                    "classification_latency_ms": classification_latency_ms,
                }
                self.last_turn_metrics = run["metrics"]["classification"]

                if label in {"answer", "negative", "refusal"}:
                    self.interviewer.record_response(session_id, section, field, user_message)
                    self.clarify_counts.pop((session_id, section, field), None)
                elif label == "meta":
                    finish_run(run)
                    return self._handle_meta(section, field, lang)
                else:
                    finish_run(run)
                    return self._clarify(session_id, section, field, lang)

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

        sheet = self.interviewer.get_flat_sheet(session_id) if self.intake_enabled else ""

        workflow_started = time.perf_counter()
        try:
            workflow_plan = self.workflow_manager.route_and_plan(user_message)
        except Exception:
            run["metrics"]["workflow"] = {
                "workflow_error": True,
                "workflow_latency_ms": round(
                    (time.perf_counter() - workflow_started) * 1000, 2
                ),
            }
            record_error(run, "dialogue", "Workflow routing failed")
            finish_run(run, "failed")
            self.last_turn_metrics = run["metrics"]["workflow"]
            return "Sorry, I could not determine how to handle that request. Please try again."

        workflow_plan["workflow_latency_ms"] = round(
            (time.perf_counter() - workflow_started) * 1000, 2
        )

        tool_result = None
        required_tools = [
            requirement
            for requirement in workflow_plan.get("requires", [])
            if requirement in self.tools.tool_ids
        ]

        if required_tools:
            authorized_tools = []
            denied_tools = []

            for tool_id in required_tools:
                decision = self.policy_engine.authorize_tool(tool_id)
                if decision.decision == "allowed":
                    authorized_tools.append(tool_id)
                else:
                    denied_tools.append(
                        {
                            "tool_id": tool_id,
                            "decision": decision.as_dict(),
                        }
                    )

            if denied_tools:
                run["metrics"]["tool_authorization"] = {
                    "authorized_tools": authorized_tools,
                    "denied_tools": denied_tools,
                }

            tool_executions = self.tools.execute_required(
                authorized_tools,
                user_message,
                timeout_seconds=TOOL_TIMEOUT_SECONDS,
            )
            run["metrics"]["tool"] = {
                "required_tools": required_tools,
                "authorized_tools": authorized_tools,
                "denied_tools": [item["tool_id"] for item in denied_tools],
                "executions": tool_executions,
                "failed_count": sum(
                    execution["status"] == "failed"
                    for execution in tool_executions
                ),
                "requires_input_count": sum(
                    execution["status"] == "requires_input"
                    for execution in tool_executions
                ),
                "timeout_count": sum(
                    execution.get("error", {}).get("type") == "tool_timeout"
                    for execution in tool_executions
                ),
            }

            successful_results = [
                execution["result"]
                for execution in tool_executions
                if execution["status"] == "executed"
            ]
            if successful_results:
                tool_result = successful_results[0]

            failed_tools = [
                execution
                for execution in tool_executions
                if execution["status"] == "failed"
            ]
            if failed_tools:
                run["metrics"]["tool"]["errors"] = [
                    {
                        "tool_id": execution["tool_id"],
                        "error": execution["error"],
                    }
                    for execution in failed_tools
                ]

        run["metrics"]["workflow"] = workflow_plan
        self.last_run = run
        self.last_turn_metrics = run["metrics"]["workflow"]

        retrieval_started = time.perf_counter()
        memories = self.mem.retrieve(session_id, user_message, k=RETRIEVAL_K)
        knowledge_results = self.knowledge.retrieve(user_message, k=RETRIEVAL_K)
        retrieval_latency_ms = round((time.perf_counter() - retrieval_started) * 1000, 2)

        knowledge_context = self.context_builder.build(
            knowledge_results,
            max_chars=KNOWLEDGE_CONTEXT_MAX_CHARS,
        )
        run["metrics"]["retrieval"] = {
            "retrieval_latency_ms": retrieval_latency_ms,
            "memory_count": len(memories),
            "knowledge_count": len(knowledge_results),
            "knowledge_included_count": knowledge_context["included_count"],
            "knowledge_context_chars": knowledge_context["context_chars"],
            "knowledge_sources": knowledge_context["sources"],
        }
        self.last_turn_metrics = run["metrics"]["retrieval"]

        memory_context = "\n".join(
            item["text"] if isinstance(item, dict) else item for item in memories
        )
        system = (
            f"You are a concise conversational AI. Respond in {'Arabic' if lang == 'ar' else 'English'}. "
            "Do not switch languages unless the session language is explicitly changed. "
            "Use the provided session information, "
            "relevant conversation memory, and domain knowledge to answer the user. "
            "Treat domain knowledge as the source of truth for business facts. "
            "Follow the selected workflow plan and do not claim a tool action has happened unless a tool actually ran. "
            "Do not invent product availability, order status, or policy details. "
            "If the available knowledge does not answer the question, say so rather than guessing. "
            "Do not claim to be a clinician, diagnose the user, or imply that this prototype replaces professional care."
        )
        messages = [
            {"role": "system", "content": system},
            {"role": "system", "content": "Workflow plan:\n" + str(workflow_plan)},
        ]
        if sheet:
            messages.insert(
                1,
                {"role": "system", "content": "Session information:\n" + sheet},
            )
        messages.extend(self.histories[session_id])
        if memory_context:
            messages.append({"role": "system", "content": "Relevant conversation memory:\n" + memory_context})
        if tool_result is not None:
            messages.append({
                "role": "system",
                "content": "Verified tool result:\n" + str(tool_result),
            })
        if knowledge_context["context"]:
            messages.append({
                "role": "system",
                "content": "Relevant domain knowledge:\n" + knowledge_context["context"],
            })
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

        output_policy = self.policy_engine.evaluate_output(answer)
        run["metrics"]["output_policy"] = output_policy.as_dict()
        if output_policy.decision == "blocked":
            record_error(
                run,
                "generation",
                f"Output policy blocked generated response: {output_policy.policy}",
            )
            finish_run(run)
            self.last_turn_metrics = run["metrics"]["output_policy"]
            return (
                "عذراً، لا أستطيع تقديم هذه الاستجابة."
                if lang == "ar"
                else "Sorry, I cannot provide that response."
            )

        finish_run(run)

        self.histories[session_id].extend([
            {"role": "user", "content": user_message},
            {"role": "assistant", "content": answer},
        ])
        memory_id = f"{session_id}-{len(self.histories[session_id])}"
        self.mem.add(session_id, memory_id, f"User: {user_message}\nAssistant: {answer}")
        return answer
