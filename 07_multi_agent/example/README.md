# Phase 8: Multi-Agent Patterns

Four hand-written multi-agent patterns built on the Phase 2 chat helper
(`common/llm.chat`) and the Phase 3 tool registry (`03_tools/tool_agent.py`,
`03_tools/tools/`). Each pattern returns a `Trajectory` (`steps`, `tool_calls`,
`iterations`, `final`) from `trajectory.py`, same contract as Phase 6.

No new framework installs are required - `torchenv` currently ships
`pydantic-ai` and `autogen-agentchat` (from Phase 7) but not `langgraph`,
`langchain`, or `crewai`, so these patterns are implemented directly against
the local Ollama model to stay dependency-safe. Swapping in a framework later
is a drop-in exercise since the `Trajectory` contract stays the same.

| Folder | Pattern | Stop condition |
| --- | --- | --- |
| `researcher_writer/handoff.py` | Researcher (tools) -> Writer (no tools) sequential handoff | fixed 2 steps |
| `planner_executor/supervisor.py` | Supervisor plans subtasks, delegates to tool-using workers | all tasks done or `max_turns` |
| `debate/debate.py` | Agent A <-> Agent B argue, Judge decides | fixed `max_rounds` then judge verdict |
| `critique_loop/critique_loop.py` | Drafter -> deterministic calculator verification -> revise | tool-verified match or `max_rounds` |

Run:

```powershell
python 07_multi_agent/researcher_writer/handoff.py "Which department has the highest total sales, and by how much?"
python 07_multi_agent/planner_executor/supervisor.py "How many rows are in employees, times 12?"
python 07_multi_agent/debate/debate.py
python 07_multi_agent/critique_loop/critique_loop.py "What is 1234 * 5678?"
pytest tests/test_multi_agent.py -v
```

## Notes

- `researcher_writer`: the writer has no tool access, so any concrete fact in
  its output (a number, a name) had to come from the researcher's tool calls.
- `planner_executor`: the supervisor's plan is truncated to `max_turns`
  subtasks before execution, so it can never run more worker turns than the cap
  even if it plans more.
- `debate`: always runs the full `max_rounds`, then a separate Judge call
  picks a winner - it does not self-terminate on agreement like Phase 6's
  critique loop.
- `critique_loop`: verification is a real `calculator()` call, not another LLM
  call, so "correct" is deterministic and the loop reliably fixes a wrong
  first draft.
