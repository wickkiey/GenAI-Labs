"""PydanticAI: Supervisor plans subtasks, delegates to tool-using worker agents."""

from __future__ import annotations

import sys
from importlib import import_module
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[2]))

from pydantic_ai import Agent
from pydantic_ai.models.openai import OpenAIChatModel
from pydantic_ai.providers.openai import OpenAIProvider

from common.config import settings

spec = import_module("07_multi_agent.spec")
Plan = spec.Plan

calculator = import_module("03_tools.tools.calculator").calculator
query_database = import_module("03_tools.tools.sqlite_tool").query_database


def _model() -> OpenAIChatModel:
    return OpenAIChatModel(
        settings.OLLAMA_MODEL,
        provider=OpenAIProvider(base_url=settings.OLLAMA_BASE_URL, api_key=settings.OLLAMA_API_KEY),
    )


def run_planner_executor(question: str, max_turns: int = 5) -> str:
    supervisor = Agent(
        model=_model(),
        output_type=Plan,
        system_prompt=(
            "You are a Supervisor. Break the user's question into a short ordered list of "
            "subtasks that workers with a calculator and a read-only database can complete."
        ),
    )
    tasks = supervisor.run_sync(question).output.tasks[:max_turns]

    results: list[str] = []
    for task in tasks:
        worker = Agent(
            model=_model(),
            system_prompt=(
                "You are a Worker. Complete exactly this subtask using the calculator or "
                "database tools as needed, and reply with a short direct result."
            ),
        )

        @worker.tool_plain
        def calculator_tool(expression: str) -> str:
            """Evaluate a basic arithmetic expression."""
            return calculator(expression)

        @worker.tool_plain
        def query_database_tool(query: str) -> str:
            """Run a single read-only SELECT query against the labs database."""
            return query_database(query)

        result = worker.run_sync(task).output
        results.append(f"{task} -> {result}")

    synthesizer = Agent(model=_model(), system_prompt="Combine the worker results below into one final answer.")
    return synthesizer.run_sync("\n".join(results) or "No subtasks were run.").output


def main() -> None:
    question = " ".join(sys.argv[1:]) or "How many rows are in employees, times 12?"
    print(run_planner_executor(question))


if __name__ == "__main__":
    main()
