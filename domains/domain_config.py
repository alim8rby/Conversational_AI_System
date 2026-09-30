"""Domain pack configuration loader.

Keeps business-specific configuration outside the reusable conversation engine.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict


class DomainConfig:
    """Load and expose one domain pack from a JSON configuration file."""

    def __init__(self, path: str):
        self.path = Path(path)
        if not self.path.exists():
            raise FileNotFoundError(f"Domain configuration not found: {self.path}")

        try:
            self.data: Dict[str, Any] = json.loads(
                self.path.read_text(encoding="utf-8")
            )
        except json.JSONDecodeError as exc:
            raise ValueError(f"Invalid domain configuration JSON: {self.path}") from exc

        self._validate()

    def _validate(self) -> None:
        required = {"domain_id", "name", "version", "assistant"}
        missing = required - self.data.keys()
        if missing:
            raise ValueError(
                f"Domain configuration is missing required fields: {sorted(missing)}"
            )

        assistant = self.data["assistant"]
        if not isinstance(assistant, dict):
            raise ValueError("Domain configuration field 'assistant' must be an object.")

        if not assistant.get("name") or not assistant.get("purpose"):
            raise ValueError("Domain assistant must define both 'name' and 'purpose'.")

    @property
    def domain_id(self) -> str:
        return self.data["domain_id"]

    @property
    def name(self) -> str:
        return self.data["name"]

    @property
    def assistant(self) -> Dict[str, Any]:
        return self.data["assistant"]

    @property
    def knowledge_sources(self) -> list[Dict[str, Any]]:
        return self.data.get("knowledge_sources", [])

    @property
    def workflows(self) -> list[str]:
        """Return configured workflow IDs for backwards compatibility."""
        workflows = self.data.get("workflows", [])
        return [
            item if isinstance(item, str) else item.get("id")
            for item in workflows
            if isinstance(item, str) or isinstance(item, dict) and item.get("id")
        ]

    @property
    def workflow_definitions(self) -> list[Dict[str, Any]]:
        """Return full workflow definitions for the execution layer."""
        workflows = self.data.get("workflows", [])
        return [
            {"id": item, "description": item.replace("_", " "), "requires": []}
            if isinstance(item, str)
            else item
            for item in workflows
            if isinstance(item, str) or isinstance(item, dict)
        ]

    @property
    def tools(self) -> list[Dict[str, Any]]:
        return self.data.get("tools", [])

    @property
    def policies(self) -> list[str]:
        return self.data.get("policies", [])
