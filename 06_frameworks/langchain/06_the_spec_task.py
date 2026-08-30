"""
Phase 7B: LangChain - 06_the_spec_task.py

Complete task implementation with both tools and structured output.
"""

from __future__ import annotations

import json
import sys
from importlib import import_module
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[2]))

from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain.prompts import ChatPromptTemplate
from langchain.tools import tool
from langchain_community.llms.ollama import Ollama

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
    """Query the SQLite database with SQL."""
    return query_db(sql)


def run_agent(question: str) -> dict:
    """Run the agent and return structured Answer."""
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
   - confidence: "high", "medium", or "low"

If you cannot answer, explain why.""",
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

    result = agent_executor.invoke({"input": question})
    
    # Try to parse as JSON, fallback to Answer object
    try:
        output = result.get("output", "")
        # Extract JSON from output if wrapped in text
        if "{" in output:
            json_start = output.find("{")
            json_end = output.rfind("}") + 1
            json_str = output[json_start:json_end]
            answer_dict = json.loads(json_str)
            return Answer(**answer_dict)
        else:
            # Return a default Answer
            return Answer(
                value=output,
                reasoning="Extracted from agent output",
                tools_used=[],
                confidence="low",
            )
    except (json.JSONDecodeError, ValueError):
        return Answer(
            value=result.get("output", ""),
            reasoning="Agent response",
            tools_used=[],
            confidence="low",
        )


def main() -> None:
    question = "What is 1234 * 5678?"
    print(f"Question: {question}")
    answer = run_agent(question)
    print(f"Answer: {answer}")
    print(f"JSON: {answer.model_dump_json(indent=2)}")


if __name__ == "__main__":
    main()
