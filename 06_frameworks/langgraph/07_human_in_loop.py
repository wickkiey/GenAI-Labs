"""
Phase 7C: LangGraph - 07_human_in_loop.py

Add human intervention nodes to the graph.
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import TypedDict

sys.path.append(str(Path(__file__).resolve().parents[2]))

from langgraph.graph import StateGraph, END


class State(TypedDict):
    """State with decision point."""

    question: str
    answer: str
    approved: bool


def answer_node(state: State) -> State:
    """Generate an answer."""
    return {
        "question": state["question"],
        "answer": f"Answer to: {state['question']}",
        "approved": False,
    }


def human_approval_node(state: State) -> State:
    """Simulate human approval (in real usage, this would be interactive)."""
    # Simulate approval
    approved = True
    return {**state, "approved": approved}


def finalize_node(state: State) -> State:
    """Finalize after approval."""
    return {**state, "answer": f"Approved: {state['answer']}"}


def main() -> None:
    graph = StateGraph(State)

    # Add nodes
    graph.add_node("answer", answer_node)
    graph.add_node("human_approval", human_approval_node)
    graph.add_node("finalize", finalize_node)

    # Set entry point
    graph.set_entry_point("answer")

    # Add edges
    graph.add_edge("answer", "human_approval")
    graph.add_edge("human_approval", "finalize")
    graph.add_edge("finalize", END)

    compiled_graph = graph.compile()
    result = compiled_graph.invoke({
        "question": "What is 2 + 2?",
        "answer": "",
        "approved": False,
    })
    print(f"Final: {result['answer']}")


if __name__ == "__main__":
    main()
