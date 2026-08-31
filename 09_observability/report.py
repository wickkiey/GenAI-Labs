"""Phase 10: render `results/frameworks.csv` as a markdown comparison table."""
from __future__ import annotations

import csv
from collections import defaultdict
from pathlib import Path

RESULTS_DIR = Path(__file__).resolve().parent / "results"
CSV_PATH = RESULTS_DIR / "frameworks.csv"


def build_report(csv_path: Path = CSV_PATH) -> str:
    if not csv_path.exists():
        return "No results yet -- run `runner.py` first."

    totals: dict[str, dict[str, float]] = defaultdict(lambda: {"n": 0, "correct": 0, "latency_ms": 0.0})
    with csv_path.open(encoding="utf-8", newline="") as f:
        for row in csv.DictReader(f):
            bucket = totals[row["framework"]]
            bucket["n"] += 1
            bucket["correct"] += 1 if row["correct"] in ("True", "true", "1") else 0
            bucket["latency_ms"] += float(row["latency_ms"])

    lines = ["| Framework | Accuracy | Avg latency (ms) | Tasks |", "| --- | --- | --- | --- |"]
    for framework, bucket in sorted(totals.items()):
        n = bucket["n"] or 1
        accuracy = bucket["correct"] / n
        avg_latency = bucket["latency_ms"] / n
        lines.append(f"| {framework} | {accuracy:.0%} | {avg_latency:.1f} | {int(bucket['n'])} |")
    return "\n".join(lines)


def main() -> None:
    print(build_report())


if __name__ == "__main__":
    main()
