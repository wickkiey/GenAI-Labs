# Phase 6: Agent Loops

Six hand-written, bounded agent loops. Each loop's core logic lives in its own
module (`react.py`, `plan_execute.py`, ...) and returns a `Trajectory`
(`steps`, `tool_calls`, `iterations`, `final`) from `trajectory.py`; the numbered
files are thin CLI entry points.

| File | Loop | Stop condition |
| --- | --- | --- |
| `react.py` | Thought -> Action -> Observation | `FINAL:` marker or `max_steps` |
| `plan_execute.py` | Planner produces `list[Task]`, Executor runs each | all tasks done |
| `reflection.py` | Answer -> Critic -> Improve | critic says `OK`, or `max_rounds` |
| `retry.py` | action fails -> retry with error fed back | success or `max_attempts` |
| `verification.py` | Solution -> Verifier -> PASS/FAIL -> retry | `PASS` or `max_rounds` |
| `critique_loop.py` | Agent A <-> Agent B until agreement | `AGREE` or `max_rounds` |

Run:

```powershell
python 05_loops/01_react.py "Which department has the highest total sales, and what is 10% of it?"
python 05_loops/02_plan_execute.py
python 05_loops/03_reflection.py
python 05_loops/04_retry.py
python 05_loops/05_verification.py
python 05_loops/06_critique_loop.py
pytest tests/test_phase6.py -v
```
