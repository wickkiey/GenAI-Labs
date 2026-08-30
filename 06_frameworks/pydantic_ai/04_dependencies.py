"""
Phase 7A: PydanticAI - 04_dependencies.py

Use dependencies to inject context into tools and system prompt.
"""

from __future__ import annotations

import sys
from importlib import import_module
from pathlib import Path
from typing import NamedTuple

sys.path.append(str(Path(__file__).resolve().parents[2]))

from pydantic_ai import Agent, ModelProvider
from pydantic_ai.exceptions import ModelRetry

from common.config import settings

# Import tool implementations
calculator_tool = import_module("03_tools.tools.calculator").calculator


class Context(NamedTuple):
    """Dependency injection context."""

    attempts: int = 0


def main() -> None:
    agent = Agent(
        model=ModelProvider.via_url(
            base_url=settings.OLLAMA_BASE_URL,
            model_name=settings.OLLAMA_MODEL,
            api_key=settings.OLLAMA_API_KEY,
        ),
        system_prompt="You are a math expert. Use the calculator tool for any arithmetic.",
    )

    @agent.tool
    def calculator(ctx: Context, expression: str) -> str:
        """Evaluate a math expression. context provides attempt info."""
        result = calculator_tool(expression)
        if result.startswith("Error:"):
            raise ModelRetry(f"Calculation failed: {result}. Try a different expression.")
        return result

    ctx = Context(attempts=1)
    question = "What is 1234 * 5678?"
    result = agent.run_sync(question, deps=ctx)
    print(result.data)


if __name__ == "__main__":
    main()
