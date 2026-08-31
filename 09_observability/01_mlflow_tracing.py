"""Phase 10: 01 -- trace an agent run with MLflow's LLM tracing.

`pip install mlflow` first. Uses a local file-based tracking store
(`./mlruns`), so no server is required to try this.
"""
from __future__ import annotations

import sys
from importlib import import_module
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))


def run_traced(question: str) -> tuple[str, list[str]]:
    import mlflow

    mlflow.set_tracking_uri(f"file:{Path(__file__).resolve().parent / 'mlruns'}")
    mlflow.set_experiment("genai-labs-observability")

    MultiToolAgent = import_module("03_tools.tool_agent").MultiToolAgent

    with mlflow.start_run(run_name="mlflow-tracing-demo"):
        mlflow.log_param("question", question)
        with mlflow.start_span(name="agent-run") as span:
            agent = MultiToolAgent(system_prompt="Answer using calculator/sqlite tools.", max_iterations=5)
            answer = agent.run(question)
            span.set_attribute("tool_calls", agent.tool_calls_made)
        mlflow.log_metric("tool_call_count", len(agent.tool_calls_made))
        mlflow.log_text(answer, "answer.txt")
    return answer, agent.tool_calls_made


def main() -> None:
    question = " ".join(sys.argv[1:]) or "How many employees are in Sales, times 12?"
    try:
        answer, tool_calls = run_traced(question)
    except ImportError as error:
        print(f"mlflow not installed, skipping: {error}")
        return
    print(f"answer: {answer}")
    print(f"tools used: {tool_calls}")
    print("view with: mlflow ui --backend-store-uri file:./09_observability/mlruns")


if __name__ == "__main__":
    main()
