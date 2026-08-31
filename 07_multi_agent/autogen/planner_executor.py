"""AutoGen: Supervisor plans subtasks, delegates to tool-using worker agents."""

from __future__ import annotations

import asyncio
import sys
from importlib import import_module
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[2]))

from autogen_agentchat.agents import AssistantAgent
from autogen_core.tools import FunctionTool

try:
    from ._client import make_client
except ImportError:
    from _client import make_client

spec = import_module("07_multi_agent.spec")
Plan = spec.Plan

calculator = import_module("03_tools.tools.calculator").calculator
query_database = import_module("03_tools.tools.sqlite_tool").query_database


async def _run(question: str, max_turns: int) -> str:
    client = make_client()

    supervisor = AssistantAgent(
        "supervisor",
        model_client=client,
        output_content_type=Plan,
        system_message=(
            "Break the user's question into a short ordered list of subtasks that workers "
            "with a calculator and a read-only database can complete."
        ),
    )
    plan_result = await supervisor.run(task=question)
    plan: Plan = plan_result.messages[-1].content
    tasks = plan.tasks[:max_turns]

    tools = [
        FunctionTool(calculator, description="Evaluate a basic arithmetic expression."),
        FunctionTool(query_database, description="Run a single read-only SELECT query against the labs database."),
    ]
    results: list[str] = []
    for task in tasks:
        worker = AssistantAgent(
            "worker",
            model_client=client,
            tools=tools,
            system_message=(
                "Complete exactly this subtask using the calculator or database tools as "
                "needed, and reply with a short direct result."
            ),
        )
        worker_result = await worker.run(task=task)
        results.append(f"{task} -> {worker_result.messages[-1].content}")

    synthesizer = AssistantAgent(
        "synthesizer", model_client=client, system_message="Combine the worker results below into one final answer."
    )
    synthesis = await synthesizer.run(task="\n".join(results) or "No subtasks were run.")
    return synthesis.messages[-1].content


def run_planner_executor(question: str, max_turns: int = 5) -> str:
    return asyncio.run(_run(question, max_turns))


def main() -> None:
    question = " ".join(sys.argv[1:]) or "How many rows are in employees, times 12?"
    print(run_planner_executor(question))


if __name__ == "__main__":
    main()
