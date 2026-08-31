"""Phase 10: 03 -- trace an agent run with Arize Phoenix (OpenInference/OTel-native).

`pip install arize-phoenix openinference-instrumentation-openai` first.
Phoenix runs an in-process collector + UI by default (http://localhost:6006).
"""
from __future__ import annotations

import sys
from importlib import import_module
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))


def run_traced(question: str) -> tuple[str, list[str]]:
    import phoenix as px
    from openinference.instrumentation.openai import OpenAIInstrumentor
    from phoenix.otel import register

    px.launch_app()
    tracer_provider = register(project_name="genai-labs-observability")
    OpenAIInstrumentor().instrument(tracer_provider=tracer_provider)

    MultiToolAgent = import_module("03_tools.tool_agent").MultiToolAgent
    agent = MultiToolAgent(system_prompt="Answer using calculator/sqlite tools.", max_iterations=5)
    answer = agent.run(question)
    return answer, agent.tool_calls_made


def main() -> None:
    question = " ".join(sys.argv[1:]) or "How many employees are in Sales, times 12?"
    try:
        answer, tool_calls = run_traced(question)
    except ImportError as error:
        print(f"arize-phoenix / openinference not installed, skipping: {error}")
        return
    print(f"answer: {answer}")
    print(f"tools used: {tool_calls}")
    print("view spans + built-in evals at http://localhost:6006")


if __name__ == "__main__":
    main()
