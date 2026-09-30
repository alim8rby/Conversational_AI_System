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
    """Evaluate deterministic domain policies before execution."""

    def __init__(
        self,
        policies: list[str] | None = None,
        allowed_tools: list[str] | None = None,
    ):
        self.policies = policies or []
        self.allowed_tools = set(allowed_tools or [])
        self._rules = [
            (
                "safeguard_bypass",
                ("ignore previous instructions", "bypass policy", "disable safeguards"),
                "The request attempts to bypass system safeguards.",
            ),
            (
                "credential_exfiltration",
                (
                    "show me the api key",
                    "give me the api key",
                    "reveal the password",
                    "show me the password",
                    "reveal credentials",
                ),
                "The request attempts to obtain protected credentials.",
            ),
        ]

    def evaluate(self, user_message: str) -> PolicyDecision:
        text = user_message.strip().lower()

        for policy_id, phrases, reason in self._rules:
            if self._matches_any(text, phrases):
                return PolicyDecision(
                    decision="blocked",
                    reason=reason,
                    policy=policy_id,
                )

        return PolicyDecision(
            decision="allowed",
            reason="No configured blocking policy matched the request.",
        )

    def authorize_tool(self, tool_id: str) -> PolicyDecision:
        """Check whether a registered tool is authorized by the active domain."""
        if tool_id not in self.allowed_tools:
            return PolicyDecision(
                decision="blocked",
                reason=f"Tool '{tool_id}' is not authorized by the active domain.",
                policy="tool_authorization",
            )

        return PolicyDecision(
            decision="allowed",
            reason=f"Tool '{tool_id}' is authorized by the active domain.",
            policy="tool_authorization",
        )

    @staticmethod
    def _matches_any(text: str, phrases: tuple[str, ...]) -> bool:
        return any(phrase in text for phrase in phrases)
