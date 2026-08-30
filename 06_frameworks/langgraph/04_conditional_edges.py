"""
Phase 7C: LangGraph - 04_conditional_edges.py

Use conditional edges to route between nodes based on state.
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import TypedDict

sys.path.append(str(Path(__file__).resolve().parents[2]))

from langgraph.graph import StateGraph

from common.config import settings


class State(TypedDict):
    """Simple state for routing."""

    value: int
    step: int


def increment_node(state: State) -> State:
    """Increment the value."""
    return {"value": state["value"] + 1, "step": state["step"] + 1}


def double_node(state: State) -> State:
    """Double the value."""
    return {"value": state["value"] * 2, "step": state["step"] + 1}


def route_decision(state: State) -> str:
    """Decide which node to go to based on state."""
    if state["value"] < 10:
        return "increment"
    else:
        return "double"


def main() -> None:
    graph = StateGraph(State)

    # Add nodes
    graph.add_node("increment", increment_node)
    graph.add_node("double", double_node)

    # Set entry point
    graph.set_entry_point("increment")

    # Add conditional edge
    graph.add_conditional_edges(
        "increment",
        route_decision,
        {
            "increment": "increment",
            "double": "double",
        },
    )

    # Set finish point
    graph.add_edge("double", END := "__end__")

    compiled_graph = graph.compile()
    result = compiled_graph.invoke({"value": 1, "step": 0})
    print(f"Final value: {result['value']}, steps: {result['step']}")


if __name__ == "__main__":
    main()
