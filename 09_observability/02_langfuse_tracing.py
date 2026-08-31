"""Phase 10: 02 -- trace an agent run with Langfuse's nested spans.

`pip install langfuse` first, and set `LANGFUSE_PUBLIC_KEY` /
`LANGFUSE_SECRET_KEY` / `LANGFUSE_HOST` in `.env` if using a local Langfuse
docker-compose stack (`infra/docker-compose.yml`).
"""
from __future__ import annotations

import sys
from importlib import import_module
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))


def run_traced(question: str) -> tuple[str, list[str]]:
    from langfuse import Langfuse

    langfuse = Langfuse()
    MultiToolAgent = import_module("03_tools.tool_agent").MultiToolAgent

    trace = langfuse.trace(name="langfuse-tracing-demo", input=question)
    agent_span = trace.span(name="agent-run", input=question)
    agent = MultiToolAgent(system_prompt="Answer using calculator/sqlite tools.", max_iterations=5)
    answer = agent.run(question)
    for tool_name in agent.tool_calls_made:
        agent_span.span(name=f"tool:{tool_name}")
    agent_span.end(output=answer)
    trace.update(output=answer)
    langfuse.flush()
    return answer, agent.tool_calls_made


def main() -> None:
    question = " ".join(sys.argv[1:]) or "How many employees are in Sales, times 12?"
    try:
        answer, tool_calls = run_traced(question)
    except ImportError as error:
        print(f"langfuse not installed, skipping: {error}")
        return
    print(f"answer: {answer}")
    print(f"tools used: {tool_calls}")
    print("view the trace tree in the Langfuse UI (LANGFUSE_HOST, default http://localhost:3000)")


if __name__ == "__main__":
    main()
