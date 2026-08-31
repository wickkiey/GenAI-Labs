"""CrewAI: Supervisor plans subtasks (parsed from free text), a Worker agent
executes each one (capped at max_turns) via a sequential Crew per task, then a
Synthesizer combines the results.
"""

from __future__ import annotations

import sys
from importlib import import_module
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[2]))

from crewai import LLM, Agent, Crew, Process, Task
from crewai.tools import tool

from common.config import settings

calculator = import_module("03_tools.tools.calculator").calculator
query_database = import_module("03_tools.tools.sqlite_tool").query_database


@tool("Calculator")
def calculator_tool(expression: str) -> str:
    """Evaluate a basic arithmetic expression."""
    return calculator(expression)


@tool("Query Database")
def query_database_tool(query: str) -> str:
    """Run a single read-only SELECT query against the labs database."""
    return query_database(query)


def _llm() -> LLM:
    return LLM(model=f"ollama/{settings.OLLAMA_MODEL}", base_url=settings.OLLAMA_HOST, temperature=float(settings.TEMPERATURE))


def _plan(llm: LLM, question: str) -> list[str]:
    planner = Agent(
        role="Supervisor",
        goal="Break the question into an ordered list of short subtasks.",
        backstory="A project manager who splits work into the smallest useful steps.",
        llm=llm,
    )
    task = Task(
        description=(
            f"Break this question into a short ordered list of subtasks that a worker with "
            f"a calculator and a read-only database can complete: {question}\n"
            "Reply with one subtask per line, no numbering or extra commentary."
        ),
        expected_output="One subtask per line.",
        agent=planner,
    )
    crew = Crew(agents=[planner], tasks=[task], process=Process.sequential)
    raw = str(crew.kickoff())
    return [line.strip("-* ") for line in raw.splitlines() if line.strip()]


def run_planner_executor(question: str, max_turns: int = 5) -> str:
    llm = _llm()
    tasks = _plan(llm, question)[:max_turns]

    worker = Agent(
        role="Worker",
        goal="Complete exactly the subtask given using the calculator or database tools as needed.",
        backstory="A careful executor who reports short, direct results.",
        tools=[calculator_tool, query_database_tool],
        llm=llm,
    )
    results: list[str] = []
    for subtask in tasks:
        crew_task = Task(description=subtask, expected_output="A short direct result.", agent=worker)
        crew = Crew(agents=[worker], tasks=[crew_task], process=Process.sequential)
        results.append(f"{subtask} -> {crew.kickoff()}")

    synthesizer = Agent(
        role="Synthesizer",
        goal="Combine worker results into one final answer.",
        backstory="A summariser who never drops a number.",
        llm=llm,
    )
    synth_task = Task(
        description="Combine these worker results into one final answer:\n" + ("\n".join(results) or "No subtasks were run."),
        expected_output="One final answer.",
        agent=synthesizer,
    )
    crew = Crew(agents=[synthesizer], tasks=[synth_task], process=Process.sequential)
    return str(crew.kickoff())


def main() -> None:
    question = " ".join(sys.argv[1:]) or "How many rows are in employees, times 12?"
    print(run_planner_executor(question))


if __name__ == "__main__":
    main()
