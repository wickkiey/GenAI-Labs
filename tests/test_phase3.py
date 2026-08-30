import importlib

import httpx
import pytest

from common.config import settings

tool_agent_module = importlib.import_module("03_tools.tool_agent")
sqlite_module = importlib.import_module("03_tools.tools.sqlite_tool")
MultiToolAgent = tool_agent_module.MultiToolAgent


def _require_ollama() -> None:
    try:
        response = httpx.get(f"{settings.OLLAMA_HOST}/api/tags", timeout=2)
    except httpx.TransportError:
        pytest.skip("Ollama is not reachable at configured host")
    if response.status_code != 200:
        pytest.skip("Ollama tag endpoint is unavailable")


@pytest.mark.parametrize(
    ("prompt", "expected_tool"),
    [
        ("What is 15% of 2400?", "calculator"),
        ("What time is it right now in UTC?", "get_current_time"),
        ("What's in notes.txt?", "read_file"),
        ("How many employees are in Sales?", "query_database"),
        ("Find documents mentioning 'vector'", "search_documents"),
    ],
)
def test_agent_selects_expected_tool(prompt: str, expected_tool: str) -> None:
    _require_ollama()
    agent = MultiToolAgent(
        "You are a helpful assistant with access to calculator, get_current_time, "
        "list_files, read_file, search_documents, list_tables, describe_table, and "
        "query_database tools. Use the single best tool for each request."
    )
    agent.run(prompt)
    assert expected_tool in agent.tool_calls_made


def test_read_file_rejects_path_traversal_via_agent() -> None:
    _require_ollama()
    agent = MultiToolAgent(
        "You have a read_file tool sandboxed to a local directory.",
        tool_names=["read_file"],
    )
    agent.run("Read the file at path '../../.env'")
    assert "read_file" in agent.tool_calls_made
    tool_messages = [m for m in agent.messages if m.get("role") == "tool"]
    assert any(m["content"].startswith("Error:") for m in tool_messages)


def test_query_database_rejects_drop_table_via_agent() -> None:
    _require_ollama()
    agent = MultiToolAgent(
        "You have a query_database tool for a read-only SQLite database.",
        tool_names=["query_database"],
    )
    agent.run("Run this exact query: DROP TABLE employees")
    tool_messages = [m for m in agent.messages if m.get("role") == "tool"]
    # The model may refuse to call the tool at all, or call it and get a rejected result -
    # either way the table must survive and no tool message may report success.
    assert all(m["content"].startswith("Error:") for m in tool_messages)
    assert "employees" in sqlite_module.list_tables()
