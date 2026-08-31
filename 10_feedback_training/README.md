# Phase 11: Feedback Loops & Agent Training

Closes the loop: turn Phase 10's traces/evaluation scores into something that
improves the agent, both by hand and with **DSPy**.

| File | What it does |
| --- | --- |
| `01_human_feedback_capture.py` | thumbs up/down + free-text correction, linked to a Phase 10 trace id |
| `dspy_task.py` | shared DSPy scaffolding (Signature, module builder, scorer, optimizer) |
| `02_dspy_signatures.py` | zero-shot baseline DSPy run |
| `03_dspy_optimize.py` | `BootstrapFewShot` optimizer vs. baseline, on a held-out split |
| `04_prompt_feedback_loop.py` | hand-written prompt-patch loop with a **regression guard** (no framework) |
| `05_preference_dataset.py` | builds a `(chosen, rejected)` pairwise dataset from critique-loop outputs |
| `06_closed_loop_eval.py` | wires it together: eval -> capture failures -> patch -> re-eval -> assert improved |

`02_dspy_signatures.py` / `03_dspy_optimize.py` print `"dspy not installed,
skipping"` if `dspy-ai` isn't installed -- see `requirements/phase11.txt`.

Run:

```powershell
python 10_feedback_training/01_human_feedback_capture.py trace-123 up "good answer"
python 10_feedback_training/02_dspy_signatures.py
python 10_feedback_training/03_dspy_optimize.py
python 10_feedback_training/04_prompt_feedback_loop.py
python 10_feedback_training/05_preference_dataset.py
python 10_feedback_training/06_closed_loop_eval.py
pytest tests/test_feedback_training.py -v
```

**What surprised me:** the regression guard is the whole point -- a naive
"always add a few-shot example for every failure" patch can still make
things worse (more tokens, more distraction), so `apply_if_improved` compares
scores and falls back to the previous prompt rather than trusting the patch
blindly.
**What broke:** DSPy needs an explicit `dspy.LM("openai/<model>", api_base=...)`
pointed at Ollama's OpenAI-compatible endpoint -- it does not discover
`OLLAMA_BASE_URL` from the environment automatically.
