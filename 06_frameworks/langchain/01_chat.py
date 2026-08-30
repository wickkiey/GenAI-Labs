"""
Phase 7B: LangChain - 01_chat.py

Basic chat with Ollama via LangChain.
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[2]))

from langchain_community.llms.ollama import Ollama

from common.config import settings


def main() -> None:
    # Initialize Ollama LLM
    llm = Ollama(
        base_url=settings.OLLAMA_BASE_URL,
        model=settings.OLLAMA_MODEL,
        temperature=float(settings.TEMPERATURE),
    )

    # Test question
    question = "What is 2 + 2?"
    response = llm.invoke(question)
    print(response)


if __name__ == "__main__":
    main()
