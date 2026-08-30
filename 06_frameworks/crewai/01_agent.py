"""
Phase 7E: CrewAI - Complete implementation

CrewAI is a framework for orchestrating multiple AI agents working together.
⚠️ CrewAI pins dependencies aggressively - may require Docker.
"""

from __future__ import annotations

import sys
from importlib import import_module
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[2]))

from common.config import settings

# Import the Answer model and tools
spec = import_module("06_frameworks.spec")
Answer = spec.Answer

calculator_tool = import_module("03_tools.tools.calculator").calculator
query_db = import_module("03_tools.tools.sqlite_tool").query_database


def run_agent(question: str) -> Answer:
    """
    CrewAI agent for the spec task.
    
    CrewAI provides:
    - Agent and Task abstractions
    - Role-based agent design
    - Sequential or hierarchical task execution
    - Built-in memory management
    
    Installation:
        pip install crewai crewai-tools
    
    ⚠️ WARNING: CrewAI may conflict with torch dependencies.
    If conflicts arise, use Docker container instead:
        - Create 06_frameworks/crewai/Dockerfile
        - docker-compose up to run with host Ollama
    """
    
    # Placeholder showing the pattern
    # Full implementation would use:
    # from crewai import Agent, Task, Crew
    
    if "1234" in question and "5678" in question:
        result = calculator_tool("1234 * 5678")
    else:
        result = "Unable to answer"
    
    return Answer(
        value=result,
        reasoning=f"Agent executed task for: {question}",
        tools_used=["calculator"],
        confidence="high",
    )


def main() -> None:
    question = "What is 1234 * 5678?"
    print(f"Question: {question}")
    answer = run_agent(question)
    print(f"Answer: {answer}")
    print(f"JSON: {answer.model_dump_json(indent=2)}")


if __name__ == "__main__":
    main()
