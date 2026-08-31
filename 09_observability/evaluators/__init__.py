"""Evaluator functions for Phase 10 -- pure functions, no LLM required except `llm_judge`."""
from __future__ import annotations

import re
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[2]))

from common.config import settings
from common.llm import chat

_NUMBER_RE = re.compile(r"-?\d[\d,]*\.?\d*")


def exact_match(expected: str, actual: str) -> bool:
    return expected.strip().lower() == actual.strip().lower()


def numeric_tolerance(expected: float, actual: str, tolerance: float = 0.01) -> bool:
    """True if any number found in `actual` is within `tolerance` (relative) of `expected`."""
    numbers = [float(n.replace(",", "")) for n in _NUMBER_RE.findall(actual)]
    if not numbers:
        return False
    allowed = max(tolerance * abs(expected), 1e-6)
    return any(abs(n - expected) <= allowed for n in numbers)


def tool_selection_accuracy(expected_tool: str, tool_calls: list[str]) -> bool:
    return expected_tool in tool_calls


def llm_judge(question: str, expected: str, actual: str) -> bool:
    """Ask the local model whether `actual` matches `expected` in substance."""
    prompt = (
        f"Question: {question}\nExpected answer: {expected}\nModel answer: {actual}\n"
        "Does the model answer match the expected answer in substance? Reply with exactly YES or NO."
    )
    response = chat([{"role": "user", "content": prompt}], model=settings.OLLAMA_MODEL)
    return response["response_content"].strip().upper().startswith("Y")
