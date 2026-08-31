"""LangChain: Researcher (AgentExecutor w/ tools) -> Writer (no tools)."""

from __future__ import annotations

import sys
from importlib import import_module
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[2]))

from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.tools import tool
from langchain_ollama import ChatOllama

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


def _llm() -> ChatOllama:
    return ChatOllama(base_url=settings.OLLAMA_HOST, model=settings.OLLAMA_MODEL, temperature=float(settings.TEMPERATURE))


def run_researcher_writer(question: str) -> str:
    llm = _llm()
    tools = [list_tables_tool, query_database_tool]
    prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                "You are a Researcher. Use the list_tables_tool and query_database_tool "
                "tools to find the exact facts needed to answer the question. Reply with a "
                "short bullet list of raw facts only - no narrative.",
            ),
            ("user", "{input}"),
            ("placeholder", "{agent_scratchpad}"),
        ]
    )
    agent = create_tool_calling_agent(llm, tools, prompt)
    executor = AgentExecutor(agent=agent, tools=tools, max_iterations=6)
    research_notes = executor.invoke({"input": question})["output"]

    writer_reply = llm.invoke(
        [
            (
                "system",
                "Using ONLY the facts provided below, write a 2-3 sentence answer to the "
                "question. Do not invent any facts and do not use any tools.",
            ),
            ("user", f"Question: {question}\n\nResearcher facts:\n{research_notes}"),
        ]
    )
    return writer_reply.content


def main() -> None:
    question = " ".join(sys.argv[1:]) or "Which department has the highest total sales, and by how much?"
    print(run_researcher_writer(question))


if __name__ == "__main__":
    main()
