"""Load domain-declared tool implementations into the ToolManager."""

from __future__ import annotations

import importlib
from typing import Any

from tools.tool_manager import ToolManager


def _load_callable(reference: str):
    """Load a callable from a module reference such as 'pkg.module:function'."""
    try:
        module_name, function_name = reference.split(":", 1)
    except ValueError as exc:
        raise ValueError(
            f"Invalid callable reference '{reference}'. Expected 'module:function'."
        ) from exc

    module = importlib.import_module(module_name)
    callable_object = getattr(module, function_name, None)
    if not callable(callable_object):
        raise TypeError(f"Configured callable is not callable: {reference}")
    return callable_object


def register_domain_tools(manager: ToolManager, definitions: list[dict[str, Any]]) -> None:
    """Register the tools declared by a domain configuration."""
    for definition in definitions:
        tool_id = definition.get("id")
        handler_ref = definition.get("handler")
        extractor_ref = definition.get("input_extractor")

        if not tool_id or not handler_ref:
            raise ValueError("Each domain tool must define 'id' and 'handler'.")

        handler = _load_callable(handler_ref)
        extractor = _load_callable(extractor_ref) if extractor_ref else None

        manager.register(
            tool_id,
            handler,
            required_inputs=tuple(definition.get("required_inputs", [])),
            input_extractor=extractor,
            description=definition.get("description", ""),
        )
