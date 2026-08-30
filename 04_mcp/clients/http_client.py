from __future__ import annotations

import sys

import anyio
from mcp import ClientSession
from mcp.client.streamable_http import streamable_http_client

try:
    from .mcp_agent import MCPAgent, mcp_tool_to_openai_schema
except ImportError:
    from mcp_agent import MCPAgent, mcp_tool_to_openai_schema

SERVER_URL = "http://127.0.0.1:8000/mcp"
SYSTEM_PROMPT = "You are a helpful assistant with access to calculator tools served over HTTP."


async def _run(prompt: str) -> str:
    async with streamable_http_client(SERVER_URL) as (read, write, _get_session_id):
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
