"""AutoGen: Researcher (tools) -> Writer (no tools) sequential handoff."""

from __future__ import annotations

import asyncio
import sys
from importlib import import_module
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[2]))

from autogen_agentchat.agents import AssistantAgent
from autogen_core.tools import FunctionTool

try:
    from ._client import make_client
except ImportError:
    from _client import make_client

list_tables = import_module("03_tools.tools.sqlite_tool").list_tables
query_database = import_module("03_tools.tools.sqlite_tool").query_database


async def _run(question: str) -> str:
    client = make_client()
    tools = [
        FunctionTool(list_tables, description="List all table names in the labs database."),
        FunctionTool(query_database, description="Run a single read-only SELECT query against the labs database."),
    ]
    researcher = AssistantAgent(
        "researcher",
        model_client=client,
        tools=tools,
        system_message=(
            "Use the list_tables and query_database tools to find the exact facts (numbers, "
            "names) needed to answer the question. Reply with a short bullet list of raw "
            "facts only - no narrative."
        ),
    )
    research_result = await researcher.run(task=question)
    research_notes = research_result.messages[-1].content

    writer = AssistantAgent(
        "writer",
        model_client=client,
        system_message=(
            "Using ONLY the facts provided below, write a 2-3 sentence answer to the "
            "question. Do not invent any facts and do not use any tools."
        ),
    )
    writer_result = await writer.run(task=f"Question: {question}\n\nResearcher facts:\n{research_notes}")
    return writer_result.messages[-1].content


def run_researcher_writer(question: str) -> str:
    return asyncio.run(_run(question))


def main() -> None:
    question = " ".join(sys.argv[1:]) or "Which department has the highest total sales, and by how much?"
    print(run_researcher_writer(question))


if __name__ == "__main__":
    main()
