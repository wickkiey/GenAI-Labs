"""Strands: Supervisor plans subtasks (structured output), Worker executes each
(capped at max_turns) with tools, then a Synthesizer combines the results.
"""

from __future__ import annotations

import sys
from importlib import import_module
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[2]))

from strands import Agent, tool
from strands.models.ollama import OllamaModel

from common.config import settings

spec = import_module("07_multi_agent.spec")
Plan = spec.Plan

calculator = import_module("03_tools.tools.calculator").calculator
query_database = import_module("03_tools.tools.sqlite_tool").query_database


@tool
def calculator_tool(expression: str) -> str:
    """Evaluate a basic arithmetic expression."""
    return calculator(expression)


@tool
def query_database_tool(query: str) -> str:
    """Run a single read-only SELECT query against the labs database."""
    return query_database(query)


def _model() -> OllamaModel:
    return OllamaModel(host=settings.OLLAMA_HOST, model_id=settings.OLLAMA_MODEL)


def run_planner_executor(question: str, max_turns: int = 5) -> str:
    supervisor = Agent(
        model=_model(),
        system_prompt=(
            "Break the user's question into a short ordered list of subtasks that workers "
            "with a calculator and a read-only database can complete."
        ),
    )
    plan: Plan = supervisor.structured_output(Plan, question)
    tasks = plan.tasks[:max_turns]

    results: list[str] = []
    for task in tasks:
        worker = Agent(
            model=_model(),
            tools=[calculator_tool, query_database_tool],
            system_prompt=(
                "Complete exactly this subtask using the calculator or database tools as "
                "needed, and reply with a short direct result."
            ),
        )
        results.append(f"{task} -> {worker(task)}")

    synthesizer = Agent(model=_model(), system_prompt="Combine the worker results below into one final answer.")
    return str(synthesizer("\n".join(results) or "No subtasks were run."))


def main() -> None:
    question = " ".join(sys.argv[1:]) or "How many rows are in employees, times 12?"
    print(run_planner_executor(question))


if __name__ == "__main__":
    main()
