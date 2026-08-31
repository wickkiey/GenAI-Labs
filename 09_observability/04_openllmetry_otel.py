"""Phase 10: 04 -- vendor-neutral tracing with OpenLLMetry (Traceloop) over OpenTelemetry.

`pip install traceloop-sdk` first. Exports spans to the console by default,
and to `otel-collector`/OTLP if `TRACELOOP_BASE_URL` is set, so the same
trace can fan out to any of the other three backends without touching agent code.
"""
from __future__ import annotations

import sys
from importlib import import_module
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))


def run_traced(question: str) -> tuple[str, list[str]]:
    from traceloop.sdk import Traceloop
    from traceloop.sdk.decorators import workflow

    Traceloop.init(app_name="genai-labs-observability", disable_batch=True)

    MultiToolAgent = import_module("03_tools.tool_agent").MultiToolAgent

    @workflow(name="agent-run")
    def _run() -> tuple[str, list[str]]:
        agent = MultiToolAgent(system_prompt="Answer using calculator/sqlite tools.", max_iterations=5)
        answer = agent.run(question)
        return answer, agent.tool_calls_made

    return _run()


def main() -> None:
    question = " ".join(sys.argv[1:]) or "How many employees are in Sales, times 12?"
    try:
        answer, tool_calls = run_traced(question)
    except ImportError as error:
        print(f"traceloop-sdk not installed, skipping: {error}")
        return
    print(f"answer: {answer}")
    print(f"tools used: {tool_calls}")
    print("spans printed to console; set TRACELOOP_BASE_URL to export via OTLP to any backend")


if __name__ == "__main__":
    main()
