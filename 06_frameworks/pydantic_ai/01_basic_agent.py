"""
Phase 7A: PydanticAI - 01_basic_agent.py

Basic agent with simple question answering.
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[2]))

from pydantic_ai import Agent
from pydantic_ai.models.openai import OpenAIChatModel
from pydantic_ai.providers.openai import OpenAIProvider

from common.config import settings


def main() -> None:
    # Use Ollama model via its OpenAI-compatible endpoint
    agent = Agent(
        model=OpenAIChatModel(
            settings.OLLAMA_MODEL,
            provider=OpenAIProvider(
                base_url=settings.OLLAMA_BASE_URL,
                api_key=settings.OLLAMA_API_KEY,
            ),
        )
    )

    # Test question
    question = "What is 2 + 2?"
    result = agent.run_sync(question)
    print(result.output)


if __name__ == "__main__":
    main()
