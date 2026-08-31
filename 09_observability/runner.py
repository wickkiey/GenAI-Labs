"""Phase 10: runs the golden dataset against one or more agent "frameworks",
scoring each answer and appending rows to `results/frameworks.csv`.

Resumable: re-running skips (task_id, framework) pairs already present in the CSV.
"""
from __future__ import annotations

import argparse
import csv
import json
import sys
import time
from importlib import import_module
from pathlib import Path
from typing import Callable

sys.path.append(str(Path(__file__).resolve().parents[1]))

try:
    from .evaluators import exact_match, numeric_tolerance
except ImportError:
    from evaluators import exact_match, numeric_tolerance

DATASET_PATH = Path(__file__).resolve().parent / "datasets" / "tasks.json"
RESULTS_DIR = Path(__file__).resolve().parent / "results"
FIELDNAMES = ["task_id", "framework", "category", "question", "correct", "latency_ms", "tool_calls"]


def load_dataset() -> list[dict]:
    return json.loads(DATASET_PATH.read_text(encoding="utf-8"))


def run_handwritten_agent(question: str) -> tuple[str, list[str]]:
    MultiToolAgent = import_module("03_tools.tool_agent").MultiToolAgent
    agent = MultiToolAgent(
        system_prompt=(
            "Answer using the calculator and sqlite tools as needed. "
            "Reply with just the final short answer, e.g. a number or short phrase."
        ),
        max_iterations=5,
    )
    answer = agent.run(question)
    return answer, agent.tool_calls_made


FRAMEWORKS: dict[str, Callable[[str], tuple[str, list[str]]]] = {
    "handwritten": run_handwritten_agent,
}


def _existing_keys(csv_path: Path) -> set[tuple[str, str]]:
    if not csv_path.exists():
        return set()
    with csv_path.open(encoding="utf-8", newline="") as f:
        return {(row["task_id"], row["framework"]) for row in csv.DictReader(f)}


def score_task(task: dict, answer: str) -> bool:
    if task["category"] in ("calculator", "multi_hop"):
        try:
            expected = float(task["expected_answer"])
        except ValueError:
            return exact_match(task["expected_answer"], answer)
        return numeric_tolerance(expected, answer)
    return exact_match(task["expected_answer"], answer)


def run(framework: str, dataset: list[dict], csv_path: Path | None = None) -> Path:
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    csv_path = csv_path or (RESULTS_DIR / "frameworks.csv")
    existing = _existing_keys(csv_path)
    write_header = not csv_path.exists() or csv_path.stat().st_size == 0

    run_fn = FRAMEWORKS[framework]
    with csv_path.open("a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDNAMES)
        if write_header:
            writer.writeheader()
        for task in dataset:
            if (task["id"], framework) in existing:
                continue
            start = time.perf_counter()
            try:
                answer, tool_calls = run_fn(task["question"])
                correct = score_task(task, answer)
            except Exception:  # noqa: BLE001 - a failed task is still a recorded result
                answer, tool_calls, correct = "", [], False
            latency_ms = round((time.perf_counter() - start) * 1000, 1)
            writer.writerow(
                {
                    "task_id": task["id"],
                    "framework": framework,
                    "category": task["category"],
                    "question": task["question"],
                    "correct": correct,
                    "latency_ms": latency_ms,
                    "tool_calls": "|".join(tool_calls),
                }
            )
            f.flush()
    return csv_path


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--framework", default="all")
    parser.add_argument("--dataset", default="all")
    args = parser.parse_args()

    dataset = load_dataset()
    frameworks = list(FRAMEWORKS) if args.framework == "all" else [args.framework]
    csv_path = RESULTS_DIR / "frameworks.csv"
    for framework in frameworks:
        csv_path = run(framework, dataset)
    print(f"wrote results to {csv_path}")


if __name__ == "__main__":
    main()
