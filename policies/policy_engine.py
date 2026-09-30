"""Domain-configurable policy evaluation before workflow execution."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class PolicyDecision:
    """Structured result of a policy evaluation."""

    decision: str
    reason: str
    policy: str | None = None

    def as_dict(self) -> dict[str, Any]:
        return {
            "decision": self.decision,
            "reason": self.reason,
            "policy": self.policy,
        }


class PolicyEngine:
    """Evaluate deterministic domain policies before execution.

    The first implementation intentionally uses explicit policy rules rather
    than an LLM. This makes blocking behavior predictable and auditable.
    """

    def __init__(self, policies: list[str] | None = None):
        self.policies = policies or []

    def evaluate(self, user_message: str) -> PolicyDecision:
        text = user_message.strip().lower()

        if self._matches_any(
            text,
            ("ignore previous instructions", "bypass policy", "disable safeguards"),
        ):
            return PolicyDecision(
                decision="blocked",
                reason="The request attempts to bypass system safeguards.",
                policy="safeguard_bypass",
            )

        return PolicyDecision(
            decision="allowed",
            reason="No configured blocking policy matched the request.",
        )

    @staticmethod
    def _matches_any(text: str, phrases: tuple[str, ...]) -> bool:
        return any(phrase in text for phrase in phrases)
