"""Register and execute domain-approved tools safely."""

from __future__ import annotations

from typing import Any, Callable, Dict


class ToolManager:
    """Expose only tools explicitly registered by the application."""

    def __init__(self):
        self._tools: Dict[str, Callable[..., Dict[str, Any]]] = {}

    def register(self, tool_id: str, handler: Callable[..., Dict[str, Any]]) -> None:
        if not tool_id:
            raise ValueError("tool_id must not be empty.")
        if not callable(handler):
            raise TypeError("Tool handler must be callable.")
        self._tools[tool_id] = handler

    @property
    def tool_ids(self) -> list[str]:
        return list(self._tools)

    def execute(self, tool_id: str, **kwargs: Any) -> Dict[str, Any]:
        handler = self._tools.get(tool_id)
        if handler is None:
            raise ValueError(f"Tool is not registered: {tool_id}")

        result = handler(**kwargs)
        if not isinstance(result, dict):
            raise TypeError(f"Tool '{tool_id}' must return a dictionary.")
        return result
