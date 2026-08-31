"""Phase 9: 06 -- the same orchestrator/subagent pattern shown with a framework.

LangGraph models a subagent as a **compiled subgraph invoked from inside a
parent node** -- the child graph has its own isolated state, and only its
final output is written back into the parent's state, which is the same
isolation guarantee as `subagent_core.Subagent`.
"""
from __future__ import annotations

import sys
from pathlib import Path
from typing import TypedDict

sys.path.append(str(Path(__file__).resolve().parents[1]))

from common.config import settings


class ChildState(TypedDict):
    task: str
    answer: str


class ParentState(TypedDict):
    question: str
    subagent_answer: str


def _build_child_graph():
    from langchain_community.llms.ollama import Ollama
    from langgraph.graph import StateGraph, END

    def solve(state: ChildState) -> ChildState:
        llm = Ollama(base_url=settings.OLLAMA_BASE_URL, model=settings.OLLAMA_MODEL)
        answer = llm.invoke(f"Answer concisely: {state['task']}")
        return {**state, "answer": answer}

    graph = StateGraph(ChildState)
    graph.add_node("solve", solve)
    graph.set_entry_point("solve")
    graph.add_edge("solve", END)
    return graph.compile()


def run_langgraph_subagent(question: str) -> str:
    """Invoke a compiled child graph as an isolated subagent from a parent node."""
    from langgraph.graph import StateGraph, END

    child = _build_child_graph()

    def subagent_node(state: ParentState) -> ParentState:
        child_result = child.invoke({"task": state["question"], "answer": ""})
        return {**state, "subagent_answer": child_result["answer"]}

    parent = StateGraph(ParentState)
    parent.add_node("subagent", subagent_node)
    parent.set_entry_point("subagent")
    parent.add_edge("subagent", END)
    compiled_parent = parent.compile()

    result = compiled_parent.invoke({"question": question, "subagent_answer": ""})
    return result["subagent_answer"]


def main() -> None:
    question = " ".join(sys.argv[1:]) or "What is the capital of France?"
    try:
        answer = run_langgraph_subagent(question)
    except ImportError as error:
        print(f"langgraph/langchain-ollama not installed, skipping framework demo: {error}")
        return
    print(f"[langgraph-subagent] {answer}")


if __name__ == "__main__":
    main()
