"""Phase 9: 04 -- each subagent owns its own MCP server connection.

The researcher subagent talks only to the `sqlite` MCP server, the coder
subagent talks only to the `filesystem` MCP server. They run concurrently,
each with an isolated `ClientSession` and message history.
"""
from __future__ import annotations

import sys
from contextlib import AsyncExitStack
from dataclasses import dataclass
from pathlib import Path

import anyio
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

sys.path.append(str(Path(__file__).resolve().parents[1] / "04_mcp" / "clients"))
from mcp_agent import MCPAgent, mcp_tool_to_openai_schema  # noqa: E402

SERVERS_DIR = Path(__file__).resolve().parents[1] / "04_mcp" / "servers"

SUBAGENTS = {
    "researcher": {
        "server": SERVERS_DIR / "sqlite" / "server.py",
        "system_prompt": "You are a researcher. Use the sqlite tools to answer factually.",
        "task": "How many employees are in the Sales department?",
    },
    "coder": {
        "server": SERVERS_DIR / "filesystem" / "server.py",
        "system_prompt": "You are a coder. Use the filesystem tools to answer based on file contents.",
        "task": "List the files available in the sandbox.",
    },
}


@dataclass
class MCPSubagentResult:
    name: str
    output: str
    tool_calls: list[str]


async def _run_one(name: str, spec: dict) -> MCPSubagentResult:
    async with AsyncExitStack() as stack:
        params = StdioServerParameters(command=sys.executable, args=[str(spec["server"])])
        read, write = await stack.enter_async_context(stdio_client(params))
        session = await stack.enter_async_context(ClientSession(read, write))
        await session.initialize()

        tools = (await session.list_tools()).tools
        schemas = [mcp_tool_to_openai_schema(tool) for tool in tools]
        dispatch_map = {tool.name: (session, tool.name) for tool in tools}

        agent = MCPAgent(spec["system_prompt"], dispatch_map, schemas)
        try:
            output = await agent.run(spec["task"])
        except Exception as error:  # noqa: BLE001 - surfaced instead of hanging the whole run
            output = f"Error: subagent '{name}' failed ({error})"
        return MCPSubagentResult(name=name, output=output, tool_calls=agent.tool_calls_made)


async def run_mcp_subagents() -> list[MCPSubagentResult]:
    import asyncio

    return list(await asyncio.gather(*(_run_one(name, spec) for name, spec in SUBAGENTS.items())))


def main() -> None:
    results = anyio.run(run_mcp_subagents)
    for result in results:
        print(f"[{result.name}] {result.output} (tools: {result.tool_calls})")


if __name__ == "__main__":
    main()
