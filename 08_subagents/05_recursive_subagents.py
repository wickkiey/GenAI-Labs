"""Phase 9: 05 -- a subagent may itself spawn a subagent, bounded by max_depth."""
from __future__ import annotations

import json
import sys
from dataclasses import dataclass, field
from typing import Any

try:
    from .subagent_core import SubagentResult
except ImportError:
    from subagent_core import SubagentResult

from common.config import settings
from common.llm import chat

DELEGATE_SCHEMA = {
    "type": "function",
    "function": {
        "name": "delegate",
        "description": "Delegate a well-defined sub-task to a fresh helper subagent and get its answer back.",
        "parameters": {
            "type": "object",
            "properties": {"subtask": {"type": "string", "description": "The sub-task to delegate."}},
            "required": ["subtask"],
            "additionalProperties": False,
        },
    },
}

SYSTEM_PROMPT = (
    "You solve tasks step by step. If a task has an independent, well-defined "
    "part that would be easier to solve on its own, call `delegate` with that "
    "sub-task instead of solving it yourself. Otherwise answer directly."
)


@dataclass
class RecursiveResult(SubagentResult):
    delegations: list["RecursiveResult"] = field(default_factory=list)


def run_recursive_subagent(task: str, max_depth: int = 2, depth: int = 0) -> RecursiveResult:
    """Run a subagent that may recursively delegate, never exceeding `max_depth`."""
    messages: list[dict[str, Any]] = [{"role": "system", "content": SYSTEM_PROMPT}]
    messages.append({"role": "user", "content": task})
    tools = [] if depth >= max_depth else [DELEGATE_SCHEMA]
    delegations: list[RecursiveResult] = []

    for _ in range(5):
        response = chat(messages, model=settings.OLLAMA_MODEL, tools=tools) if tools else chat(
            messages, model=settings.OLLAMA_MODEL
        )
        tool_calls = response.get("tool_calls") or []
        if not tool_calls:
            reply = response["response_content"].strip()
            return RecursiveResult(
                name=f"subagent-depth{depth}", task=task, output=reply, depth=depth, delegations=delegations
            )

        message: dict[str, Any] = {"role": "assistant", "content": response["response_content"]}
        message["tool_calls"] = [
            {"id": c.id, "type": c.type, "function": {"name": c.function.name, "arguments": c.function.arguments}}
            for c in tool_calls
        ]
        messages.append(message)
        for call in tool_calls:
            try:
                arguments = json.loads(call.function.arguments or "{}")
                subtask = arguments["subtask"]
            except (json.JSONDecodeError, KeyError) as error:
                result_text = f"Error: invalid delegate arguments ({error})"
            else:
                child = run_recursive_subagent(subtask, max_depth=max_depth, depth=depth + 1)
                delegations.append(child)
                result_text = child.output
            messages.append({"role": "tool", "tool_call_id": call.id, "content": result_text})

    return RecursiveResult(
        name=f"subagent-depth{depth}",
        task=task,
        output="(iteration limit reached)",
        depth=depth,
        delegations=delegations,
    )


def main() -> None:
    task = " ".join(sys.argv[1:]) or (
        "Compute 12 * 8, then separately find the capital of France, then combine both into one sentence."
    )
    result = run_recursive_subagent(task, max_depth=2)
    print(result.output)
    print(f"delegations made: {len(result.delegations)}")


if __name__ == "__main__":
    main()
