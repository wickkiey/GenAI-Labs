"""Strands: Researcher (tools) -> Writer (no tools) sequential handoff."""

from __future__ import annotations

import sys
from importlib import import_module
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[2]))

from strands import Agent, tool
from strands.models.ollama import OllamaModel

from common.config import settings

list_tables = import_module("03_tools.tools.sqlite_tool").list_tables
query_database = import_module("03_tools.tools.sqlite_tool").query_database


@tool
def list_tables_tool() -> str:
    """List all table names in the labs database."""
    return list_tables()


@tool
def query_database_tool(query: str) -> str:
    """Run a single read-only SELECT query against the labs database."""
    return query_database(query)


def _model() -> OllamaModel:
    return OllamaModel(host=settings.OLLAMA_HOST, model_id=settings.OLLAMA_MODEL)


def run_researcher_writer(question: str) -> str:
    researcher = Agent(
        model=_model(),
        tools=[list_tables_tool, query_database_tool],
        system_prompt=(
            "Use the list_tables_tool and query_database_tool tools to find the exact facts "
            "needed to answer the question. Reply with a short bullet list of raw facts only."
        ),
    )
    research_notes = str(researcher(question))

    writer = Agent(
        model=_model(),
        system_prompt=(
            "Using ONLY the facts provided below, write a 2-3 sentence answer to the "
            "question. Do not invent any facts and do not use any tools."
        ),
    )
    return str(writer(f"Question: {question}\n\nResearcher facts:\n{research_notes}"))


def main() -> None:
    question = " ".join(sys.argv[1:]) or "Which department has the highest total sales, and by how much?"
    print(run_researcher_writer(question))


if __name__ == "__main__":
    main()
