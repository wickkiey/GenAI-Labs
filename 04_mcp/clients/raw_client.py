from __future__ import annotations

import sys
from pathlib import Path

import anyio
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

try:
    from .mcp_agent import MCPAgent, mcp_tool_to_openai_schema
except ImportError:
    from mcp_agent import MCPAgent, mcp_tool_to_openai_schema

SERVER_PATH = Path(__file__).resolve().parents[1] / "servers" / "calculator" / "server.py"

SYSTEM_PROMPT = "You are a helpful assistant with access to calculator tools over MCP."


async def _run(prompt: str) -> str:
    params = StdioServerParameters(command=sys.executable, args=[str(SERVER_PATH)])
    async with stdio_client(params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            tools = (await session.list_tools()).tools
            schemas = [mcp_tool_to_openai_schema(tool) for tool in tools]
            dispatch_map = {tool.name: (session, tool.name) for tool in tools}
            agent = MCPAgent(SYSTEM_PROMPT, dispatch_map, schemas)
            return await agent.run(prompt)


def main() -> None:
    prompt = " ".join(sys.argv[1:]) or "What is 1234 * 5678?"
    print(anyio.run(_run, prompt))


if __name__ == "__main__":
    main()
