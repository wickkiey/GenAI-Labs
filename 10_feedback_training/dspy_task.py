"""Shared DSPy scaffolding for `02_dspy_signatures.py` and `03_dspy_optimize.py`.

Kept in an unnumbered module (per repo convention) so both numbered entry
points can import it with a plain `import` statement.
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))

from common.config import settings

GOLDEN_EXAMPLES = [
    {"question": "What is 15% of 2400?", "answer": "360"},
    {"question": "What is 1234 * 5678?", "answer": "7006652"},
    {"question": "What is 12 + 8 * 3?", "answer": "36"},
    {"question": "What is (100 - 25) / 5?", "answer": "15"},
    {"question": "What is 9999 - 4567?", "answer": "5432"},
    {"question": "What is 45 * 45?", "answer": "2025"},
]

TRAIN_SPLIT = GOLDEN_EXAMPLES[:4]
HELD_OUT_SPLIT = GOLDEN_EXAMPLES[4:]


def configure_dspy():
    """Point DSPy's LM at the local Ollama OpenAI-compatible endpoint."""
    import dspy

    lm = dspy.LM(
        f"openai/{settings.OLLAMA_MODEL}",
        api_base=settings.OLLAMA_BASE_URL,
        api_key=settings.OLLAMA_API_KEY,
    )
    dspy.configure(lm=lm)
    return dspy


def build_module():
    dspy = configure_dspy()

    class SolveMath(dspy.Signature):
        """Solve the arithmetic word problem. Answer with just the final number."""

        question: str = dspy.InputField()
        answer: str = dspy.OutputField(desc="just the final numeric answer, no words")

    return dspy.Predict(SolveMath)


def score(module, examples: list[dict]) -> float:
    if not examples:
        return 0.0
    correct = 0
    for example in examples:
        prediction = module(question=example["question"])
        if example["answer"].strip() in str(prediction.answer).strip():
            correct += 1
    return correct / len(examples)


def dspy_metric(example, prediction, trace=None) -> bool:
    return example.answer.strip() in str(prediction.answer).strip()


def optimize(module, trainset: list[dict]):
    """Run DSPy's BootstrapFewShot optimizer against a training split."""
    dspy = configure_dspy()
    examples = [
        dspy.Example(question=item["question"], answer=item["answer"]).with_inputs("question")
        for item in trainset
    ]
    optimizer = dspy.BootstrapFewShot(metric=dspy_metric, max_bootstrapped_demos=2)
    return optimizer.compile(module, trainset=examples)
