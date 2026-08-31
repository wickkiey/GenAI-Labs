from __future__ import annotations

import json
import time
from dataclasses import asdict, dataclass, field
from functools import wraps
from pathlib import Path
from typing import Any, Callable

TRACE_DIR = Path(__file__).resolve().parents[1] / "09_observability" / "traces"
DEFAULT_TRACE_PATH = TRACE_DIR / "traces.jsonl"


@dataclass
class TraceRecord:
    """One row of `09_observability/traces/*.jsonl` -- the shared trace schema for Phase 10."""

    task: str
    framework: str
    model: str = ""
    tool_calls: list[dict[str, Any]] = field(default_factory=list)
    steps: list[dict[str, Any]] = field(default_factory=list)
    final_answer: str = ""
    latency_ms: float = 0.0
    tokens: int = 0
    success: bool = True

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def append_trace(record: TraceRecord, path: Path | None = None) -> None:
    target = path or DEFAULT_TRACE_PATH
    target.parent.mkdir(parents=True, exist_ok=True)
    with target.open("a", encoding="utf-8") as f:
        f.write(json.dumps(record.to_dict()) + "\n")


def traced(
    framework: str, model: str = "", trace_path: Path | None = None
) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
    """Wrap a `fn(task, ...) -> answer` or `fn(task, ...) -> (answer, tool_calls)`
    callable so every call appends a `TraceRecord` (latency, success, tool
    calls) to a JSONL file, independent of which backend (MLflow, Langfuse,
    Phoenix, OTel) is also tracing the same call.
    """

    def decorator(fn: Callable[..., Any]) -> Callable[..., Any]:
        @wraps(fn)
        def wrapper(task: str, *args: Any, **kwargs: Any) -> Any:
            start = time.perf_counter()
            success = True
            answer: Any = ""
            tool_calls: list[dict[str, Any]] = []
            try:
                result = fn(task, *args, **kwargs)
                if isinstance(result, tuple) and len(result) == 2:
                    answer, raw_tool_calls = result
                    tool_calls = [
                        {"name": call} if isinstance(call, str) else call for call in raw_tool_calls
                    ]
                else:
                    answer = result
                return result
            except Exception:
                success = False
                raise
            finally:
                latency_ms = (time.perf_counter() - start) * 1000
                append_trace(
                    TraceRecord(
                        task=task,
                        framework=framework,
                        model=model,
                        tool_calls=tool_calls,
                        final_answer=str(answer),
                        latency_ms=latency_ms,
                        success=success,
                    ),
                    trace_path,
                )

        return wrapper

    return decorator
