"""
Phase 7C: LangGraph - 02_agent_node.py

Add an LLM-based agent node to the graph.
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import TypedDict

sys.path.append(str(Path(__file__).resolve().parents[2]))

from langchain_community.llms.ollama import Ollama
from langgraph.graph import StateGraph

from common.config import settings


class AgentState(TypedDict):
    """State passed through the graph."""

    input: str
    output: str | None
    step: int


def agent_node(state: AgentState) -> AgentState:
    """LLM-based agent node."""
    llm = Ollama(
        base_url=settings.OLLAMA_BASE_URL,
        model=settings.OLLAMA_MODEL,
        temperature=float(settings.TEMPERATURE),
    )

    response = llm.invoke(state["input"])
    return {
        "input": state["input"],
        "output": response,
        "step": state["step"] + 1,
    }


def main() -> None:
    # Create a state graph
    graph = StateGraph(AgentState)

    # Add nodes
    graph.add_node("agent", agent_node)
    graph.set_entry_point("agent")
    graph.set_finish_point("agent")

    # Compile and run
    compiled_graph = graph.compile()
    result = compiled_graph.invoke({"input": "What is 2 + 2?", "output": None, "step": 0})
    print(f"Output: {result['output']}")


if __name__ == "__main__":
    main()
