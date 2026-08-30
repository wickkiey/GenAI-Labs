from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

from mcp import ClientSession

sys.path.append(str(Path(__file__).resolve().parents[2]))

from common.config import settings
from common.llm import chat


def mcp_tool_to_openai_schema(tool: Any, name: str | None = None) -> dict[str, Any]:
    """Convert an MCP tool definition into an OpenAI-style function tool schema."""
    return {
        "type": "function",
        "function": {
            "name": name or tool.name,
            "description": tool.description or "",
            "parameters": tool.inputSchema,
        },
    }


class MCPAgent:
    """Drives one or more MCP `ClientSession`s through a bounded tool loop.

    `dispatch_map` maps the tool name presented to the model to the
    `(session, real_tool_name)` pair used to actually call it, which lets
    callers namespace tools from multiple servers (see `multi_server.py`).
    """

    def __init__(
        self,
        system_prompt: str,
        dispatch_map: dict[str, tuple[ClientSession, str]],
        schemas: list[dict[str, Any]],
        model: str = settings.OLLAMA_MODEL,
        max_iterations: int = 5,
    ) -> None:
        self.model = model
        self.max_iterations = max_iterations
        self.messages: list[dict[str, Any]] = [{"role": "system", "content": system_prompt}]
        self.dispatch_map = dispatch_map
        self.schemas = schemas
        self.tool_calls_made: list[str] = []
        self.iterations = 0

    def _call_model(self) -> dict[str, Any]:
        return chat(self.messages, model=self.model, tools=self.schemas)

    @staticmethod
    def _assistant_message(response: dict[str, Any]) -> dict[str, Any]:
        message: dict[str, Any] = {"role": "assistant", "content": response["response_content"]}
        if tool_calls := response.get("tool_calls"):
            message["tool_calls"] = [
                {
                    "id": call.id,
                    "type": call.type,
                    "function": {"name": call.function.name, "arguments": call.function.arguments},
                }
                for call in tool_calls
            ]
        return message

    async def _run_tool_calls(self, response: dict[str, Any]) -> None:
        self.messages.append(self._assistant_message(response))
        for call in response["tool_calls"]:
            self.tool_calls_made.append(call.function.name)
            entry = self.dispatch_map.get(call.function.name)
            if entry is None:
                result_text = f"Error: unknown tool '{call.function.name}'"
            else:
                session, real_name = entry
                try:
                    arguments = json.loads(call.function.arguments or "{}")
                except json.JSONDecodeError as error:
                    result_text = f"Error: invalid arguments ({error})"
                else:
                    result = await session.call_tool(real_name, arguments)
                    result_text = "".join(block.text for block in result.content if hasattr(block, "text"))
                    if result.isError:
                        result_text = f"Error: {result_text}"
            self.messages.append({"role": "tool", "tool_call_id": call.id, "content": result_text})

    async def run(self, user_input: str) -> str:
        self.messages.append({"role": "user", "content": user_input})
        for iteration in range(1, self.max_iterations + 1):
            self.iterations = iteration
            response = self._call_model()
            if not response.get("tool_calls"):
                reply = response["response_content"].strip()
                self.messages.append({"role": "assistant", "content": reply})
                return reply
            await self._run_tool_calls(response)
        raise RuntimeError(f"agent exceeded its {self.max_iterations}-iteration tool-call limit")
