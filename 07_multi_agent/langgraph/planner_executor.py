"""LangGraph: Supervisor plans subtasks (structured output), Executor runs each
via a prebuilt ReAct agent capped at max_turns, then a Synthesizer combines them.
"""

from __future__ import annotations

import sys
from importlib import import_module
from pathlib import Path
from typing import TypedDict

sys.path.append(str(Path(__file__).resolve().parents[2]))

from langchain_core.tools import tool
from langchain_ollama import ChatOllama
from langgraph.graph import END, StateGraph
from langgraph.prebuilt import create_react_agent

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


class PlanExecuteState(TypedDict):
    question: str
    max_turns: int
    tasks: list[str]
    results: list[str]
    final: str


def _plan_node(state: PlanExecuteState) -> PlanExecuteState:
    planner = _llm().with_structured_output(Plan)
    plan: Plan = planner.invoke(
        [
            (
                "system",
                "Break the user's question into a short ordered list of subtasks that "
                "workers with a calculator and a read-only database can complete.",
            ),
            ("user", state["question"]),
        ]
    )
    return {**state, "tasks": plan.tasks[: state["max_turns"]]}


def _execute_node(state: PlanExecuteState) -> PlanExecuteState:
    agent = create_react_agent(
        _llm(),
        [calculator_tool, query_database_tool],
        prompt="Complete exactly this subtask using the calculator or database tools as needed.",
    )
    results = []
    for task in state["tasks"]:
        result = agent.invoke({"messages": [("user", task)]})
        results.append(f"{task} -> {result['messages'][-1].content}")
    return {**state, "results": results}


def _synthesize_node(state: PlanExecuteState) -> PlanExecuteState:
    reply = _llm().invoke(
        [
            ("system", "Combine the worker results below into one final answer."),
            ("user", "\n".join(state["results"]) or "No subtasks were run."),
        ]
    )
    return {**state, "final": reply.content}


def run_planner_executor(question: str, max_turns: int = 5) -> str:
    graph = StateGraph(PlanExecuteState)
    graph.add_node("plan", _plan_node)
    graph.add_node("execute", _execute_node)
    graph.add_node("synthesize", _synthesize_node)
    graph.set_entry_point("plan")
    graph.add_edge("plan", "execute")
    graph.add_edge("execute", "synthesize")
    graph.add_edge("synthesize", END)
    compiled = graph.compile()
    result = compiled.invoke(
        {"question": question, "max_turns": max_turns, "tasks": [], "results": [], "final": ""}
    )
    return result["final"]


def main() -> None:
    question = " ".join(sys.argv[1:]) or "How many rows are in employees, times 12?"
    print(run_planner_executor(question))


if __name__ == "__main__":
    main()
