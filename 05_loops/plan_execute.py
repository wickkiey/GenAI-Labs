from __future__ import annotations

import sys
from importlib import import_module
from pathlib import Path

from pydantic import BaseModel

sys.path.append(str(Path(__file__).resolve().parents[1]))

from common.config import settings
from common.llm import chat

try:
    from .trajectory import Trajectory
except ImportError:
    from trajectory import Trajectory

calculator = import_module("03_tools.tools.calculator").calculator


class Task(BaseModel):
    description: str
    tool: str | None = None
    tool_input: str | None = None


class Plan(BaseModel):
    tasks: list[Task]


def _plan(question: str) -> Plan:
    response = chat(
        [
            {
                "role": "system",
                "content": (
                    "Break the user's question into a short ordered list of tasks. "
                    "Set tool to 'calculator' and tool_input to an arithmetic expression "
                    "for any task that needs arithmetic, otherwise leave tool null."
                ),
            },
            {"role": "user", "content": question},
        ],
        model=settings.OLLAMA_MODEL,
        response_format={
            "type": "json_schema",
            "json_schema": {"name": "plan", "schema": Plan.model_json_schema()},
        },
    )
    return Plan.model_validate_json(response["response_content"])


def _execute_task(task: Task, prior_results: list[str]) -> str:
    if task.tool == "calculator" and task.tool_input:
        return calculator(task.tool_input)
    context = "\n".join(prior_results)
    response = chat(
        [
            {"role": "system", "content": "Answer the sub-task briefly using any prior results given."},
            {"role": "user", "content": f"Prior results:\n{context}\n\nTask: {task.description}"},
        ],
        model=settings.OLLAMA_MODEL,
    )
    return response["response_content"].strip()


def run_plan_execute(question: str) -> Trajectory:
    """Planner produces a list of tasks, Executor runs each one until all are done."""
    trajectory = Trajectory()
    plan = _plan(question)
    results: list[str] = []
    for task in plan.tasks:
        trajectory.iterations += 1
        result = _execute_task(task, results)
        results.append(f"{task.description} -> {result}")
        if task.tool == "calculator":
            trajectory.tool_calls.append(
                {"name": "calculator", "arguments": {"expression": task.tool_input}, "result": result}
            )
        trajectory.steps.append({"task": task.description, "result": result})

    synthesis = chat(
        [
            {"role": "system", "content": "Combine the task results into one final answer."},
            {"role": "user", "content": "\n".join(results)},
        ],
        model=settings.OLLAMA_MODEL,
    )
    trajectory.final = synthesis["response_content"].strip()
    return trajectory
