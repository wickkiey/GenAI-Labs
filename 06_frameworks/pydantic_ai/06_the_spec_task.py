"""
Phase 7A: PydanticAI - 06_the_spec_task.py

Implement the Phase 7 invariant task: answer using calculator + sqlite tools,
verify the result, and return Answer(value, reasoning, tools_used, confidence).
"""

from __future__ import annotations

import sys
from importlib import import_module
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[2]))

from pydantic_ai import Agent, ModelProvider

from common.config import settings

# Import dependencies
spec = import_module("06_frameworks.spec")
Answer = spec.Answer

calculator_tool = import_module("03_tools.tools.calculator").calculator
query_db = import_module("03_tools.tools.sqlite_tool").query_database


def run_agent(question: str) -> Answer:
    """Run the agent on a question and return structured Answer."""
    agent = Agent(
        model=ModelProvider.via_url(
            base_url=settings.OLLAMA_BASE_URL,
            model_name=settings.OLLAMA_MODEL,
            api_key=settings.OLLAMA_API_KEY,
        ),
        result_type=Answer,
        system_prompt="""You are a helpful assistant with access to calculator and database tools.
        
Always:
1. Use tools to answer questions accurately
2. Return your answer in JSON format with: value, reasoning, tools_used, confidence
3. tools_used should be an array: ["calculator"], ["sqlite"], or both
4. confidence should be one of: "high", "medium", "low"

If you cannot answer with the available tools, explain why.""",
    )

    @agent.tool
    def calculator(expression: str) -> str:
        """Evaluate a mathematical expression."""
        return calculator_tool(expression)

    @agent.tool
    def query_database(sql: str) -> str:
        """Query the SQLite database with SQL."""
        return query_db(sql)

    result = agent.run_sync(question)
    return result.data


def main() -> None:
    # Test with a simple question
    question = "What is 1234 * 5678?"
    print(f"Question: {question}")
    answer = run_agent(question)
    print(f"Answer: {answer}")
    print(f"JSON: {answer.model_dump_json(indent=2)}")


if __name__ == "__main__":
    main()
