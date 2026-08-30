"""
Phase 7A: PydanticAI - 02_tools.py

Add calculator and database tools to the agent.
"""

from __future__ import annotations

import sys
from importlib import import_module
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[2]))

from pydantic_ai import Agent, ModelProvider

from common.config import settings

# Import tool implementations from Phase 3
calculator_tool = import_module("03_tools.tools.calculator").calculator
query_db = import_module("03_tools.tools.sqlite_tool").query_database


def main() -> None:
    agent = Agent(
        model=ModelProvider.via_url(
            base_url=settings.OLLAMA_BASE_URL,
            model_name=settings.OLLAMA_MODEL,
            api_key=settings.OLLAMA_API_KEY,
        ),
        system_prompt="You are a helpful assistant with access to a calculator and database tools.",
    )

    # Register tools
    @agent.tool
    def calculator(expression: str) -> str:
        """Evaluate a math expression."""
        return calculator_tool(expression)

    @agent.tool
    def query_database(sql: str) -> str:
        """Query the SQLite database."""
        return query_db(sql)

    # Test with a question requiring both tools
    question = "What is 10% of 1000?"
    result = agent.run_sync(question)
    print(result.data)


if __name__ == "__main__":
    main()
