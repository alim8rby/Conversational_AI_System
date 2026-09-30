"""Register, validate, and execute domain-approved tools safely."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable, Dict


ToolHandler = Callable[..., Dict[str, Any]]
InputExtractor = Callable[[str], Dict[str, Any]]


@dataclass(frozen=True)
class ToolDefinition:
    """Describe a tool's execution contract."""

    tool_id: str
    handler: ToolHandler
    required_inputs: tuple[str, ...] = ()
    input_extractor: InputExtractor | None = None
    description: str = ""


class ToolManager:
    """Expose only tools explicitly registered by the application."""

    def __init__(self):
        self._tools: Dict[str, ToolDefinition] = {}

    def register(
        self,
        tool_id: str,
        handler: ToolHandler,
        *,
        required_inputs: tuple[str, ...] = (),
        input_extractor: InputExtractor | None = None,
        description: str = "",
    ) -> None:
        if not tool_id:
            raise ValueError("tool_id must not be empty.")
        if not callable(handler):
            raise TypeError("Tool handler must be callable.")
        if input_extractor is not None and not callable(input_extractor):
            raise TypeError("Input extractor must be callable.")
        self._tools[tool_id] = ToolDefinition(
            tool_id=tool_id,
            handler=handler,
            required_inputs=required_inputs,
            input_extractor=input_extractor,
            description=description,
        )

    @property
    def tool_ids(self) -> list[str]:
        return list(self._tools)

    def get_definition(self, tool_id: str) -> ToolDefinition:
        definition = self._tools.get(tool_id)
        if definition is None:
            raise ValueError(f"Tool is not registered: {tool_id}")
        return definition

    def prepare_inputs(self, tool_id: str, user_message: str) -> Dict[str, Any]:
        """Extract tool inputs from the user's message."""
        definition = self.get_definition(tool_id)
        if definition.input_extractor is None:
            return {}
        inputs = definition.input_extractor(user_message)
        if not isinstance(inputs, dict):
            raise TypeError(f"Input extractor for '{tool_id}' must return a dictionary.")
        return inputs

    def missing_inputs(self, tool_id: str, inputs: Dict[str, Any]) -> list[str]:
        """Return required inputs that are missing or empty."""
        definition = self.get_definition(tool_id)
        return [
            name
            for name in definition.required_inputs
            if inputs.get(name) in (None, "")
        ]

    def execute(self, tool_id: str, **kwargs: Any) -> Dict[str, Any]:
        definition = self.get_definition(tool_id)
        missing = self.missing_inputs(tool_id, kwargs)
        if missing:
            raise ValueError(
                f"Missing required input for '{tool_id}': {', '.join(missing)}"
            )

        result = definition.handler(**kwargs)
        if not isinstance(result, dict):
            raise TypeError(f"Tool '{tool_id}' must return a dictionary.")
        return result

    def prepare_and_execute(
        self,
        tool_id: str,
        user_message: str,
    ) -> Dict[str, Any]:
        """Prepare inputs and execute a single tool."""
        inputs = self.prepare_inputs(tool_id, user_message)
        missing = self.missing_inputs(tool_id, inputs)
        if missing:
            return {
                "tool_id": tool_id,
                "status": "requires_input",
                "missing_inputs": missing,
                "inputs": inputs,
            }

        result = self.execute(tool_id, **inputs)
        return {
            "tool_id": tool_id,
            "status": "executed",
            "inputs": inputs,
            "result": result,
        }

    def execute_required(
        self,
        tool_ids: list[str],
        user_message: str,
    ) -> list[Dict[str, Any]]:
        """Execute all registered tools required by a workflow, in order."""
        executions = []
        for tool_id in tool_ids:
            executions.append(self.prepare_and_execute(tool_id, user_message))
        return executions
