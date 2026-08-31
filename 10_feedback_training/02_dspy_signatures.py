"""Phase 11: 02 -- express the calculator task as a DSPy Signature/Module; baseline run."""
from __future__ import annotations

try:
    from .dspy_task import GOLDEN_EXAMPLES, build_module, score
except ImportError:
    from dspy_task import GOLDEN_EXAMPLES, build_module, score


def main() -> None:
    try:
        module = build_module()
        baseline_score = score(module, GOLDEN_EXAMPLES)
    except ImportError as error:
        print(f"dspy not installed, skipping: {error}")
        return
    print(f"zero-shot baseline accuracy: {baseline_score:.0%}")


if __name__ == "__main__":
    main()
