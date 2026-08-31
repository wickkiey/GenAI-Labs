"""Sequential handoff: a Researcher agent gathers facts with tools, a Writer agent
turns those facts into prose. The writer never touches a tool - it can only know
what the researcher handed it, which is what makes this pattern testable.
"""

from __future__ import annotations

import sys
from importlib import import_module
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[2]))
sys.path.append(str(Path(__file__).resolve().parents[1]))

from common.config import settings
from common.llm import chat

try:
    from ..trajectory import Trajectory
except ImportError:
    from trajectory import Trajectory

MultiToolAgent = import_module("03_tools.tool_agent").MultiToolAgent

RESEARCHER_TOOLS = ["list_tables", "describe_table", "query_database"]


def run_researcher_writer(question: str, max_iterations: int = 4) -> Trajectory:
    """Researcher retrieves facts via tools -> Writer composes the final answer from them."""
    trajectory = Trajectory()

    researcher = MultiToolAgent(
        "You are a Researcher. Use the list_tables, describe_table, and query_database "
        "tools to find the exact facts (numbers, names) needed to answer the question. "
        "Reply with a short bullet list of raw facts only - no narrative.",
        model=settings.OLLAMA_MODEL,
        max_iterations=max_iterations,
        tool_names=RESEARCHER_TOOLS,
    )
    research_notes = researcher.run(question)
    trajectory.tool_calls.extend({"name": name} for name in researcher.tool_calls_made)
    trajectory.steps.append(
        {"agent": "researcher", "output": research_notes, "tool_calls": list(researcher.tool_calls_made)}
    )

    writer_reply = chat(
        [
            {
                "role": "system",
                "content": (
                    "You are a Writer. Using ONLY the facts provided below, write a "
                    "2-3 sentence answer to the question. Do not invent any facts and "
                    "do not use any tools."
                ),
            },
            {"role": "user", "content": f"Question: {question}\n\nResearcher facts:\n{research_notes}"},
        ],
        model=settings.OLLAMA_MODEL,
    )["response_content"].strip()
    trajectory.steps.append({"agent": "writer", "output": writer_reply})
    trajectory.iterations = 2
    trajectory.final = writer_reply
    return trajectory


def main() -> None:
    question = " ".join(sys.argv[1:]) or "Which department has the highest total sales, and by how much?"
    trajectory = run_researcher_writer(question)
    print(trajectory.final)
    print(f"researcher tool calls: {[c['name'] for c in trajectory.tool_calls]}")


if __name__ == "__main__":
    main()
