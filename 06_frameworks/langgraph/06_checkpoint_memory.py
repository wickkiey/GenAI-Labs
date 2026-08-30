"""
Phase 7C: LangGraph - 06_checkpoint_memory.py

Persist graph state using checkpoints for resumability.
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import TypedDict

sys.path.append(str(Path(__file__).resolve().parents[2]))

from langgraph.graph import StateGraph, END
from langgraph.checkpoint.sqlite import SqliteSaver

from common.config import settings


class State(TypedDict):
    """Simple state."""

    value: int
    step: int


def increment_node(state: State) -> State:
    """Increment the value."""
    return {"value": state["value"] + 1, "step": state["step"] + 1}


def main() -> None:
    # Create a checkpoint saver
    checkpoint_dir = Path(__file__).resolve().parent / ".checkpoints"
    checkpoint_dir.mkdir(exist_ok=True)
    checkpointer = SqliteSaver(str(checkpoint_dir / "state.db"))

    graph = StateGraph(State)
    graph.add_node("increment", increment_node)
    graph.set_entry_point("increment")
    graph.add_edge("increment", END)

    # Compile with checkpointer for persistence
    compiled_graph = graph.compile(checkpointer=checkpointer)

    # Run with a thread_id for checkpoint grouping
    thread_id = "test_thread_1"
    config = {"configurable": {"thread_id": thread_id}}

    result = compiled_graph.invoke(
        {"value": 0, "step": 0},
        config,
    )
    print(f"After first run: {result}")

    # Resume from checkpoint
    result2 = compiled_graph.invoke(
        {"value": result["value"], "step": result["step"]},
        config,
    )
    print(f"After resume: {result2}")


if __name__ == "__main__":
    main()
