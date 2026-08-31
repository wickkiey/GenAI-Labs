"""Phase 11: 06 -- wire it together end-to-end, fully automated and rerunnable.

run eval -> capture failures -> optimize (prompt-patch) -> re-run eval ->
assert the score improved (or at least did not regress, thanks to the
regression guard in `04_prompt_feedback_loop.py`).
"""
from __future__ import annotations

import json
import sys
from importlib import import_module
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))

_pfl = import_module("10_feedback_training.04_prompt_feedback_loop")
PromptCandidate = _pfl.PromptCandidate
evaluate = _pfl.evaluate
improve_with_regression_guard = _pfl.improve_with_regression_guard

RESULTS_PATH = Path(__file__).resolve().parent / "closed_loop_results.json"

DATASET = [
    {"question": "What is 15% of 2400?", "expected_answer": "360"},
    {"question": "What is 1234 * 5678?", "expected_answer": "7006652"},
    {"question": "What is 9999 - 4567?", "expected_answer": "5432"},
    {"question": "What is 45 * 45?", "expected_answer": "2025"},
]


def run_closed_loop(candidate: PromptCandidate, dataset: list[dict], run_fn=None) -> dict:
    kwargs = {"run_fn": run_fn} if run_fn is not None else {}
    improved, before_score, after_score = improve_with_regression_guard(candidate, dataset, **kwargs)
    result = {
        "before_score": before_score,
        "after_score": after_score,
        "few_shot_examples_kept": len(improved.few_shot),
        "improved": after_score >= before_score,
    }
    RESULTS_PATH.write_text(json.dumps(result, indent=2), encoding="utf-8")
    return result


def main() -> None:
    baseline = PromptCandidate(system_prompt="Answer with just the final number.")
    result = run_closed_loop(baseline, DATASET)
    print(json.dumps(result, indent=2))
    assert result["after_score"] >= result["before_score"], "closed loop must never regress the score"


if __name__ == "__main__":
    main()

