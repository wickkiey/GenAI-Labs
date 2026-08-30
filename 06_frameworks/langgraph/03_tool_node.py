"""
Phase 7C: LangGraph - 03_tool_node.py

Add a tool-calling node that processes tool calls from the agent.
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
from langgraph.graph import StateGraph

from common.config import settings

# Import tool implementations
calculator_tool = import_module("03_tools.tools.calculator").calculator


@tool
def calculator(expression: str) -> str:
    """Evaluate a mathematical expression."""
    return calculator_tool(expression)


class AgentState(TypedDict):
    """State passed through the graph."""

    input: str
    messages: list[dict]
    output: str | None


def agent_node(state: AgentState) -> AgentState:
    """Agent node that can call tools."""
    llm = Ollama(
        base_url=settings.OLLAMA_BASE_URL,
        model=settings.OLLAMA_MODEL,
        temperature=float(settings.TEMPERATURE),
    )

    tools = [calculator]
    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", "You are a helpful math assistant."),
            ("user", "{input}"),
            ("placeholder", "{agent_scratchpad}"),
        ]
    )

    agent = create_tool_calling_agent(llm, tools, prompt)
    agent_executor = AgentExecutor(
        agent=agent,
        tools=tools,
        verbose=False,
        max_iterations=5,
    )

    result = agent_executor.invoke({"input": state["input"]})
    
    return {
        "input": state["input"],
        "messages": state.get("messages", []) + [{"role": "assistant", "content": result["output"]}],
        "output": result["output"],
    }


def main() -> None:
    graph = StateGraph(AgentState)
    graph.add_node("agent", agent_node)
    graph.set_entry_point("agent")
    graph.set_finish_point("agent")

    compiled_graph = graph.compile()
    result = compiled_graph.invoke({
        "input": "What is 1234 * 5678?",
        "messages": [],
        "output": None,
    })
    print(f"Output: {result['output']}")


if __name__ == "__main__":
    main()
