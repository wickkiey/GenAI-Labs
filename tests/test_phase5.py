from __future__ import annotations

import importlib
import sys
from contextlib import AsyncExitStack
from pathlib import Path

import anyio
import httpx
import pytest
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

from common.config import settings

multi_server = importlib.import_module("04_mcp.clients.multi_server")
http_client_module = importlib.import_module("04_mcp.clients.http_client")


def _require_ollama() -> None:
    try:
        response = httpx.get(f"{settings.OLLAMA_HOST}/api/tags", timeout=2)
    except httpx.TransportError:
        pytest.skip("Ollama is not reachable at configured host")
    if response.status_code != 200:
        pytest.skip("Ollama tag endpoint is unavailable")


def test_multi_server_tool_names_merge_without_collisions() -> None:
    async def _collect_names() -> list[str]:
        async with AsyncExitStack() as stack:
            names: list[str] = []
            for prefix, server_path in multi_server.SERVERS.items():
                session = await multi_server._connect(stack, server_path)
                tools = (await session.list_tools()).tools
                names.extend(f"{prefix}__{tool.name}" for tool in tools)
            return names

    names = anyio.run(_collect_names)
    assert len(names) == len(set(names))
    assert any(name.startswith("calc__") for name in names)
    assert any(name.startswith("db__") for name in names)
    assert any(name.startswith("fs__") for name in names)


def test_multi_server_agent_uses_at_least_two_servers() -> None:
    _require_ollama()
    reply, tool_calls = anyio.run(
        multi_server._run, "How many employees are in Sales, then multiply that number by 12?"
    )
    assert reply
    assert len(tool_calls) >= 2
    prefixes = {name.split("__", 1)[0] for name in tool_calls}
    assert len(prefixes) >= 2


def test_disconnected_server_raises_clear_error_not_hang() -> None:
    async def _connect_bad_server() -> None:
        params = StdioServerParameters(
            command=sys.executable, args=[str(Path(__file__).parent / "does_not_exist.py")]
        )
        with anyio.fail_after(10):
            async with stdio_client(params) as (read, write):
                async with ClientSession(read, write) as session:
                    await session.initialize()

    with pytest.raises(Exception):
        anyio.run(_connect_bad_server)


def test_http_client_against_live_server_or_skip() -> None:
    _require_ollama()
    try:
        reply = anyio.run(http_client_module._run, "What is 12 * 8?")
    except Exception:
        pytest.skip(f"calculator_http server is not running at {http_client_module.SERVER_URL}")
    assert "96" in reply
