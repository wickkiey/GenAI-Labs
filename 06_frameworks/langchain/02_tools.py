"""
Phase 7B: LangChain - 02_tools.py

Add calculator and database tools via LangChain's tool decorator.
"""

from __future__ import annotations

import sys
from importlib import import_module
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[2]))

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

    # Bind tools to the LLM
    tools = [calculator, query_database]
    llm_with_tools = llm.bind_tools(tools)

    question = "What is 10% of 1000?"
    response = llm_with_tools.invoke(question)
    print(response)


if __name__ == "__main__":
    main()
