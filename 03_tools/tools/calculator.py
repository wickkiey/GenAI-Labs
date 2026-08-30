from __future__ import annotations

import ast
import operator
from collections.abc import Callable

try:
    from .registry import register_tool
except ImportError:
    from registry import register_tool

CALCULATOR_SCHEMA = {
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


@register_tool(CALCULATOR_SCHEMA)
def calculator(expression: str) -> str:
    """Safely evaluate a numeric expression using a strict AST whitelist (never raw eval)."""
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
