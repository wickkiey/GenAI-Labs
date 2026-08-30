from __future__ import annotations

import importlib
import json

import httpx
import pytest

from common.config import settings

trajectory_module = importlib.import_module("05_loops.trajectory")
react_module = importlib.import_module("05_loops.react")
plan_execute_module = importlib.import_module("05_loops.plan_execute")
reflection_module = importlib.import_module("05_loops.reflection")
retry_module = importlib.import_module("05_loops.retry")
verification_module = importlib.import_module("05_loops.verification")
critique_loop_module = importlib.import_module("05_loops.critique_loop")


def _require_ollama() -> None:
    try:
        response = httpx.get(f"{settings.OLLAMA_HOST}/api/tags", timeout=2)
    except httpx.TransportError:
        pytest.skip("Ollama is not reachable at configured host")
    if response.status_code != 200:
        pytest.skip("Ollama tag endpoint is unavailable")


def _fake_chat_always(text: str):
    def _chat(messages, **kwargs):
        return {"response_content": text}

    return _chat


def test_trajectory_is_json_serialisable() -> None:
    trajectory = trajectory_module.Trajectory()
    trajectory.steps.append({"a": 1})
    trajectory.tool_calls.append({"name": "calculator", "arguments": {"expression": "1+1"}, "result": "2"})
    trajectory.iterations = 1
    trajectory.final = "done"
    json.dumps(trajectory.to_dict())  # must not raise


def test_react_never_exceeds_max_steps_on_unsolvable_task(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(
        react_module, "chat", _fake_chat_always("Thought: still thinking\nAction: calculator[1+1]")
    )
    trajectory = react_module.run_react("unsolvable", max_steps=3)
    assert trajectory.iterations == 3
    assert len(trajectory.tool_calls) == 3


def test_reflection_never_exceeds_max_rounds_on_unsolvable_task(monkeypatch: pytest.MonkeyPatch) -> None:
    responses = iter(["initial answer"] + ["Missing details, try again"] * 10)
    monkeypatch.setattr(reflection_module, "chat", lambda messages, **kw: {"response_content": next(responses)})
    trajectory = reflection_module.run_reflection("unsolvable", max_rounds=3)
    assert trajectory.iterations == 3


def test_reflection_round_two_answer_differs_from_round_one(monkeypatch: pytest.MonkeyPatch) -> None:
    responses = iter(["answer v1", "FAIL: needs more detail", "answer v2 with more detail", "OK"])
    monkeypatch.setattr(reflection_module, "chat", lambda messages, **kw: {"response_content": next(responses)})
    trajectory = reflection_module.run_reflection("question", max_rounds=3)
    revised = [s for s in trajectory.steps if "revised_answer" in s]
    assert revised
    assert revised[0]["revised_answer"] != "answer v1"


def test_verification_never_exceeds_max_rounds_on_unsolvable_task(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(verification_module, "chat", _fake_chat_always("FAIL: always wrong"))
    trajectory = verification_module.run_verification("unsolvable", max_rounds=3)
    assert trajectory.iterations == 3


def test_critique_loop_never_exceeds_max_rounds_on_disagreement(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(critique_loop_module, "chat", _fake_chat_always("I disagree, here's why"))
    trajectory = critique_loop_module.run_critique_loop("unsolvable", max_rounds=2)
    assert trajectory.iterations == 2


def test_retry_recovers_from_a_tool_that_fails_twice() -> None:
    calls = {"count": 0}

    def flaky_action(previous_error: str | None) -> str:
        calls["count"] += 1
        if calls["count"] < 3:
            raise RuntimeError(f"attempt {calls['count']} failed")
        return "success"

    trajectory = retry_module.run_retry(flaky_action, max_attempts=3)
    assert trajectory.final == "success"
    assert trajectory.iterations == 3
    assert calls["count"] == 3


def test_retry_gives_up_after_max_attempts() -> None:
    def always_fails(previous_error: str | None) -> str:
        raise RuntimeError("nope")

    trajectory = retry_module.run_retry(always_fails, max_attempts=2)
    assert trajectory.iterations == 2
    assert "failed after 2 attempts" in trajectory.final


def test_plan_execute_produces_multiple_tasks_for_compound_question() -> None:
    _require_ollama()
    trajectory = plan_execute_module.run_plan_execute("What is 15 * 4, and separately what is 100 / 5?")
    assert trajectory.iterations >= 2


def test_react_solves_arithmetic_with_live_model() -> None:
    _require_ollama()
    trajectory = react_module.run_react("What is 1234 * 5678?", max_steps=4)
    assert trajectory.final
