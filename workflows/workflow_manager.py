"""Route conversations into domain-defined workflows and build execution plans."""

from __future__ import annotations

import json
from typing import Dict, List

from domains.domain_config import DomainConfig
from providers.ollama_client import OllamaClient


class WorkflowManager:
    """Resolve a user request to one configured workflow.

    This layer owns workflow selection, but does not execute tools or mutate
    business state yet. It returns a small execution plan for later layers.
    """

    ROUTER_SYSTEM_PROMPT = """You route a user's request to one configured business workflow.

Return ONLY valid JSON with exactly these keys:
{"workflow_id":"...", "reason":"brief explanation"}

Choose exactly one workflow from the supplied list.
Use the workflow descriptions to decide.
Do not invent a workflow that is not configured.
"""

    def __init__(self, domain: DomainConfig, client: OllamaClient):
        self.domain = domain
        self.client = client
        self._definitions = self._normalize_workflows(domain.workflows)

    @staticmethod
    def _normalize_workflows(workflows: List) -> Dict[str, Dict]:
        definitions: Dict[str, Dict] = {}
        for workflow in workflows:
            if isinstance(workflow, str):
                definitions[workflow] = {
                    "id": workflow,
                    "description": workflow.replace("_", " "),
                    "requires": [],
                }
            elif isinstance(workflow, dict) and workflow.get("id"):
                definitions[workflow["id"]] = workflow
        return definitions

    @property
    def workflow_ids(self) -> List[str]:
        return list(self._definitions)

    def route(self, user_message: str) -> Dict[str, str]:
        """Classify the request into one configured workflow."""
        if not self._definitions:
            raise RuntimeError("The domain does not define any workflows.")

        workflow_descriptions = "\n".join(
            f'- {workflow_id}: {definition.get("description", workflow_id)}'
            for workflow_id, definition in self._definitions.items()
        )
        messages = [
            {"role": "system", "content": self.ROUTER_SYSTEM_PROMPT},
            {
                "role": "user",
                "content": (
                    f"Configured workflows:\n{workflow_descriptions}\n\n"
                    f"User request: {user_message}"
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
            raise RuntimeError("Workflow router returned invalid JSON.") from exc

        workflow_id = parsed.get("workflow_id")
        reason = parsed.get("reason", "")
        if workflow_id not in self._definitions or not isinstance(reason, str):
            raise RuntimeError("Workflow router returned an invalid workflow.")

        return {"workflow_id": workflow_id, "reason": reason}

    def build_plan(self, workflow_id: str) -> Dict:
        """Translate a configured workflow into an execution plan."""
        definition = self._definitions.get(workflow_id)
        if definition is None:
            raise ValueError(f"Unknown workflow: {workflow_id}")

        requires = definition.get("requires", [])
        if not isinstance(requires, list):
            raise ValueError(
                f"Workflow '{workflow_id}' field 'requires' must be a list."
            )

        return {
            "workflow_id": workflow_id,
            "description": definition.get("description", ""),
            "requires": requires,
            "status": "ready",
        }

    def route_and_plan(self, user_message: str) -> Dict:
        """Route a request and return its validated execution plan."""
        route = self.route(user_message)
        plan = self.build_plan(route["workflow_id"])
        plan["reason"] = route["reason"]
        return plan
