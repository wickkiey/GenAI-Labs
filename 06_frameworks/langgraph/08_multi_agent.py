"""
Phase 7C: LangGraph - 08_multi_agent.py

Coordinate multiple agents in a graph.
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import TypedDict

sys.path.append(str(Path(__file__).resolve().parents[2]))

from langchain_community.llms.ollama import Ollama
from langgraph.graph import StateGraph, END

from common.config import settings


class MultiAgentState(TypedDict):
    """Shared state for multiple agents."""

    question: str
    researcher_answer: str
    writer_answer: str


def researcher_node(state: MultiAgentState) -> MultiAgentState:
    """Researcher agent searches for information."""
    llm = Ollama(
        base_url=settings.OLLAMA_BASE_URL,
        model=settings.OLLAMA_MODEL,
        temperature=float(settings.TEMPERATURE),
    )
    
    research = llm.invoke(f"Research: {state['question']}")
    return {**state, "researcher_answer": research}


def writer_node(state: MultiAgentState) -> MultiAgentState:
    """Writer agent synthesizes the answer."""
    llm = Ollama(
        base_url=settings.OLLAMA_BASE_URL,
        model=settings.OLLAMA_MODEL,
        temperature=float(settings.TEMPERATURE),
    )
    
    writing = llm.invoke(f"Based on: {state['researcher_answer']}\n\nWrite: {state['question']}")
    return {**state, "writer_answer": writing}


def main() -> None:
    graph = StateGraph(MultiAgentState)

    # Add nodes
    graph.add_node("researcher", researcher_node)
    graph.add_node("writer", writer_node)

    # Set entry point
    graph.set_entry_point("researcher")

    # Sequential flow
    graph.add_edge("researcher", "writer")
    graph.add_edge("writer", END)

    compiled_graph = graph.compile()
    result = compiled_graph.invoke({
        "question": "What is 1234 * 5678?",
        "researcher_answer": "",
        "writer_answer": "",
    })
    print(f"Final: {result['writer_answer']}")


if __name__ == "__main__":
    main()
