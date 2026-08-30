from __future__ import annotations

import sys
from contextlib import AsyncExitStack
from pathlib import Path

import anyio
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

try:
    from .mcp_agent import MCPAgent, mcp_tool_to_openai_schema
except ImportError:
    from mcp_agent import MCPAgent, mcp_tool_to_openai_schema

SERVERS_DIR = Path(__file__).resolve().parents[1] / "servers"
SERVERS = {
    "calc": SERVERS_DIR / "calculator" / "server.py",
    "db": SERVERS_DIR / "sqlite" / "server.py",
    "fs": SERVERS_DIR / "filesystem" / "server.py",
}

SYSTEM_PROMPT = (
    "You are a helpful assistant with tools from three MCP servers: "
    "calculator (calc__*), sqlite (db__*), and filesystem (fs__*). "
    "Use the namespaced tool names exactly as given. Always use a calc__ tool "
    "for arithmetic instead of computing it yourself, even simple multiplication."
)


async def _connect(stack: AsyncExitStack, server_path: Path) -> ClientSession:
    params = StdioServerParameters(command=sys.executable, args=[str(server_path)])
    read, write = await stack.enter_async_context(stdio_client(params))
    session = await stack.enter_async_context(ClientSession(read, write))
    await session.initialize()
    return session


async def _run(prompt: str) -> tuple[str, list[str]]:
    async with AsyncExitStack() as stack:
        schemas = []
        dispatch_map: dict[str, tuple[ClientSession, str]] = {}
        for prefix, server_path in SERVERS.items():
            session = await _connect(stack, server_path)
            tools = (await session.list_tools()).tools
            for tool in tools:
                exposed_name = f"{prefix}__{tool.name}"
                schemas.append(mcp_tool_to_openai_schema(tool, name=exposed_name))
                dispatch_map[exposed_name] = (session, tool.name)

        agent = MCPAgent(SYSTEM_PROMPT, dispatch_map, schemas)
        reply = await agent.run(prompt)
        return reply, agent.tool_calls_made


def main() -> None:
    prompt = " ".join(sys.argv[1:]) or "How many employees are in Sales, then multiply that by 12?"
    reply, tool_calls = anyio.run(_run, prompt)
    print(reply)
    print(f"tools called: {tool_calls}")


if __name__ == "__main__":
    main()
