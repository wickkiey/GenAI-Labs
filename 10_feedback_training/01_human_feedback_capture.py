"""Phase 11: 01 -- capture human feedback (thumbs up/down + a correction) per trace.

Feedback rows are linked to a Phase 10 `trace_id` so later phases (DSPy
optimization, prompt-patch loop, preference datasets) can pull real
corrections instead of only golden-dataset labels.
"""
from __future__ import annotations

import json
import sys
import time
from dataclasses import asdict, dataclass
from pathlib import Path

FEEDBACK_PATH = Path(__file__).resolve().parent / "feedback.jsonl"


@dataclass
class Feedback:
    trace_id: str
    rating: str  # "up" or "down"
    comment: str = ""
    timestamp: float = 0.0

    def to_dict(self) -> dict:
        return asdict(self)


def capture_feedback(trace_id: str, rating: str, comment: str = "", path: Path | None = None) -> Feedback:
    if rating not in ("up", "down"):
        raise ValueError("rating must be 'up' or 'down'")
    feedback = Feedback(trace_id=trace_id, rating=rating, comment=comment, timestamp=time.time())
    target = path or FEEDBACK_PATH
    target.parent.mkdir(parents=True, exist_ok=True)
    with target.open("a", encoding="utf-8") as f:
        f.write(json.dumps(feedback.to_dict()) + "\n")
    return feedback


def load_feedback(path: Path | None = None) -> list[dict]:
    target = path or FEEDBACK_PATH
    if not target.exists():
        return []
    return [json.loads(line) for line in target.read_text(encoding="utf-8").splitlines() if line.strip()]


def main() -> None:
    if len(sys.argv) < 3:
        print("usage: python 01_human_feedback_capture.py <trace_id> <up|down> [comment]")
        return
    trace_id, rating = sys.argv[1], sys.argv[2]
    comment = " ".join(sys.argv[3:])
    feedback = capture_feedback(trace_id, rating, comment)
    print(f"recorded: {feedback.to_dict()}")


if __name__ == "__main__":
    main()
