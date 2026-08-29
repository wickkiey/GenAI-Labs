from __future__ import annotations

import ast
import json
import operator
import sys
from collections.abc import Callable
from pathlib import Path
from typing import Any

sys.path.append(str(Path(__file__).resolve().parents[1]))

from common.config import settings
from common.llm import chat

CALCULATOR_TOOL = {
    "type": "function",
    "function": {
        "name": "calculator",
        "description": "Evaluate a basic arithmetic expression.",
        "parameters": {
            "type": "object",
            "properties": {
                "expression": {
                    "type": "string",
                    "description": "Arithmetic using numbers and +, -, *, /, //, %, or **.",
                }
            },
            "required": ["expression"],
            "additionalProperties": False,
        },
    },
}

_BINARY_OPERATORS: dict[type[ast.operator], Callable[[int | float, int | float], int | float]] = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.FloorDiv: operator.floordiv,
    ast.Mod: operator.mod,
    ast.Pow: operator.pow,
}
_UNARY_OPERATORS: dict[type[ast.unaryop], Callable[[int | float], int | float]] = {
    ast.UAdd: operator.pos,
    ast.USub: operator.neg,
}


def calculator(expression: str) -> str:
    """Safely evaluate a numeric expression using a strict AST whitelist."""
    try:
        tree = ast.parse(expression, mode="eval")
        value = _evaluate_expression(tree.body)
    except (SyntaxError, TypeError, ValueError, ZeroDivisionError) as error:
        return f"Error: invalid calculation ({error})"
    return str(value)


def _evaluate_expression(node: ast.expr) -> int | float:
    if isinstance(node, ast.Constant) and type(node.value) in {int, float}:
        return node.value
    if isinstance(node, ast.BinOp) and type(node.op) in _BINARY_OPERATORS:
        return _BINARY_OPERATORS[type(node.op)](
            _evaluate_expression(node.left), _evaluate_expression(node.right)
        )
    if isinstance(node, ast.UnaryOp) and type(node.op) in _UNARY_OPERATORS:
        return _UNARY_OPERATORS[type(node.op)](_evaluate_expression(node.operand))
    raise ValueError("only numeric arithmetic is allowed")


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


class Agent:
    """A stateful single-call agent using the configured local Ollama model."""

    def __init__(self, system_prompt: str, model: str = settings.OLLAMA_MODEL) -> None:
        self.model = model
        self.messages: list[dict[str, Any]] = [{"role": "system", "content": system_prompt}]

    def run(self, user_input: str) -> str:
        self.messages.append({"role": "user", "content": user_input})
        response = chat(self.messages, model=self.model)
        reply = response["response_content"].strip()
        self.messages.append({"role": "assistant", "content": reply})
        return reply


class ToolAgent(Agent):
    """An agent that can perform one calculator round-trip per user request."""

    def __init__(self, system_prompt: str, model: str = settings.OLLAMA_MODEL) -> None:
        super().__init__(system_prompt, model)
        self.tool_call_count = 0

    def _call_model(self) -> dict[str, Any]:
        return chat(self.messages, model=self.model, tools=[CALCULATOR_TOOL])

    def _run_tool_calls(self, response: dict[str, Any]) -> None:
        self.messages.append(_assistant_message(response))
        for call in response["tool_calls"]:
            self.tool_call_count += 1
            try:
                arguments = json.loads(call.function.arguments)
                expression = arguments["expression"]
                result = calculator(expression)
            except (json.JSONDecodeError, KeyError, TypeError) as error:
                result = f"Error: invalid calculator arguments ({error})"
            self.messages.append({"role": "tool", "tool_call_id": call.id, "content": result})

    def run(self, user_input: str) -> str:
        self.messages.append({"role": "user", "content": user_input})
        response = self._call_model()
        if not response.get("tool_calls"):
            reply = response["response_content"].strip()
            self.messages.append({"role": "assistant", "content": reply})
            return reply

        self._run_tool_calls(response)
        final_response = self._call_model()
        reply = final_response["response_content"].strip()
        self.messages.append(_assistant_message(final_response))
        return reply


class LoopingToolAgent(ToolAgent):
    """A calculator agent with a hard limit for sequential tool-call rounds."""

    def __init__(
        self,
        system_prompt: str,
        model: str = settings.OLLAMA_MODEL,
        max_iterations: int = 5,
    ) -> None:
        super().__init__(system_prompt, model)
        if max_iterations < 1:
            raise ValueError("max_iterations must be at least 1")
        self.max_iterations = max_iterations
        self.iterations = 0

    def run(self, user_input: str) -> str:
        self.messages.append({"role": "user", "content": user_input})
        for iteration in range(1, self.max_iterations + 1):
            self.iterations = iteration
            response = self._call_model()
            if not response.get("tool_calls"):
                reply = response["response_content"].strip()
                self.messages.append({"role": "assistant", "content": reply})
                return reply
            self._run_tool_calls(response)
        raise RuntimeError(f"agent exceeded its {self.max_iterations}-iteration tool-call limit")
