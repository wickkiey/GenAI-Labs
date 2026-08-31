"""PydanticAI: Researcher (tools) -> Writer (no tools) sequential handoff."""

from __future__ import annotations

import sys
from importlib import import_module
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[2]))

from pydantic_ai import Agent
from pydantic_ai.models.openai import OpenAIChatModel
from pydantic_ai.providers.openai import OpenAIProvider

from common.config import settings

list_tables = import_module("03_tools.tools.sqlite_tool").list_tables
query_database = import_module("03_tools.tools.sqlite_tool").query_database


def _model() -> OpenAIChatModel:
    return OpenAIChatModel(
        settings.OLLAMA_MODEL,
        provider=OpenAIProvider(base_url=settings.OLLAMA_BASE_URL, api_key=settings.OLLAMA_API_KEY),
    )


def run_researcher_writer(question: str) -> str:
    researcher = Agent(
        model=_model(),
        system_prompt=(
            "You are a Researcher. Use the list_tables_tool and query_database_tool tools "
            "to find the exact facts (numbers, names) needed to answer the question. Reply "
            "with a short bullet list of raw facts only - no narrative."
        ),
    )

    @researcher.tool_plain
    def list_tables_tool() -> str:
        """List all table names in the labs database."""
        return list_tables()

    @researcher.tool_plain
    def query_database_tool(query: str) -> str:
        """Run a single read-only SELECT query against the labs database."""
        return query_database(query)

    research_notes = researcher.run_sync(question).output

    writer = Agent(
        model=_model(),
        system_prompt=(
            "You are a Writer. Using ONLY the facts provided below, write a 2-3 sentence "
            "answer to the question. Do not invent any facts and do not use any tools."
        ),
    )
    result = writer.run_sync(f"Question: {question}\n\nResearcher facts:\n{research_notes}")
    return result.output


def main() -> None:
    question = " ".join(sys.argv[1:]) or "Which department has the highest total sales, and by how much?"
    print(run_researcher_writer(question))


if __name__ == "__main__":
    main()
