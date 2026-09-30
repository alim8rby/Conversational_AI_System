"""LLM-based conversational answer classification."""

from __future__ import annotations

import json
from typing import Dict

from providers.ollama_client import OllamaClient


CLASSIFIER_SYSTEM_PROMPT = """You classify a user's response to an intake question.
Your job is to understand the conversational relationship, not to measure word overlap.

Return ONLY valid JSON with exactly these keys:
{"label":"answer|negative|refusal|meta|unclear|off_topic","reason":"brief explanation"}

Definitions:
- answer: the user meaningfully responds to the question.
- negative: the user clearly answers with absence, denial, or "nothing". This is still a valid response.
- refusal: the user declines to answer. This is still a valid conversational response.
- meta: the user is talking about the test, assistant, conversation, or process rather than the intake topic. Treat this as valid conversational input, not an invalid answer.
- unclear: the user appears to be trying to answer but the meaning is too ambiguous to proceed.
- off_topic: the user gives content unrelated to the question and not clearly meta/test/refusal.

Examples:
Question: "What do you notice or experience in this situation?"
User: "nothing"
JSON: {"label":"negative","reason":"The user explicitly reports no noticeable experience."}

Question: "What brings you here today?"
User: "لا شيء"
JSON: {"label":"negative","reason":"The user denies having a specific concern."}

Question: "Tell me about yourself, including your occupation."
User: "I'm just testing you"
JSON: {"label":"meta","reason":"The user is explicitly describing the test rather than answering the intake topic."}

Question: "What brings you here today?"
User: "I'd rather not say."
JSON: {"label":"refusal","reason":"The user declines to provide the information."}

Question: "Tell me about yourself."
User: "I work in finance and live with my family."
JSON: {"label":"answer","reason":"The user provides information relevant to the requested introduction."}

Question: "What brings you here today?"
User: "The weather has been strange lately."
JSON: {"label":"off_topic","reason":"The response does not address the intake question."}
"""


class AnswerClassifier:
    """Classify intake responses using the local Ollama LLM."""

    LABELS = {"answer", "negative", "refusal", "meta", "unclear", "off_topic"}

    def __init__(self, client: OllamaClient):
        self.client = client

    def classify(
        self,
        question: str,
        answer: str,
        lang: str = "en",
    ) -> Dict[str, str]:
        language_note = (
            "The user is responding in Arabic; understand Arabic naturally."
            if lang == "ar"
            else "The user is responding in English; understand English naturally."
        )
        messages = [
            {"role": "system", "content": CLASSIFIER_SYSTEM_PROMPT},
            {
                "role": "user",
                "content": (
                    f"Language: {lang}\n{language_note}\n"
                    f"Question: {question}\nUser response: {answer}"
                ),
            },
        ]
        result = self.client.chat(
            messages,
            temperature=0.0,
            max_tokens=120,
            format="json",
        )
        try:
            parsed = json.loads(result["content"])
        except (KeyError, json.JSONDecodeError) as exc:
            raise RuntimeError("Answer classifier returned invalid JSON.") from exc

        label = parsed.get("label")
        reason = parsed.get("reason", "")
        if label not in self.LABELS or not isinstance(reason, str):
            raise RuntimeError("Answer classifier returned an invalid classification.")
        return {"label": label, "reason": reason}
