"""Phase 11: 03 -- optimize the DSPy module with BootstrapFewShot and compare to baseline."""
from __future__ import annotations

try:
    from .dspy_task import HELD_OUT_SPLIT, TRAIN_SPLIT, build_module, optimize, score
except ImportError:
    from dspy_task import HELD_OUT_SPLIT, TRAIN_SPLIT, build_module, optimize, score


def main() -> None:
    try:
        baseline_module = build_module()
        baseline_score = score(baseline_module, HELD_OUT_SPLIT)

        optimized_module = optimize(build_module(), TRAIN_SPLIT)
        optimized_score = score(optimized_module, HELD_OUT_SPLIT)
    except ImportError as error:
        print(f"dspy not installed, skipping: {error}")
        return

    print(f"baseline held-out accuracy:  {baseline_score:.0%}")
    print(f"optimized held-out accuracy: {optimized_score:.0%}")
    if optimized_score >= baseline_score:
        print("DSPy optimization matched or improved the baseline.")
    else:
        print("WARNING: optimization did not improve on the baseline this run.")


if __name__ == "__main__":
    main()
