from __future__ import annotations

import re
import sys
from importlib import import_module
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))

from common.config import settings
from common.llm import chat

try:
    from .trajectory import Trajectory
except ImportError:
    from trajectory import Trajectory

calculator = import_module("03_tools.tools.calculator").calculator

SYSTEM_PROMPT = """You solve problems using a Thought / Action / Observation loop.
On each turn output exactly one of:
Thought: <your reasoning>
Action: calculator[<expression>]
or, once you know the final answer:
Thought: <your reasoning>
FINAL: <answer>
Never output anything else."""

ACTION_RE = re.compile(r"Action:\s*calculator\[(.*?)\]", re.DOTALL)
FINAL_RE = re.compile(r"FINAL:\s*(.+)", re.DOTALL)


def run_react(question: str, max_steps: int = 5) -> Trajectory:
    """Thought -> Action -> Observation loop that stops on a FINAL marker or max_steps."""
    trajectory = Trajectory()
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": question},
    ]
    for step in range(1, max_steps + 1):
        trajectory.iterations = step
        response = chat(messages, model=settings.OLLAMA_MODEL)
        text = response["response_content"].strip()
        messages.append({"role": "assistant", "content": text})

        final_match = FINAL_RE.search(text)
        if final_match:
            trajectory.steps.append({"step": step, "content": text})
            trajectory.final = final_match.group(1).strip()
            return trajectory

        action_match = ACTION_RE.search(text)
        if not action_match:
            trajectory.steps.append({"step": step, "content": text})
            trajectory.final = text
            return trajectory

        expression = action_match.group(1).strip()
        observation = calculator(expression)
        trajectory.tool_calls.append(
            {"name": "calculator", "arguments": {"expression": expression}, "result": observation}
        )
        trajectory.steps.append({"step": step, "content": text, "observation": observation})
        messages.append({"role": "user", "content": f"Observation: {observation}"})

    trajectory.final = "(max steps reached without a FINAL answer)"
    return trajectory
