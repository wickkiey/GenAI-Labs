from __future__ import annotations

import json
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

sys.path.append(str(Path(__file__).resolve().parents[1]))

from common.config import settings
from common.llm import chat


@dataclass
class SubagentResult:
    """What a subagent hands back to its parent -- a result, never its raw history."""

    name: str
    task: str
    output: str
    depth: int = 0
    tool_calls: list[str] = field(default_factory=list)


class Subagent:
    """A bounded, single-purpose agent with its own isolated message history.

    Unlike the peer agents in `07_multi_agent/`, a `Subagent` is spawned by a
    parent for one task, returns a single `SubagentResult`, and is then
    discarded -- its `messages` history never becomes part of the parent's
    conversation.
    """

    def __init__(
        self,
        name: str,
        system_prompt: str,
        model: str = settings.OLLAMA_MODEL,
        tools: dict[str, Any] | None = None,
        max_iterations: int = 5,
    ) -> None:
        self.name = name
        self.model = model
        self.tools = tools or {}
        self.max_iterations = max_iterations
        self.messages: list[dict[str, Any]] = [{"role": "system", "content": system_prompt}]
        self.tool_calls_made: list[str] = []

    def _schemas(self) -> list[dict[str, Any]]:
        return [spec.schema for spec in self.tools.values()]

    def _call_model(self) -> dict[str, Any]:
        if self.tools:
            return chat(self.messages, model=self.model, tools=self._schemas())
        return chat(self.messages, model=self.model)

    def _dispatch(self, tool_name: str, arguments: dict[str, Any]) -> str:
        spec = self.tools.get(tool_name)
        if spec is None:
            return f"Error: unknown tool '{tool_name}'"
        try:
            return spec.func(**arguments)
        except Exception as error:  # noqa: BLE001 - surfaced to the model as a recoverable error
            return f"Error: tool '{tool_name}' failed ({error})"

    def _run_tool_calls(self, response: dict[str, Any]) -> None:
        message: dict[str, Any] = {"role": "assistant", "content": response["response_content"]}
        tool_calls = response.get("tool_calls") or []
        if tool_calls:
            message["tool_calls"] = [
                {
                    "id": call.id,
                    "type": call.type,
                    "function": {"name": call.function.name, "arguments": call.function.arguments},
                }
                for call in tool_calls
            ]
        self.messages.append(message)
        for call in tool_calls:
            self.tool_calls_made.append(call.function.name)
            try:
                arguments = json.loads(call.function.arguments or "{}")
            except json.JSONDecodeError as error:
                result = f"Error: invalid arguments ({error})"
            else:
                result = self._dispatch(call.function.name, arguments)
            self.messages.append({"role": "tool", "tool_call_id": call.id, "content": result})

    def run(self, task: str, depth: int = 0) -> SubagentResult:
        self.messages.append({"role": "user", "content": task})
        for _ in range(1, self.max_iterations + 1):
            response = self._call_model()
            if not response.get("tool_calls"):
                reply = response["response_content"].strip()
                self.messages.append({"role": "assistant", "content": reply})
                return SubagentResult(
                    name=self.name, task=task, output=reply, depth=depth, tool_calls=self.tool_calls_made
                )
            self._run_tool_calls(response)
        raise RuntimeError(f"subagent '{self.name}' exceeded its {self.max_iterations}-iteration limit")


def spawn_subagent(
    name: str,
    system_prompt: str,
    task: str,
    depth: int = 0,
    **kwargs: Any,
) -> SubagentResult:
    """Create a brand-new, isolated `Subagent` and run it once.

    This is the simplest delegation primitive: the parent never sees the
    child's intermediate messages, only the returned `SubagentResult`.
    """
    agent = Subagent(name=name, system_prompt=system_prompt, **kwargs)
    return agent.run(task, depth=depth)
