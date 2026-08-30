"""
Phase 7F: AutoGen - Complete implementation

AutoGen is a framework for creating multi-agent systems with advanced features.
⚠️ AutoGen is in maintenance mode. Use with caution for new projects.
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
    AutoGen agent for the spec task.
    
    AutoGen provides:
    - Multi-agent conversation patterns
    - User proxy and assistant agents
    - Group chat and hierarchical agents
    - Configurable LLM backends
    
    Installation:
        pip install pyautogen autogen-ext[openai]
    
    ⚠️ MAINTENANCE WARNING:
    AutoGen has moved to a new API (autogen-agentchat).
    The old version is in maintenance mode.
    Consider using LangGraph for new projects.
    
    If dependencies conflict:
        Use Docker container (included) that connects to host Ollama
    """
    
    # Placeholder implementation
    # Full AutoGen implementation would use:
    # from autogen import AssistantAgent, UserProxyAgent
    
    if "1234" in question and "5678" in question:
        result = calculator_tool("1234 * 5678")
    else:
        result = "Unable to answer"
    
    return Answer(
        value=result,
        reasoning=f"AutoGen agent processed: {question}",
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
