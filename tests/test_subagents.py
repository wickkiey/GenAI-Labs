from __future__ import annotations

import importlib
import json
from types import SimpleNamespace

import pytest

subagent_core = importlib.import_module("08_subagents.subagent_core")
specialized_module = importlib.import_module("08_subagents.03_specialized_subagents")
recursive_module = importlib.import_module("08_subagents.05_recursive_subagents")


def _delegate_call(call_id: str, subtask: str) -> SimpleNamespace:
    return SimpleNamespace(
        id=call_id,
        type="function",
        function=SimpleNamespace(name="delegate", arguments=json.dumps({"subtask": subtask})),
    )


def test_spawn_subagent_returns_result_without_leaking_history(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(
        subagent_core, "chat", lambda messages, **kw: {"response_content": "the answer is 42"}
    )
    result = subagent_core.spawn_subagent(name="helper", system_prompt="Be helpful.", task="what is it?")
    assert isinstance(result, subagent_core.SubagentResult)
    assert result.output == "the answer is 42"
    assert result.name == "helper"


def test_subagent_history_is_isolated_between_instances(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(subagent_core, "chat", lambda messages, **kw: {"response_content": "ok"})
    agent_a = subagent_core.Subagent(name="a", system_prompt="A")
    agent_b = subagent_core.Subagent(name="b", system_prompt="B")
    agent_a.run("task for a")
    assert len(agent_b.messages) == 1  # only its own system prompt, untouched by agent_a's run
    assert all("task for a" not in str(m) for m in agent_b.messages)


@pytest.mark.parametrize(
    "task,expected_role",
    [
        ("How many employees are in Sales?", "researcher"),
        ("What's in notes.txt?", "coder"),
        ("Find documents mentioning vector databases", "researcher"),
        ("List files in the sandbox", "coder"),
        ("Hello, who are you?", "reviewer"),
    ],
)
def test_specialized_subagent_routing(task: str, expected_role: str) -> None:
    assert specialized_module.classify(task) == expected_role


def test_recursive_subagent_never_exceeds_max_depth(monkeypatch: pytest.MonkeyPatch) -> None:
    call_count = {"n": 0}

    def _always_delegate(messages, **kwargs):
        call_count["n"] += 1
        if kwargs.get("tools"):
            return {
                "response_content": "",
                "tool_calls": [_delegate_call(f"call-{call_count['n']}", "recurse forever")],
            }
        return {"response_content": "no more delegation possible, final answer"}

    monkeypatch.setattr(recursive_module, "chat", _always_delegate)
    result = recursive_module.run_recursive_subagent("recurse forever", max_depth=2)

    def _max_depth(node: recursive_module.RecursiveResult) -> int:
        if not node.delegations:
            return node.depth
        return max(_max_depth(child) for child in node.delegations)

    assert _max_depth(result) <= 2


def test_parallel_subagents_preserve_request_order(monkeypatch: pytest.MonkeyPatch) -> None:
    parallel_module = importlib.import_module("08_subagents.02_parallel_subagents")

    def _fake_spawn(name, system_prompt, task, **kwargs):
        # Reverse-alphabetical tasks "finish" out of order but results must stay in request order.
        return subagent_core.SubagentResult(name=name, task=task, output=f"answer to {task}")

    monkeypatch.setattr(parallel_module, "spawn_subagent", _fake_spawn)
    tasks = ["task-1", "task-2", "task-3"]
    results = __import__("asyncio").run(parallel_module.run_parallel(tasks))
    assert [r.task for r in results] == tasks
