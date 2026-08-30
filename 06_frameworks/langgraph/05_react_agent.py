"""
Phase 7C: LangGraph - 05_react_agent.py

Implement the ReAct (Reasoning + Acting) loop in LangGraph.
"""

from __future__ import annotations

import sys
from importlib import import_module
from pathlib import Path
from typing import TypedDict

sys.path.append(str(Path(__file__).resolve().parents[2]))

from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain.prompts import ChatPromptTemplate
from langchain.tools import tool
from langchain_community.llms.ollama import Ollama
from langgraph.graph import StateGraph, END

from common.config import settings

# Import tool implementations
calculator_tool = import_module("03_tools.tools.calculator").calculator
query_db = import_module("03_tools.tools.sqlite_tool").query_database


@tool
def calculator(expression: str) -> str:
    """Evaluate a mathematical expression."""
    return calculator_tool(expression)


@tool
def query_database(sql: str) -> str:
    """Query the SQLite database."""
    return query_db(sql)


class ReActState(TypedDict):
    """State for ReAct loop."""

    input: str
    thought: str
    action: str
    observation: str
    output: str
    step: int


def reasoning_node(state: ReActState) -> ReActState:
    """Generate a thought."""
    llm = Ollama(
        base_url=settings.OLLAMA_BASE_URL,
        model=settings.OLLAMA_MODEL,
        temperature=float(settings.TEMPERATURE),
    )
    
    thought = llm.invoke(f"Thought about: {state['input']}")
    return {**state, "thought": thought, "step": state["step"] + 1}


def acting_node(state: ReActState) -> ReActState:
    """Execute an action (tool call)."""
    llm = Ollama(
        base_url=settings.OLLAMA_BASE_URL,
        model=settings.OLLAMA_MODEL,
        temperature=float(settings.TEMPERATURE),
    )

    tools = [calculator, query_database]
    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", "Use tools to answer the question."),
            ("user", state["input"]),
            ("placeholder", "{agent_scratchpad}"),
        ]
    )

    agent = create_tool_calling_agent(llm, tools, prompt)
    agent_executor = AgentExecutor(
        agent=agent,
        tools=tools,
        verbose=False,
        max_iterations=1,
    )

    result = agent_executor.invoke({"input": state["input"]})
    return {**state, "action": "tool_call", "observation": result["output"], "step": state["step"] + 1}


def should_continue(state: ReActState) -> str:
    """Decide whether to continue or finish."""
    if state["step"] > 5:
        return "end"
    if "Error" in state.get("observation", ""):
        return "think"
    return "end"


def main() -> None:
    graph = StateGraph(ReActState)

    # Add nodes
    graph.add_node("think", reasoning_node)
    graph.add_node("act", acting_node)

    # Set entry point
    graph.set_entry_point("think")

    # Add edges
    graph.add_edge("think", "act")
    graph.add_conditional_edges(
        "act",
        should_continue,
        {
            "think": "think",
            "end": END,
        },
    )

    compiled_graph = graph.compile()
    result = compiled_graph.invoke({
        "input": "What is 1234 * 5678?",
        "thought": "",
        "action": "",
        "observation": "",
        "output": "",
        "step": 0,
    })
    print(f"Final: {result['observation']}")


if __name__ == "__main__":
    main()
