# Phase 9: Sub-Agents

Orchestrator/sub-agent delegation: a parent agent spawns **isolated** child
agents to handle bounded subtasks and gets back a `SubagentResult`, never a
running conversation. This is different from Phase 8's peer-to-peer
multi-agent patterns (handoff, debate, critique loop), where agents share or
pass along a conversation.

Core primitive lives in `subagent_core.py` (`Subagent`, `spawn_subagent`); the
numbered files are runnable demonstrations.

| File | Pattern |
| --- | --- |
| `01_basic_subagent.py` | one parent spawns one isolated subagent |
| `02_parallel_subagents.py` | N subagents run concurrently, results merged in order |
| `03_specialized_subagents.py` | role-specific subagents (researcher/coder/reviewer), routed by task type |
| `04_subagent_with_mcp.py` | each subagent owns its own MCP server connection |
| `05_recursive_subagents.py` | a subagent may delegate to another subagent, bounded by `max_depth` |
| `06_framework_subagents.py` | the same pattern shown as a LangGraph subgraph-as-node |

Run:

```powershell
python 08_subagents/01_basic_subagent.py "Summarize why the sky is blue"
python 08_subagents/02_parallel_subagents.py
python 08_subagents/03_specialized_subagents.py "How many employees are in Sales?"
python 08_subagents/04_subagent_with_mcp.py
python 08_subagents/05_recursive_subagents.py
python 08_subagents/06_framework_subagents.py
pytest tests/test_subagents.py -v
```

**What surprised me:** isolation is the whole point -- a subagent's
`messages` history is never appended to the parent's, so the parent's context
window stays small no matter how much work a subagent did internally.
**What broke:** an unbounded recursive-delegation task will happily loop
forever unless `max_depth` is enforced explicitly at spawn time -- there's no
implicit stop condition like `FINAL:` in Phase 6's loops.
