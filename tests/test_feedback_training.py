from __future__ import annotations

import importlib
import json
from types import SimpleNamespace

import pytest

feedback_module = importlib.import_module("10_feedback_training.01_human_feedback_capture")
preference_module = importlib.import_module("10_feedback_training.05_preference_dataset")
pfl_module = importlib.import_module("10_feedback_training.04_prompt_feedback_loop")
closed_loop_module = importlib.import_module("10_feedback_training.06_closed_loop_eval")


def test_capture_feedback_rejects_invalid_rating() -> None:
    with pytest.raises(ValueError):
        feedback_module.capture_feedback("trace-1", "meh")


def test_capture_and_load_feedback_roundtrip(tmp_path) -> None:
    path = tmp_path / "feedback.jsonl"
    feedback_module.capture_feedback("trace-1", "up", "great answer", path=path)
    feedback_module.capture_feedback("trace-2", "down", "wrong number", path=path)

    loaded = feedback_module.load_feedback(path=path)
    assert len(loaded) == 2
    assert loaded[0]["trace_id"] == "trace-1"
    assert loaded[1]["rating"] == "down"


def test_preference_pair_is_well_formed() -> None:
    trajectory = SimpleNamespace(
        steps=[{"round": 0, "agent": "A", "position": "Remote work is bad."}],
        final="Remote work is good, actually.",
    )
    pair = preference_module.build_preference_pair("pref-1", "Is remote work good?", trajectory)
    assert pair is not None
    assert pair.task_id == "pref-1"
    assert pair.chosen != pair.rejected
    assert pair.chosen and pair.rejected
    json.dumps(pair.to_dict())  # must not raise


def test_preference_pair_is_none_when_position_never_changed() -> None:
    trajectory = SimpleNamespace(
        steps=[{"round": 0, "agent": "A", "position": "Same answer."}], final="Same answer."
    )
    assert preference_module.build_preference_pair("pref-2", "question?", trajectory) is None


def test_propose_patch_adds_one_example_per_failure() -> None:
    dataset = [
        {"question": "2+2", "expected_answer": "4"},
        {"question": "3+3", "expected_answer": "6"},
    ]
    candidate = pfl_module.PromptCandidate(system_prompt="Answer.")
    patched = pfl_module.propose_patch(candidate, dataset, run_fn=lambda c, q: "wrong")
    assert len(patched.few_shot) == 2


def test_apply_if_improved_rejects_worse_candidate() -> None:
    dataset = [{"question": "2+2", "expected_answer": "4"}]
    baseline = pfl_module.PromptCandidate(system_prompt="Answer.")
    worse_candidate = pfl_module.PromptCandidate(
        system_prompt="Answer.", few_shot=[{"question": "x", "answer": "y"}]
    )

    def run_fn(candidate, question):
        return "4" if not candidate.few_shot else "wrong answer"

    kept, before, after = pfl_module.apply_if_improved(baseline, worse_candidate, dataset, run_fn)
    assert kept is baseline
    assert before == 1.0
    assert after == 1.0


def test_improve_with_regression_guard_keeps_improving_patch() -> None:
    dataset = [
        {"question": "2+2", "expected_answer": "4"},
        {"question": "3+3", "expected_answer": "6"},
    ]

    def run_fn(candidate, question):
        for example in candidate.few_shot:
            if example["question"] == question:
                return example["answer"]
        return "no idea"

    baseline = pfl_module.PromptCandidate(system_prompt="Answer.")
    improved, before, after = pfl_module.improve_with_regression_guard(baseline, dataset, run_fn=run_fn)
    assert before == 0.0
    assert after == 1.0
    assert len(improved.few_shot) == 2


def test_closed_loop_never_regresses_and_is_idempotent(tmp_path) -> None:
    def run_fn(candidate, question):
        for example in candidate.few_shot:
            if example["question"] == question:
                return example["answer"]
        return "no idea"

    closed_loop_module.RESULTS_PATH = tmp_path / "closed_loop_results.json"
    candidate = pfl_module.PromptCandidate(system_prompt="Answer.")
    dataset = closed_loop_module.DATASET[:2]

    first = closed_loop_module.run_closed_loop(candidate, dataset, run_fn=run_fn)
    assert first["after_score"] >= first["before_score"]

    # Rerunning against the already-improved candidate must not regress or crash.
    improved_candidate = pfl_module.PromptCandidate(
        system_prompt="Answer.", few_shot=dataset and [{"question": dataset[0]["question"], "answer": dataset[0]["expected_answer"]}]
    )
    second = closed_loop_module.run_closed_loop(improved_candidate, dataset, run_fn=run_fn)
    assert second["after_score"] >= second["before_score"]


def test_dspy_task_module_available_or_skips() -> None:
    dspy = pytest.importorskip("dspy")
    assert dspy is not None
