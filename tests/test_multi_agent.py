from __future__ import annotations

import importlib
import json

import httpx
import pytest

from common.config import settings

trajectory_module = importlib.import_module("07_multi_agent.example.trajectory")
handoff_module = importlib.import_module("07_multi_agent.example.researcher_writer.handoff")
supervisor_module = importlib.import_module("07_multi_agent.example.planner_executor.supervisor")
debate_module = importlib.import_module("07_multi_agent.example.debate.debate")
critique_loop_module = importlib.import_module("07_multi_agent.example.critique_loop.critique_loop")


def _require_ollama() -> None:
    try:
        response = httpx.get(f"{settings.OLLAMA_HOST}/api/tags", timeout=2)
    except httpx.TransportError:
        pytest.skip("Ollama is not reachable at configured host")
    if response.status_code != 200:
        pytest.skip("Ollama tag endpoint is unavailable")


def test_trajectory_is_json_serialisable() -> None:
    trajectory = trajectory_module.Trajectory()
    trajectory.steps.append({"agent": "researcher", "output": "fact"})
    trajectory.tool_calls.append({"name": "query_database"})
    trajectory.iterations = 2
    trajectory.final = "done"
    json.dumps(trajectory.to_dict())  # must not raise


def test_researcher_writer_handoff_carries_researched_facts_live() -> None:
    _require_ollama()
    trajectory = handoff_module.run_researcher_writer(
        "Which department has the highest total sales, and by how much?"
    )
    assert trajectory.tool_calls, "the researcher must call at least one database tool"
    assert trajectory.final
    assert "Sales" in trajectory.final or "sales" in trajectory.final.lower()


def test_planner_executor_never_exceeds_max_turns(monkeypatch: pytest.MonkeyPatch) -> None:
    many_tasks = [f"subtask {i}" for i in range(10)]
    monkeypatch.setattr(supervisor_module, "_plan", lambda question: many_tasks)

    class _StubWorker:
        def __init__(self, *args, **kwargs) -> None:
            self.tool_calls_made: list[str] = []

        def run(self, task: str) -> str:
            return f"done: {task}"

    monkeypatch.setattr(supervisor_module, "MultiToolAgent", _StubWorker)
    monkeypatch.setattr(
        supervisor_module, "chat", lambda messages, **kw: {"response_content": "final synthesis"}
    )

    trajectory = supervisor_module.run_planner_executor("unsolvable compound question", max_turns=3)
    assert trajectory.iterations == 3
    assert len(trajectory.steps) == 1 + 3  # 1 supervisor step + 3 worker steps
    assert trajectory.final == "final synthesis"


def test_debate_runs_fixed_rounds_and_judge_picks_a_position(monkeypatch: pytest.MonkeyPatch) -> None:
    responses = iter(
        [
            "Position A: use LangGraph",  # initial A
            "Position B: use PydanticAI",  # initial B
            "Position A restated",
            "Position B restated",
            "B\nB's argument is stronger.",  # judge
        ]
    )
    monkeypatch.setattr(debate_module, "chat", lambda messages, **kw: {"response_content": next(responses)})

    trajectory = debate_module.run_debate("LangGraph or PydanticAI?", max_rounds=1)
    assert trajectory.iterations == 1
    assert trajectory.final == "Position B restated"


def test_critique_loop_fixes_a_deliberately_wrong_first_answer(monkeypatch: pytest.MonkeyPatch) -> None:
    wrong = json.dumps({"expression": "12 * 12", "answer": "100"})
    correct = json.dumps({"expression": "12 * 12", "answer": "144"})
    responses = iter([wrong, correct])
    monkeypatch.setattr(
        critique_loop_module, "chat", lambda messages, **kw: {"response_content": next(responses)}
    )

    trajectory = critique_loop_module.run_critique_loop("What is 12 * 12?", max_rounds=3)
    assert trajectory.iterations == 2
    assert trajectory.final == "144"


def test_critique_loop_never_exceeds_max_rounds_on_persistent_error(monkeypatch: pytest.MonkeyPatch) -> None:
    always_wrong = json.dumps({"expression": "2 + 2", "answer": "5"})
    monkeypatch.setattr(
        critique_loop_module, "chat", lambda messages, **kw: {"response_content": always_wrong}
    )

    trajectory = critique_loop_module.run_critique_loop("What is 2 + 2?", max_rounds=2)
    assert trajectory.iterations == 2
    assert trajectory.final == "5"


def test_planner_executor_handles_compound_question_live() -> None:
    _require_ollama()
    trajectory = supervisor_module.run_planner_executor(
        "How many employees are in Sales, and what is that number times 12?"
    )
    assert trajectory.final
    assert trajectory.iterations >= 1


def test_debate_terminates_with_live_model() -> None:
    _require_ollama()
    trajectory = debate_module.run_debate("Is tabs or spaces better for Python?", max_rounds=1)
    assert trajectory.final
    assert trajectory.iterations == 1
