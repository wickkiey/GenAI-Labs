# Agent Arena

This project compares two agent strategies on the same task and evaluates their trajectories.

What I built: a comparison harness for recording answers, tool use, and final verdicts.
What surprised me: the same model can produce very different results when the control logic changes.
What broke: without a deterministic evaluator, arena results become noisy and hard to compare.
