from __future__ import annotations

import csv
import importlib
import json

import pytest

evaluators = importlib.import_module("09_observability.evaluators")
trace_module = importlib.import_module("common.trace")
runner_module = importlib.import_module("09_observability.runner")


def test_exact_match() -> None:
    assert evaluators.exact_match("Engineering", " engineering ")
    assert not evaluators.exact_match("Engineering", "Sales")


def test_numeric_tolerance_finds_number_in_text() -> None:
    assert evaluators.numeric_tolerance(360.0, "15% of 2400 is 360.")
    assert evaluators.numeric_tolerance(7006652, "The result is 7,006,652.")
    assert not evaluators.numeric_tolerance(360.0, "the answer is 999")


def test_tool_selection_accuracy() -> None:
    assert evaluators.tool_selection_accuracy("query_database", ["list_tables", "query_database"])
    assert not evaluators.tool_selection_accuracy("calculator", ["query_database"])


def test_trace_record_is_json_serialisable() -> None:
    record = trace_module.TraceRecord(task="2+2", framework="handwritten", final_answer="4")
    json.dumps(record.to_dict())  # must not raise


def test_traced_decorator_appends_one_line_per_call(tmp_path) -> None:
    trace_path = tmp_path / "traces.jsonl"

    @trace_module.traced(framework="test", trace_path=trace_path)
    def fake_agent(task: str) -> tuple[str, list[str]]:
        return "42", ["calculator"]

    fake_agent("what is 6*7?")
    fake_agent("what is 7*6?")

    lines = trace_path.read_text(encoding="utf-8").strip().splitlines()
    assert len(lines) == 2
    record = json.loads(lines[0])
    assert record["final_answer"] == "42"
    assert record["tool_calls"] == [{"name": "calculator"}]
    assert record["success"] is True


def test_score_task_calculator_and_sqlite() -> None:
    calc_task = {"category": "calculator", "expected_answer": "360"}
    assert runner_module.score_task(calc_task, "The answer is 360.")
    sql_task = {"category": "sqlite", "expected_answer": "Engineering"}
    assert runner_module.score_task(sql_task, "engineering")


def test_runner_is_resumable(tmp_path, monkeypatch: pytest.MonkeyPatch) -> None:
    calls = {"n": 0}

    def _fake_run(question: str) -> tuple[str, list[str]]:
        calls["n"] += 1
        return "4", ["calculator"]

    monkeypatch.setitem(runner_module.FRAMEWORKS, "fake", _fake_run)
    dataset = [{"id": "t1", "category": "calculator", "question": "2+2", "expected_answer": "4"}]
    csv_path = tmp_path / "frameworks.csv"

    runner_module.run("fake", dataset, csv_path=csv_path)
    runner_module.run("fake", dataset, csv_path=csv_path)  # rerun: should not duplicate

    with csv_path.open(encoding="utf-8", newline="") as f:
        rows = list(csv.DictReader(f))
    assert len(rows) == 1
    assert calls["n"] == 1
