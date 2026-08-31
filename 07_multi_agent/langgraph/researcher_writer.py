"""LangGraph: Researcher (prebuilt ReAct agent w/ tools) -> Writer (no tools),
wired together as a 2-node StateGraph.
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

list_tables = import_module("03_tools.tools.sqlite_tool").list_tables
query_database = import_module("03_tools.tools.sqlite_tool").query_database


@tool
def list_tables_tool() -> str:
    """List all table names in the labs database."""
    return list_tables()


@tool
def query_database_tool(query: str) -> str:
    """Run a single read-only SELECT query against the labs database."""
    return query_database(query)


def _llm() -> ChatOllama:
    return ChatOllama(base_url=settings.OLLAMA_HOST, model=settings.OLLAMA_MODEL, temperature=float(settings.TEMPERATURE))


class HandoffState(TypedDict):
    question: str
    research_notes: str
    final: str


def _researcher_node(state: HandoffState) -> HandoffState:
    agent = create_react_agent(
        _llm(),
        [list_tables_tool, query_database_tool],
        prompt=(
            "Use the list_tables_tool and query_database_tool tools to find the exact facts "
            "needed to answer the question. Reply with a short bullet list of raw facts only."
        ),
    )
    result = agent.invoke({"messages": [("user", state["question"])]})
    return {**state, "research_notes": result["messages"][-1].content}


def _writer_node(state: HandoffState) -> HandoffState:
    reply = _llm().invoke(
        [
            (
                "system",
                "Using ONLY the facts provided below, write a 2-3 sentence answer to the "
                "question. Do not invent any facts and do not use any tools.",
            ),
            ("user", f"Question: {state['question']}\n\nResearcher facts:\n{state['research_notes']}"),
        ]
    )
    return {**state, "final": reply.content}


def run_researcher_writer(question: str) -> str:
    graph = StateGraph(HandoffState)
    graph.add_node("researcher", _researcher_node)
    graph.add_node("writer", _writer_node)
    graph.set_entry_point("researcher")
    graph.add_edge("researcher", "writer")
    graph.add_edge("writer", END)
    compiled = graph.compile()
    result = compiled.invoke({"question": question, "research_notes": "", "final": ""})
    return result["final"]


def main() -> None:
    question = " ".join(sys.argv[1:]) or "Which department has the highest total sales, and by how much?"
    print(run_researcher_writer(question))


if __name__ == "__main__":
    main()
