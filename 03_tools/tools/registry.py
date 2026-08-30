from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from typing import Any


@dataclass
class ToolSpec:
    schema: dict[str, Any]
    func: Callable[..., str]


TOOL_REGISTRY: dict[str, ToolSpec] = {}


def register_tool(schema: dict[str, Any]) -> Callable[[Callable[..., str]], Callable[..., str]]:
    """Register a function under its OpenAI-style tool schema name."""

    def decorator(func: Callable[..., str]) -> Callable[..., str]:
        TOOL_REGISTRY[schema["function"]["name"]] = ToolSpec(schema=schema, func=func)
        return func

    return decorator
