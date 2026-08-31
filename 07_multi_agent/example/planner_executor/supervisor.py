"""Supervisor/worker pattern: a supervisor plans a bounded list of subtasks, then
delegates each one to a tool-using worker agent. The supervisor never runs more
than max_turns worker turns, even if it plans more subtasks than that.
"""

from __future__ import annotations

import sys
from importlib import import_module
from pathlib import Path

from pydantic import BaseModel

sys.path.append(str(Path(__file__).resolve().parents[2]))
sys.path.append(str(Path(__file__).resolve().parents[1]))

from common.config import settings
from common.llm import chat

try:
    from ..trajectory import Trajectory
except ImportError:
    from trajectory import Trajectory

MultiToolAgent = import_module("03_tools.tool_agent").MultiToolAgent

WORKER_TOOLS = ["calculator", "list_tables", "describe_table", "query_database"]


class Plan(BaseModel):
    tasks: list[str]


def _plan(question: str) -> list[str]:
    response = chat(
        [
            {
                "role": "system",
                "content": (
                    "You are a Supervisor. Break the user's question into a short "
                    "ordered list of subtasks that workers with a calculator and a "
                    "read-only database can complete."
                ),
            },
            {"role": "user", "content": question},
        ],
        model=settings.OLLAMA_MODEL,
        response_format={"type": "json_schema", "json_schema": {"name": "plan", "schema": Plan.model_json_schema()}},
    )
    try:
        return Plan.model_validate_json(response["response_content"]).tasks
    except ValueError:
        return [question]


def run_planner_executor(question: str, max_turns: int = 5) -> Trajectory:
    """Supervisor delegates subtasks to worker agents, capped at max_turns."""
    trajectory = Trajectory()
    tasks = _plan(question)[:max_turns]
    trajectory.steps.append({"agent": "supervisor", "plan": tasks})

    results: list[str] = []
    turns = 0
    for task in tasks:
        if turns >= max_turns:
            break
        turns += 1
        trajectory.iterations = turns
        worker = MultiToolAgent(
            "You are a Worker. Complete exactly this subtask using the calculator "
            "or database tools as needed, and reply with a short direct result.",
            model=settings.OLLAMA_MODEL,
            tool_names=WORKER_TOOLS,
        )
        result = worker.run(task)
        results.append(f"{task} -> {result}")
        trajectory.tool_calls.extend({"name": name} for name in worker.tool_calls_made)
        trajectory.steps.append({"agent": "worker", "task": task, "result": result})

    synthesis = chat(
        [
            {"role": "system", "content": "Combine the worker results below into one final answer."},
            {"role": "user", "content": "\n".join(results) or "No subtasks were run."},
        ],
        model=settings.OLLAMA_MODEL,
    )["response_content"].strip()
    trajectory.final = synthesis
    return trajectory


def main() -> None:
    question = " ".join(sys.argv[1:]) or "How many rows are in employees, times 12?"
    trajectory = run_planner_executor(question)
    print(trajectory.final)
    print(f"turns: {trajectory.iterations}")


if __name__ == "__main__":
    main()
