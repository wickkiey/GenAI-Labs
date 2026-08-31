"""LangChain: Supervisor plans subtasks (structured output), Executor runs each
via an AgentExecutor capped at max_turns, then a Synthesizer combines them.
"""

from __future__ import annotations

import sys
from importlib import import_module
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[2]))

from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.tools import tool
from langchain_ollama import ChatOllama

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


def _llm() -> ChatOllama:
    return ChatOllama(base_url=settings.OLLAMA_HOST, model=settings.OLLAMA_MODEL, temperature=float(settings.TEMPERATURE))


def run_planner_executor(question: str, max_turns: int = 5) -> str:
    llm = _llm()
    planner = llm.with_structured_output(Plan)
    plan: Plan = planner.invoke(
        [
            (
                "system",
                "Break the user's question into a short ordered list of subtasks that "
                "workers with a calculator and a read-only database can complete.",
            ),
            ("user", question),
        ]
    )
    tasks = plan.tasks[:max_turns]

    tools = [calculator_tool, query_database_tool]
    prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                "Complete exactly this subtask using the calculator or database tools as "
                "needed, and reply with a short direct result.",
            ),
            ("user", "{input}"),
            ("placeholder", "{agent_scratchpad}"),
        ]
    )
    agent = create_tool_calling_agent(llm, tools, prompt)
    executor = AgentExecutor(agent=agent, tools=tools, max_iterations=6)

    results = [f"{task} -> {executor.invoke({'input': task})['output']}" for task in tasks]

    synthesis = llm.invoke(
        [
            ("system", "Combine the worker results below into one final answer."),
            ("user", "\n".join(results) or "No subtasks were run."),
        ]
    )
    return synthesis.content


def main() -> None:
    question = " ".join(sys.argv[1:]) or "How many rows are in employees, times 12?"
    print(run_planner_executor(question))


if __name__ == "__main__":
    main()
