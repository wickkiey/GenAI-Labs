from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

sys.path.append(str(Path(__file__).resolve().parents[1]))

from common.config import settings
from common.llm import chat

try:
    from .tools import TOOL_REGISTRY
except ImportError:
    from tools import TOOL_REGISTRY


def _assistant_message(response: dict[str, Any]) -> dict[str, Any]:
    message: dict[str, Any] = {"role": "assistant", "content": response["response_content"]}
    if tool_calls := response.get("tool_calls"):
        message["tool_calls"] = [
            {
                "id": call.id,
                "type": call.type,
                "function": {"name": call.function.name, "arguments": call.function.arguments},
            }
            for call in tool_calls
        ]
    return message


class MultiToolAgent:
    """An agent that selects from a registry of tools across bounded rounds."""

    def __init__(
        self,
        system_prompt: str,
        model: str = settings.OLLAMA_MODEL,
        max_iterations: int = 5,
        tool_names: list[str] | None = None,
    ) -> None:
        self.model = model
        self.max_iterations = max_iterations
        self.messages: list[dict[str, Any]] = [{"role": "system", "content": system_prompt}]
        names = tool_names if tool_names is not None else list(TOOL_REGISTRY)
        self.tools = {name: TOOL_REGISTRY[name] for name in names}
        self.tool_calls_made: list[str] = []
        self.iterations = 0

    def _schemas(self) -> list[dict[str, Any]]:
        return [spec.schema for spec in self.tools.values()]

    def _call_model(self) -> dict[str, Any]:
        return chat(self.messages, model=self.model, tools=self._schemas())

    def _dispatch(self, name: str, arguments: dict[str, Any]) -> str:
        spec = self.tools.get(name)
        if spec is None:
            return f"Error: unknown tool '{name}'"
        try:
            return spec.func(**arguments)
        except Exception as error:  # noqa: BLE001 - surfaced to the model as a recoverable error
            return f"Error: tool '{name}' failed ({error})"

    def _run_tool_calls(self, response: dict[str, Any]) -> None:
        self.messages.append(_assistant_message(response))
        for call in response["tool_calls"]:
            self.tool_calls_made.append(call.function.name)
            try:
                arguments = json.loads(call.function.arguments or "{}")
            except json.JSONDecodeError as error:
                result = f"Error: invalid arguments ({error})"
            else:
                result = self._dispatch(call.function.name, arguments)
            self.messages.append({"role": "tool", "tool_call_id": call.id, "content": result})

    def run(self, user_input: str) -> str:
        self.messages.append({"role": "user", "content": user_input})
        for iteration in range(1, self.max_iterations + 1):
            self.iterations = iteration
            response = self._call_model()
            if not response.get("tool_calls"):
                reply = response["response_content"].strip()
                self.messages.append({"role": "assistant", "content": reply})
                return reply
            self._run_tool_calls(response)
        raise RuntimeError(f"agent exceeded its {self.max_iterations}-iteration tool-call limit")
