# Phase 8: Multi-Agent Patterns

Four multi-agent patterns, each implemented once by hand and once per
framework, so the same pattern can be compared across implementations.

| Pattern | Description | Stop condition |
| --- | --- | --- |
| `researcher_writer` | Researcher (tools) -> Writer (no tools) sequential handoff | fixed 2 steps |
| `planner_executor` | Supervisor plans subtasks, delegates to tool-using workers | all tasks done or `max_turns` |
| `debate` | Agent A <-> Agent B argue, Judge decides | fixed `max_rounds` then judge verdict |
| `critique_loop` | Drafter -> deterministic calculator verification -> revise | tool-verified match or `max_rounds` |

## Folders

| Folder | Implementation | Status in `torchenv` |
| --- | --- | --- |
| `example/` | Hand-written, no framework - `common/llm.chat` + Phase 3 tool registry, returns a `Trajectory` | always works |
| `pydantic_ai/` | [PydanticAI](https://ai.pydantic.dev) `Agent` + `tool_plain` / `output_type` | installed, live-tested |
| `autogen/` | `autogen-agentchat` `AssistantAgent` + `FunctionTool` / `output_content_type` | installed, live-tested |
| `langgraph/` | `StateGraph` with prebuilt `create_react_agent` nodes and conditional edges | installed, live-tested |
| `langchain/` | `AgentExecutor` + `create_tool_calling_agent` + `with_structured_output` | installed, live-tested |
| `crewai/` | `Agent` / `Task` / `Crew(process=Process.sequential)` | installed, live-tested |
| `strands/` | `strands.Agent` + `@tool` + `OllamaModel` + `structured_output()` | installed, live-tested |

Every framework folder exposes the same four function names so they're
drop-in comparable:

```text
run_researcher_writer(question: str) -> str
run_planner_executor(question: str, max_turns: int = 5) -> str
run_debate(question: str, max_rounds: int = 3) -> str
run_critique_loop(question: str, max_rounds: int = 3) -> str
```

Run any pattern directly:

```powershell
python 07_multi_agent/example/researcher_writer/handoff.py "..."
python 07_multi_agent/pydantic_ai/researcher_writer.py "..."
python 07_multi_agent/autogen/critique_loop.py "What is 1234 * 5678?"
python 07_multi_agent/langgraph/debate.py
python 07_multi_agent/langchain/planner_executor.py "..."
python 07_multi_agent/crewai/critique_loop.py "What is 1234 * 5678?"
python 07_multi_agent/strands/critique_loop.py "What is 1234 * 5678?"
```

## Shared conventions

- `spec.py` at this level defines `DraftAnswer` (expression/answer) and `Plan`
  (list of subtask strings), reused by every framework's `critique_loop` and
  `planner_executor` so the structured-output contract is identical everywhere.
- Every `critique_loop` verifies against the real `03_tools/tools/calculator.py`
  function directly - never another LLM call - so "correct" is deterministic.
- Every `researcher_writer` gives the writer agent zero tool access, so any
  concrete fact (a number, a name) in its output had to come from the
  researcher's tool calls.
- `common/config.py`'s `settings.OLLAMA_BASE_URL` (`.../v1`) is for OpenAI-style
  clients (PydanticAI, AutoGen, `common/llm.py`). `settings.OLLAMA_HOST` (no
  `/v1`) is for native-Ollama clients (`ChatOllama` in LangGraph/LangChain,
  CrewAI's `LLM(model="ollama/...")`, Strands' `OllamaModel`). Mixing these up
  causes a silent `404 page not found`.

## Installing the frameworks

`torchenv` ships `pydantic-ai` and `autogen-agentchat` from Phase 7. This
phase additionally installed `langgraph`, `langchain` + `langchain-ollama`,
`strands-agents` + `strands-agents-tools`, and `crewai` + `crewai-tools`
directly into `torchenv` (all verified not to break `torch` or each other).
`crewai`'s install downgraded some shared packages (`openai`, `pyyaml`,
`requests`, `opentelemetry-*`) to satisfy its pins - if that causes trouble
for other projects sharing this env, run `pip freeze` before installing new
frameworks and keep a snapshot so you can roll back with
`pip install -r <snapshot>.txt`, or run CrewAI in Docker per its
`06_frameworks/crewai/Dockerfile` fallback.

## Test

```powershell
pytest tests/test_multi_agent.py -v          # example/ (hand-written) patterns
```
