"""Phase 11: 05 -- build a (chosen, rejected) preference dataset from critique-loop outputs.

Format matches a standard DPO/RLHF pairwise-preference dataset:
`{"task_id", "prompt", "chosen", "rejected"}`. Actual fine-tuning is out of
scope for local Ollama -- this only produces the data in the right shape.
"""
from __future__ import annotations

import json
import sys
from dataclasses import asdict, dataclass
from importlib import import_module
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))

OUTPUT_PATH = Path(__file__).resolve().parent / "preference_pairs.jsonl"


@dataclass
class PreferencePair:
    task_id: str
    prompt: str
    chosen: str
    rejected: str

    def to_dict(self) -> dict:
        return asdict(self)


def build_preference_pair(task_id: str, prompt: str, trajectory) -> PreferencePair | None:
    """Turn one critique-loop Trajectory into a (chosen, rejected) pair:
    the first position taken vs. the final, agreed-upon position."""
    if not trajectory.steps:
        return None
    initial = trajectory.steps[0].get("position", "")
    final = trajectory.final
    if not initial or not final or initial.strip() == final.strip():
        return None
    return PreferencePair(task_id=task_id, prompt=prompt, chosen=final, rejected=initial)


def write_pairs(pairs: list[PreferencePair], path: Path | None = None) -> Path:
    target = path or OUTPUT_PATH
    target.parent.mkdir(parents=True, exist_ok=True)
    with target.open("w", encoding="utf-8") as f:
        for pair in pairs:
            f.write(json.dumps(pair.to_dict()) + "\n")
    return target


def build_dataset_from_critique_loop(questions: list[str]) -> list[PreferencePair]:
    critique_loop = import_module("05_loops.critique_loop")
    pairs = []
    for i, question in enumerate(questions):
        trajectory = critique_loop.run_critique_loop(question)
        pair = build_preference_pair(task_id=f"pref-{i}", prompt=question, trajectory=trajectory)
        if pair is not None:
            pairs.append(pair)
    return pairs


def main() -> None:
    questions = [
        "Should companies allow fully remote work?",
        "Is 0 a natural number?",
    ]
    pairs = build_dataset_from_critique_loop(questions)
    target = write_pairs(pairs)
    print(f"wrote {len(pairs)} preference pairs to {target}")


if __name__ == "__main__":
    main()
