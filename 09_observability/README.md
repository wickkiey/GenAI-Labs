# Phase 10: Observability & Tracing

Traces the same hand-written agent run (`03_tools.tool_agent.MultiToolAgent`)
through four popular tools, plus a shared vendor-neutral `@traced` decorator
(`common/trace.py`) used everywhere so trace data always exists even when a
given SDK isn't installed.

| File | Backend | Notes |
| --- | --- | --- |
| `01_mlflow_tracing.py` | MLflow | local file store (`./mlruns`), no server needed |
| `02_langfuse_tracing.py` | Langfuse | nested spans per LLM/tool call, needs `LANGFUSE_*` env vars |
| `03_phoenix_tracing.py` | Arize Phoenix | OpenInference/OTel-native, in-process UI at :6006 |
| `04_openllmetry_otel.py` | OpenLLMetry (Traceloop) | vendor-neutral OpenTelemetry, console or OTLP export |
| `05_compare_backends.py` | all four | one task, traced everywhere at once |

Each script prints `"<package> not installed, skipping"` instead of failing
if its SDK isn't installed -- see `requirements/phase10.txt` for install lines.

Evaluation harness (`datasets/`, `evaluators/`, `runner.py`, `report.py`) is
the same one described in the original Phase 10 plan: 30 golden tasks
(calculator / sqlite / multi-hop), scored with exact-match / numeric
tolerance / LLM-as-judge / tool-selection-accuracy evaluators.

Run:

```powershell
python 09_observability/01_mlflow_tracing.py
python 09_observability/02_langfuse_tracing.py
python 09_observability/03_phoenix_tracing.py
python 09_observability/04_openllmetry_otel.py
python 09_observability/05_compare_backends.py
python 09_observability/runner.py --framework all --dataset all
python 09_observability/report.py
pytest tests/test_observability.py -v
```

**What surprised me:** the `@traced`/`TraceRecord` layer only needs to know
about `(answer, tool_calls)` -- it doesn't care which of the four vendor
SDKs is also watching the same call, so it's the one trace you can always
rely on even with zero extra packages installed.
