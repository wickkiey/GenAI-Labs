"""
Phase 7: Invariant Task Specification for Framework Comparison

All six frameworks (PydanticAI, LangChain, LangGraph, Strands, CrewAI, AutoGen)
solve the same task using the same tools, model, and temperature.

Task: "Answer the question using calculator + sqlite tools, verify the result,
and return Answer(value, reasoning, tools_used, confidence)."
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal


@dataclass
class Answer:
    """Standard answer format across all frameworks."""

    value: str
    """The final answer to the question."""

    reasoning: str
    """Why this answer is correct."""

    tools_used: list[str]
    """Which tools were called: ['calculator'], ['sqlite'], or both."""

    confidence: Literal["high", "medium", "low"]
    """Confidence in the answer."""


# 10 standardised test questions for all frameworks
TEST_QUESTIONS = [
    # Calculator-only (4)
    "What is 1234 * 5678?",
    "What is 15% of 2400?",
    "Calculate (100 + 50) / 2",
    "What is the square root of 144? (approximate)",
    # SQLite-only (3)
    "How many employees are in the Sales department?",
    "What is the total sales for all departments?",
    "Which department has the highest total sales?",
    # Multi-hop (3)
    "What is 10% of the highest total sales?",
    "If each Sales employee earns 10000, what's the total wage bill for Sales?",
    "Which department has the second-highest employee count?",
]

EXPECTED_ANSWERS = {
    "What is 1234 * 5678?": {
        "tools": ["calculator"],
        "answer_pattern": "7006652",
    },
    "What is 15% of 2400?": {
        "tools": ["calculator"],
        "answer_pattern": "360",
    },
    "Calculate (100 + 50) / 2": {
        "tools": ["calculator"],
        "answer_pattern": "75",
    },
    "What is the square root of 144? (approximate)": {
        "tools": ["calculator"],
        "answer_pattern": "12",
    },
    "How many employees are in the Sales department?": {
        "tools": ["sqlite"],
        "answer_pattern": "number",
    },
    "What is the total sales for all departments?": {
        "tools": ["sqlite"],
        "answer_pattern": "number",
    },
    "Which department has the highest total sales?": {
        "tools": ["sqlite"],
        "answer_pattern": "Sales",
    },
}
