"""Phase 10: 05 -- run one task once, traced simultaneously to all four backends.

Each backend's tracing call is wrapped so a missing package just prints a
skip notice instead of aborting the whole comparison.
"""
from __future__ import annotations

import sys
import time
from importlib import import_module
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))

from common.trace import TraceRecord, append_trace

BACKENDS = {
    "mlflow": "01_mlflow_tracing",
    "langfuse": "02_langfuse_tracing",
    "phoenix": "03_phoenix_tracing",
    "openllmetry": "04_openllmetry_otel",
}


def run_all(question: str) -> dict[str, dict]:
    results: dict[str, dict] = {}
    for backend_name, module_name in BACKENDS.items():
        module = import_module(f"09_observability.{module_name}")
        start = time.perf_counter()
        try:
            answer, tool_calls = module.run_traced(question)
            status = "ok"
        except ImportError as error:
            answer, tool_calls, status = "", [], f"skipped ({error})"
        latency_ms = round((time.perf_counter() - start) * 1000, 1)
        results[backend_name] = {
            "answer": answer,
            "tool_calls": tool_calls,
            "status": status,
            "latency_ms": latency_ms,
        }

        # Always append our own vendor-neutral trace regardless of backend availability.
        append_trace(
            TraceRecord(
                task=question,
                framework=backend_name,
                final_answer=str(answer),
                tool_calls=[{"name": t} for t in tool_calls],
                latency_ms=latency_ms,
                success=status == "ok",
            )
        )
    return results


def main() -> None:
    question = " ".join(sys.argv[1:]) or "How many employees are in Sales, times 12?"
    results = run_all(question)
    for backend_name, info in results.items():
        print(f"[{backend_name}] status={info['status']} latency_ms={info['latency_ms']} answer={info['answer']}")


if __name__ == "__main__":
    main()
