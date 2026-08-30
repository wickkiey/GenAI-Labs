"""
Phase 7C: LangGraph - 10_the_spec_task.py

Complete spec task implementation with LangGraph.
"""

from __future__ import annotations

import json
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

# Import the Answer model
spec = import_module("06_frameworks.spec")
Answer = spec.Answer

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


class SpecTaskState(TypedDict):
    """State for spec task execution."""

    question: str
    agent_output: str
    answer: dict


def execute_agent_node(state: SpecTaskState) -> SpecTaskState:
    """Execute the agent with tools."""
    llm = Ollama(
        base_url=settings.OLLAMA_BASE_URL,
        model=settings.OLLAMA_MODEL,
        temperature=float(settings.TEMPERATURE),
    )

    tools = [calculator, query_database]
    prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                """You are a helpful assistant with access to calculator and database tools.

Always:
1. Use tools to answer questions accurately
2. Return your final answer as JSON with:
   - value: the answer
   - reasoning: why this answer is correct
   - tools_used: ["calculator"], ["sqlite"], or both
   - confidence: "high", "medium", or "low"""",
            ),
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

    result = agent_executor.invoke({"input": state["question"]})
    
    # Parse output
    output = result.get("output", "")
    try:
        if "{" in output:
            json_start = output.find("{")
            json_end = output.rfind("}") + 1
            json_str = output[json_start:json_end]
            answer_dict = json.loads(json_str)
        else:
            answer_dict = {
                "value": output,
                "reasoning": "Extracted from agent",
                "tools_used": [],
                "confidence": "low",
            }
    except json.JSONDecodeError:
        answer_dict = {
            "value": output,
            "reasoning": "Agent response",
            "tools_used": [],
            "confidence": "low",
        }

    return {
        "question": state["question"],
        "agent_output": output,
        "answer": answer_dict,
    }


def validate_answer_node(state: SpecTaskState) -> SpecTaskState:
    """Validate the answer format."""
    # Ensure answer has required fields
    required_fields = ["value", "reasoning", "tools_used", "confidence"]
    for field in required_fields:
        if field not in state["answer"]:
            state["answer"][field] = "" if isinstance(state["answer"].get(field), str) else []
    
    return state


def run_agent(question: str) -> Answer:
    """Run the complete spec task workflow."""
    graph = StateGraph(SpecTaskState)

    # Add nodes
    graph.add_node("execute", execute_agent_node)
    graph.add_node("validate", validate_answer_node)

    # Set entry point
    graph.set_entry_point("execute")

    # Add edges
    graph.add_edge("execute", "validate")
    graph.add_edge("validate", END)

    compiled_graph = graph.compile()
    result = compiled_graph.invoke({
        "question": question,
        "agent_output": "",
        "answer": {},
    })

    # Convert to Answer model
    return Answer(**result["answer"])


def main() -> None:
    question = "What is 1234 * 5678?"
    print(f"Question: {question}")
    answer = run_agent(question)
    print(f"Answer: {answer}")
    print(f"JSON: {answer.model_dump_json(indent=2)}")


if __name__ == "__main__":
    main()
