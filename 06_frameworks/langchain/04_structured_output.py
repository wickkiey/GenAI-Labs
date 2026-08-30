"""
Phase 7B: LangChain - 04_structured_output.py

Return structured output using Pydantic models with LangChain.
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

# Import the Answer model
spec = import_module("06_frameworks.spec")
Answer = spec.Answer

# Import tool implementations
calculator_tool = import_module("03_tools.tools.calculator").calculator


@tool
def calculator(expression: str) -> str:
    """Evaluate a mathematical expression."""
    return calculator_tool(expression)


def main() -> None:
    llm = Ollama(
        base_url=settings.OLLAMA_BASE_URL,
        model=settings.OLLAMA_MODEL,
        temperature=float(settings.TEMPERATURE),
    )

    # Use with_structured_output to enforce the Answer schema
    structured_llm = llm.with_structured_output(Answer)

    prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                """You are a helpful assistant. 
Return your response in JSON format with fields:
- value: the answer
- reasoning: why this answer is correct
- tools_used: list of tool names used
- confidence: "high", "medium", or "low"
""",
            ),
            ("user", "{input}"),
        ]
    )

    question = "What is 100 + 50?"
    response = structured_llm.invoke(prompt.format_prompt(input=question).to_string())
    print(response.model_dump_json(indent=2))


if __name__ == "__main__":
    main()
