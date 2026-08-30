"""
Phase 7C: LangGraph - 01_basic_graph.py

Create a basic graph with nodes and edges.
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[2]))

from langgraph.graph import Graph
from langchain_community.llms.ollama import Ollama

from common.config import settings


def main() -> None:
    # Create a simple graph
    graph = Graph()

    # Add nodes
    def start_node(state):
        return {"message": "Starting graph", "step": 1}

    def end_node(state):
        return {"message": "Graph complete", "step": state["step"] + 1}

    graph.add_node("start", start_node)
    graph.add_node("end", end_node)

    # Add edges
    graph.add_edge("start", "end")
    graph.set_entry_point("start")

    # Run the graph
    result = graph.invoke({})
    print(result)


if __name__ == "__main__":
    main()
