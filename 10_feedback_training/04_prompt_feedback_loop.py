"""Phase 11: 04 -- a hand-written prompt-patch loop with a regression guard (no framework).

Failed tasks become new few-shot examples; the patched prompt is only kept
if it scores at least as well as the baseline on the same dataset.
"""
from __future__ import annotations

import sys
from dataclasses import dataclass, field
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))

from common.config import settings
from common.llm import chat


@dataclass
class PromptCandidate:
    system_prompt: str
    few_shot: list[dict] = field(default_factory=list)


def render_prompt(candidate: PromptCandidate) -> str:
    lines = [candidate.system_prompt]
    for example in candidate.few_shot:
        lines.append(f"Q: {example['question']}\nA: {example['answer']}")
    return "\n".join(lines)


def run_candidate(candidate: PromptCandidate, question: str) -> str:
    system_prompt = render_prompt(candidate)
    response = chat(
        [{"role": "system", "content": system_prompt}, {"role": "user", "content": question}],
        model=settings.OLLAMA_MODEL,
    )
    return response["response_content"].strip()


def evaluate(candidate: PromptCandidate, dataset: list[dict], run_fn=run_candidate) -> float:
    """Fraction of `dataset` answered correctly (case-insensitive substring match)."""
    if not dataset:
        return 0.0
    correct = sum(
        1
        for item in dataset
        if item["expected_answer"].strip().lower() in run_fn(candidate, item["question"]).lower()
    )
    return correct / len(dataset)


def propose_patch(candidate: PromptCandidate, dataset: list[dict], run_fn=run_candidate) -> PromptCandidate:
    """Add one few-shot example per currently-failing task -- the simplest possible prompt patch."""
    new_examples = list(candidate.few_shot)
    for item in dataset:
        answer = run_fn(candidate, item["question"])
        if item["expected_answer"].strip().lower() not in answer.lower():
            new_examples.append({"question": item["question"], "answer": item["expected_answer"]})
    return PromptCandidate(system_prompt=candidate.system_prompt, few_shot=new_examples)


def apply_if_improved(
    baseline: PromptCandidate, candidate: PromptCandidate, dataset: list[dict], run_fn=run_candidate
) -> tuple[PromptCandidate, float, float]:
    """The regression guard: keep `candidate` only if it scores >= `baseline` on `dataset`."""
    baseline_score = evaluate(baseline, dataset, run_fn)
    candidate_score = evaluate(candidate, dataset, run_fn)
    if candidate_score >= baseline_score:
        return candidate, baseline_score, candidate_score
    return baseline, baseline_score, baseline_score


def improve_with_regression_guard(
    candidate: PromptCandidate, dataset: list[dict], run_fn=run_candidate
) -> tuple[PromptCandidate, float, float]:
    patched = propose_patch(candidate, dataset, run_fn)
    return apply_if_improved(candidate, patched, dataset, run_fn)


def main() -> None:
    dataset = [
        {"question": "What is 15% of 2400?", "expected_answer": "360"},
        {"question": "What is 1234 * 5678?", "expected_answer": "7006652"},
        {"question": "What is 9999 - 4567?", "expected_answer": "5432"},
    ]
    baseline = PromptCandidate(system_prompt="Answer with just the final number.")
    improved, before, after = improve_with_regression_guard(baseline, dataset)
    print(f"baseline accuracy: {before:.0%}")
    print(f"patched accuracy:  {after:.0%}")
    print(f"few-shot examples kept: {len(improved.few_shot)}")


if __name__ == "__main__":
    main()
