"""
Phase 7B: LangChain - 03_agent.py

Create a tool-using agent with LangChain's AgentExecutor.
"""

from __future__ import annotations

import sys
from importlib import import_module
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[2]))

from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain.prompts import ChatPromptTemplate
from langchain.tools import tool
from langchain_community.llms.ollama import Ollama

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
    """Query the SQLite database with SQL."""
    return query_db(sql)


def main() -> None:
    llm = Ollama(
        base_url=settings.OLLAMA_BASE_URL,
        model=settings.OLLAMA_MODEL,
        temperature=float(settings.TEMPERATURE),
    )

    tools = [calculator, query_database]

    # Create a prompt template for the agent
    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", "You are a helpful assistant with access to calculator and database tools."),
            ("user", "{input}"),
            ("placeholder", "{agent_scratchpad}"),
        ]
    )

    # Create and execute the agent
    agent = create_tool_calling_agent(llm, tools, prompt)
    agent_executor = AgentExecutor(
        agent=agent,
        tools=tools,
        verbose=True,
        max_iterations=5,
    )

    question = "What is 1234 * 5678?"
    result = agent_executor.invoke({"input": question})
    print(f"\nFinal Answer: {result['output']}")


if __name__ == "__main__":
    main()
