from __future__ import annotations

import sys
from pathlib import Path

import anyio
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

SERVERS_DIR = Path(__file__).resolve().parents[1] / "04_mcp" / "servers"
PYTHON = sys.executable


async def _list_tool_names(server_path: Path) -> list[str]:
    params = StdioServerParameters(command=PYTHON, args=[str(server_path)])
    async with stdio_client(params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            result = await session.list_tools()
            return sorted(tool.name for tool in result.tools)


async def _call_tool(server_path: Path, name: str, arguments: dict):
    params = StdioServerParameters(command=PYTHON, args=[str(server_path)])
    async with stdio_client(params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            return await session.call_tool(name, arguments)


def _text(result) -> str:
    return "".join(block.text for block in result.content if hasattr(block, "text"))


def test_calculator_server_lists_expected_tools() -> None:
    names = anyio.run(_list_tool_names, SERVERS_DIR / "calculator" / "server.py")
    assert names == ["add", "divide", "multiply", "subtract"]


def test_calculator_server_multiply() -> None:
    result = anyio.run(
        _call_tool, SERVERS_DIR / "calculator" / "server.py", "multiply", {"a": 1234, "b": 5678}
    )
    assert not result.isError
    assert "7006652" in _text(result)


def test_calculator_server_divide_by_zero_returns_error_not_crash() -> None:
    result = anyio.run(
        _call_tool, SERVERS_DIR / "calculator" / "server.py", "divide", {"a": 1, "b": 0}
    )
    assert result.isError
    assert "division by zero" in _text(result)

    # the server process must still be usable for a fresh session after the error
    follow_up = anyio.run(
        _call_tool, SERVERS_DIR / "calculator" / "server.py", "add", {"a": 1, "b": 2}
    )
    assert not follow_up.isError
    assert "3" in _text(follow_up)


def test_filesystem_server_lists_expected_tools() -> None:
    names = anyio.run(_list_tool_names, SERVERS_DIR / "filesystem" / "server.py")
    assert names == ["list_files", "read_file", "search_files"]


def test_filesystem_server_reads_seed_file() -> None:
    result = anyio.run(
        _call_tool, SERVERS_DIR / "filesystem" / "server.py", "read_file", {"path": "notes.txt"}
    )
    assert not result.isError
    assert "sandbox" in _text(result)


def test_filesystem_server_rejects_path_traversal() -> None:
    result = anyio.run(
        _call_tool, SERVERS_DIR / "filesystem" / "server.py", "read_file", {"path": "../../.env"}
    )
    assert result.isError


def test_sqlite_server_lists_expected_tools() -> None:
    names = anyio.run(_list_tool_names, SERVERS_DIR / "sqlite" / "server.py")
    assert names == ["describe_table", "list_tables", "query_database"]


def test_sqlite_server_query_database() -> None:
    result = anyio.run(
        _call_tool,
        SERVERS_DIR / "sqlite" / "server.py",
        "query_database",
        {"query": "SELECT COUNT(*) FROM employees"},
    )
    assert not result.isError
    assert "rows" in _text(result)


def test_sqlite_server_rejects_write_statement() -> None:
    result = anyio.run(
        _call_tool,
        SERVERS_DIR / "sqlite" / "server.py",
        "query_database",
        {"query": "DROP TABLE employees"},
    )
    assert result.isError


def test_knowledge_server_lists_expected_tools() -> None:
    names = anyio.run(_list_tool_names, SERVERS_DIR / "knowledge" / "server.py")
    assert names == ["get_document", "search_knowledge"]


def test_knowledge_server_search_and_get_document() -> None:
    search_result = anyio.run(
        _call_tool, SERVERS_DIR / "knowledge" / "server.py", "search_knowledge", {"keyword": "vector"}
    )
    assert not search_result.isError
    assert "vectors.txt" in _text(search_result)

    document_result = anyio.run(
        _call_tool, SERVERS_DIR / "knowledge" / "server.py", "get_document", {"name": "vectors.txt"}
    )
    assert not document_result.isError
    assert "embeddings" in _text(document_result)


def test_knowledge_server_rejects_path_traversal() -> None:
    result = anyio.run(
        _call_tool, SERVERS_DIR / "knowledge" / "server.py", "get_document", {"name": "../../.env"}
    )
    assert result.isError
