"""CrewAI: Researcher (tool) -> Writer (no tools) sequential handoff via a
2-task, 2-agent sequential Crew.
"""

from __future__ import annotations

import sys
from importlib import import_module
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[2]))

from crewai import LLM, Agent, Crew, Process, Task
from crewai.tools import tool

from common.config import settings

list_tables = import_module("03_tools.tools.sqlite_tool").list_tables
query_database = import_module("03_tools.tools.sqlite_tool").query_database


@tool("List Tables")
def list_tables_tool() -> str:
    """List all table names in the labs database."""
    return list_tables()


@tool("Query Database")
def query_database_tool(query: str) -> str:
    """Run a single read-only SELECT query against the labs database."""
    return query_database(query)


def _llm() -> LLM:
    return LLM(model=f"ollama/{settings.OLLAMA_MODEL}", base_url=settings.OLLAMA_HOST, temperature=float(settings.TEMPERATURE))


def run_researcher_writer(question: str) -> str:
    llm = _llm()
    researcher = Agent(
        role="Researcher",
        goal="Find the exact facts needed to answer the question using the database tools.",
        backstory="A meticulous analyst who never states a fact without checking the database.",
        tools=[list_tables_tool, query_database_tool],
        llm=llm,
    )
    writer = Agent(
        role="Writer",
        goal="Write a concise answer using only facts handed to you.",
        backstory="A clear technical writer who never invents facts.",
        llm=llm,
    )

    research_task = Task(
        description=f"Find the facts needed to answer: {question}",
        expected_output="A short bullet list of raw facts only.",
        agent=researcher,
    )
    write_task = Task(
        description="Using ONLY the researcher's facts, write a 2-3 sentence answer.",
        expected_output="A 2-3 sentence final answer.",
        agent=writer,
        context=[research_task],
    )

    crew = Crew(agents=[researcher, writer], tasks=[research_task, write_task], process=Process.sequential)
    return str(crew.kickoff())


def main() -> None:
    question = " ".join(sys.argv[1:]) or "Which department has the highest total sales, and by how much?"
    print(run_researcher_writer(question))


if __name__ == "__main__":
    main()
