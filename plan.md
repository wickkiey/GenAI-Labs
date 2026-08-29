# GenAI Labs — Implementation Plan (Phase by Phase)

**Ground rules for the whole repo**

| Item | Decision |
| --- | --- |
| Python env | Existing conda env **`torchenv`** (activate with `conda activate torchenv` before every step) |
| Model runtime | **Ollama** on the host, `http://localhost:11434` |
| Default model | `qwen3:8b` (tool-capable). Fallback if slow: `qwen2.5:7b-instruct` |
| Embedding model | `nomic-embed-text` |
| Docker | Used **only** where a service is needed: Chroma/Qdrant, Postgres, Langfuse. Never for the lab Python code. |
| Config | One `.env` at repo root, read by one shared module `common/config.py` |
| Test style | Every module has `test_*.py` runnable with `pytest`, **plus** a manual "run and eyeball" command |

**Golden rule:** do not start a phase until the previous phase's *Exit check* passes.

---

## Phase 0 — Environment & Repo Skeleton

### 0.1 Build

1. Verify env and Ollama:
   ```powershell
   conda activate torchenv
   python --version
   ollama --version
   ollama list
   ```
2. Pull models:
   ```powershell
   ollama pull qwen3:8b
   ollama pull nomic-embed-text
   ```
3. Install base deps into `torchenv`:
   ```powershell
   pip install python-dotenv pydantic httpx rich pytest ollama openai
   ```
4. Create the skeleton (only folders you need now; add later phases as you reach them):
   ```text
   GenAI-Labs/
   ├── .env
   ├── .env.example
   ├── .gitignore
   ├── requirements/            # one txt per phase group
   ├── common/
   │   ├── __init__.py
   │   ├── config.py            # loads .env, exposes MODEL, BASE_URL
   │   ├── llm.py               # get_openai_client(), get_ollama_client()
   │   └── trace.py             # (filled in Phase 9)
   ├── 00_setup/
   └── tests/
   ```
5. `.env`:
   ```text
   OLLAMA_HOST=http://localhost:11434
   OLLAMA_BASE_URL=http://localhost:11434/v1
   OLLAMA_API_KEY=ollama
   OLLAMA_MODEL=qwen3:8b
   EMBED_MODEL=nomic-embed-text
   TEMPERATURE=0
   ```
6. `common/config.py` — load dotenv, expose `settings` (a Pydantic `BaseSettings` or simple dataclass).
7. `common/llm.py` — two factories:
   - `get_openai_client()` → `openai.OpenAI(base_url=OLLAMA_BASE_URL, api_key="ollama")`
   - `chat(messages, **kw)` thin helper used by Phase 1.
8. `00_setup/ollama_check.py` — prints Ollama version, model list, and a one-line completion.

### 0.2 Test

```powershell
python 00_setup/ollama_check.py
pytest tests/test_phase0.py -v
```

`tests/test_phase0.py` asserts:
- `/api/tags` returns 200 and contains `qwen3`
- a 5-token completion returns non-empty text
- `settings.OLLAMA_MODEL` is not empty

### 0.3 Exit check
- [ ] `ollama_check.py` prints a model answer
- [ ] `pytest` green
- [ ] `.env` is gitignored, `.env.example` is committed

---

## Phase 1 — LLM Fundamentals (no agents)

**Folder:** `01_llm_basics/`

### 1.1 Build (one file at a time, in order)

| File | What to build | New concept |
| --- | --- | --- |
| `01_simple_completion.py` | single user message → response | messages array |
| `02_system_prompt.py` | same question with 3 different system prompts | role steering |
| `03_conversation.py` | multi-turn loop keeping `messages` list | context/history |
| `04_streaming.py` | `stream=True`, print token by token | streaming |
| `05_structured_output.py` | `Person(name, age, occupation)` via JSON schema / `response_format` | structured output |
| `06_parameters.py` | temperature 0 vs 1, max_tokens, seed | determinism |

Keep every file < 60 lines. Each file must be runnable standalone: `python 01_llm_basics/03_conversation.py`.

### 1.2 Test

```powershell
python 01_llm_basics/01_simple_completion.py
# ... run each in order
pytest tests/test_phase1.py -v
```

`tests/test_phase1.py`:
- structured output parses into the Pydantic model without exception
- temperature=0 twice → identical output (or note in README if the model is non-deterministic)
- streaming yields > 1 chunk

### 1.3 Exit check
- [ ] You can explain `system / user / assistant / tool` roles from memory
- [ ] Structured output works reliably 3 runs in a row
- [ ] `01_llm_basics/README.md` written in your own words

---

## Phase 2 — First Agent (hand-written, no framework)

**Folder:** `02_agents/`

### 2.1 Build

1. `01_basic_agent.py` — a class:
   ```text
   Agent(system_prompt, model)
     .run(user_input) -> str        # single LLM call, keeps history
   ```
2. `02_agent_with_tool.py` — add ONE tool, `calculator(expression: str) -> str`:
   - define the JSON tool schema by hand
   - pass `tools=[...]` to the chat call
   - detect `tool_calls` in the response
   - execute the function, append a `role="tool"` message, call the LLM again
   - return the final answer
3. `03_agent_loop.py` — wrap step 2 in a `while` loop with `max_iterations=5`, so multiple sequential tool calls work.
4. `04_structured_agent.py` — force the final answer into a Pydantic model.

**Do not use any agent framework in this phase.** This is the reference implementation you will compare everything against later.

### 2.2 Test

```powershell
python 02_agents/03_agent_loop.py "What is 1234 * 5678, then subtract 1000?"
pytest tests/test_phase2.py -v
```

`tests/test_phase2.py`:
- `calculator("2+2")` returns `4` (unit test, no LLM)
- agent answers `1234*5678` correctly → `7006652`
- agent does **not** call the tool for "Hello, who are you?"
- loop terminates and never exceeds `max_iterations`

### 2.3 Exit check
- [ ] You can draw the tool-calling round-trip on paper
- [ ] Agent handles both tool and no-tool questions correctly

---

## Phase 3 — Tools

**Folder:** `03_tools/`

### 3.1 Build

Add tools one per file, registering into a shared `tool_registry`:

1. `tools/calculator.py` — safe eval (use `ast.literal_eval` + operator whitelist, **never** raw `eval`)
2. `tools/datetime_tool.py` — `get_current_time(timezone)`
3. `tools/filesystem.py` — `list_files`, `read_file` **sandboxed to `data/sandbox/`** (resolve path, reject anything outside)
4. `tools/sqlite_tool.py` — `list_tables`, `describe_table`, `query_database` (read-only, reject non-SELECT)
5. `tools/search.py` — keyword search over local text files in `data/docs/`
6. `04_multiple_tools.py` — give the agent all 5 and test selection
7. `05_error_handling.py` — tool raises → return error string to the model → model retries

Seed data: create `data/sandbox/*.txt` and a `data/labs.db` SQLite with 2–3 small tables (`employees`, `departments`, `sales`).

### 3.2 Test

```powershell
pytest tests/test_tools.py -v          # pure unit tests, no LLM
python 03_tools/04_multiple_tools.py   # manual selection check
pytest tests/test_phase3.py -v         # LLM selection tests
```

Selection test matrix (assert the *right tool name* was called):

| Prompt | Expected tool |
| --- | --- |
| "What is 15% of 2400?" | calculator |
| "What time is it in IST?" | datetime |
| "What's in notes.txt?" | filesystem |
| "How many employees are in Sales?" | sqlite |
| "Find documents mentioning 'vector'" | search |

Security tests (must fail safely):
- `read_file("../../.env")` → rejected
- `query_database("DROP TABLE employees")` → rejected

### 3.3 Exit check
- [ ] 5/5 tool-selection cases pass
- [ ] Both security tests pass
- [ ] Tool errors are recovered from, not crashed on

---

## Phase 4 — MCP Servers (build your own)

**Folder:** `04_mcp/servers/`

```powershell
pip install "mcp[cli]"
```

### 4.1 Build (one server at a time)

| Order | Server | Tools exposed | Transport |
| --- | --- | --- | --- |
| 1 | `calculator/server.py` | add, subtract, multiply, divide | stdio |
| 2 | `filesystem/server.py` | list_files, read_file, search_files (sandboxed) | stdio |
| 3 | `sqlite/server.py` | list_tables, describe_table, query_database | stdio |
| 4 | `knowledge/server.py` | search_knowledge, get_document | stdio (HTTP variant later) |

Reuse the Phase 3 tool functions — the MCP server should be a thin wrapper (`@mcp.tool()`), not a rewrite. That proves the separation between *tool logic* and *tool protocol*.

Then: `5. calculator_http/` — same calculator over **Streamable HTTP**, containerised:
- `Dockerfile` (python:3.12-slim, `pip install mcp`, `CMD python server.py`)
- `docker-compose.yml` exposing port 8000

### 4.2 Test

```powershell
# Inspector (no agent involved) - the fastest feedback loop
mcp dev 04_mcp/servers/calculator/server.py
```
In the Inspector UI: list tools → call `multiply(1234, 5678)` → expect `7006652`.

```powershell
pytest tests/test_mcp_servers.py -v
```
Test uses `mcp.client.stdio` directly (no LLM):
- `list_tools()` returns expected names + schemas
- each tool returns the correct result
- `divide(1, 0)` returns an MCP error, doesn't kill the server
- filesystem server rejects path traversal

Docker check:
```powershell
docker compose -f 04_mcp/servers/calculator_http/docker-compose.yml up -d
curl http://localhost:8000/mcp    # or use `mcp dev` against the URL
docker compose ... down
```

### 4.3 Exit check
- [ ] All 4 stdio servers pass Inspector + pytest
- [ ] HTTP server reachable from a container
- [ ] You can explain tools vs resources vs prompts in MCP

---

## Phase 5 — MCP Clients

**Folder:** `04_mcp/clients/`

### 5.1 Build

1. `raw/client.py` — pure MCP Python SDK client: connect → list tools → convert MCP schemas into OpenAI tool schemas → feed your **Phase 2 hand-written agent**. This is the key learning step.
2. `multi_server.py` — connect to calculator + sqlite + filesystem at once, namespace tool names (`calc__add`, `db__query`).
3. `http_client.py` — same, but against the Dockerised HTTP server.

(Framework-specific MCP clients come in Phase 7 — don't do them yet.)

### 5.2 Test

```powershell
python 04_mcp/clients/multi_server.py "How many rows in employees, times 12?"
pytest tests/test_phase5.py -v
```
Assertions:
- tool list from 3 servers merges without name collisions
- the multi-step question triggers ≥ 2 tool calls across ≥ 2 servers
- server disconnect is handled with a clear error, not a hang

### 5.3 Exit check
- [ ] Your own agent, zero frameworks, driving 3 MCP servers

---

## Phase 6 — Agent Loops (hand-written)

**Folder:** `05_loops/`

### 6.1 Build

| File | Loop | Stop condition |
| --- | --- | --- |
| `01_react.py` | Thought → Action → Observation | `FINAL:` marker or max steps |
| `02_plan_execute.py` | Planner produces `list[Task]`, Executor runs each | all tasks done |
| `03_reflection.py` | Answer → Critic → Improve | critic says OK, or max 3 rounds |
| `04_retry.py` | tool/parse failure → retry with error fed back | success or 3 attempts |
| `05_verification.py` | Solution → Verifier → PASS/FAIL → retry | PASS or max rounds |
| `06_critique_loop.py` | Agent A ↔ Agent B until agreement | agree or max 4 rounds |

Every loop must return a **trajectory object**: `{steps: [...], tool_calls: [...], iterations: n, final: str}`. You will reuse this in Phase 10.

### 6.2 Test

```powershell
python 05_loops/01_react.py "Which department has the highest total sales, and what is 10% of it?"
pytest tests/test_phase6.py -v
```
Assertions:
- no loop exceeds its max-iteration cap (inject a deliberately unsolvable task)
- plan-execute produces ≥ 2 tasks for a compound question
- reflection loop's round-2 answer differs from round-1
- retry loop recovers from a tool that fails the first 2 calls (use a mock tool)
- trajectory dict is JSON-serialisable

### 6.3 Exit check
- [ ] 6 loops implemented, all bounded, all emit trajectories
- [ ] `docs/concepts/loops.md` written comparing them

---

## Phase 7 — Frameworks (same task, six times)

**The invariant task** (write it once in `06_frameworks/spec.py`):

> "Answer the question using calculator + sqlite tools, verify the result, and return `Answer(value, reasoning, tools_used, confidence)`."

Same model, same temperature, same 10 test questions for all frameworks.

### 7.1 Build order

**7A — PydanticAI** (`pip install pydantic-ai`)
```text
01_basic_agent.py  02_tools.py  03_structured_output.py
04_dependencies.py 05_mcp.py    06_the_spec_task.py
```

**7B — LangChain** (`pip install langchain langchain-ollama langchain-mcp-adapters`)
```text
01_chat.py 02_tools.py 03_agent.py 04_structured_output.py 05_mcp.py 06_the_spec_task.py
```

**7C — LangGraph** (`pip install langgraph`) — *deepest module, take your time*
```text
01_basic_graph.py      02_agent_node.py     03_tool_node.py
04_conditional_edges.py 05_react_agent.py   06_checkpoint_memory.py
07_human_in_loop.py    08_multi_agent.py    09_mcp.py
10_the_spec_task.py
```

**7D — Strands** (`pip install strands-agents strands-agents-tools`)
```text
01_basic_agent.py 02_tools.py 03_streaming.py 04_mcp.py 05_the_spec_task.py
```

**7E — CrewAI** (`pip install crewai crewai-tools`) — ⚠️ pins deps aggressively; if it fights `torchenv`, run it in a **Docker container** (`06_frameworks/crewai/Dockerfile`) talking to host Ollama via `host.docker.internal`.
```text
01_agent.py 02_task.py 03_crew_sequential.py 04_tools.py 05_memory.py 06_the_spec_task.py
```

**7F — AutoGen** (`pip install autogen-agentchat autogen-ext[openai]`) — add the maintenance-mode warning in its README. Same Docker fallback if deps conflict.
```text
01_single_agent.py 02_two_agents.py 03_group_chat.py 04_tools.py 05_the_spec_task.py
```

### 7.2 Test — one shared harness

Build `tests/framework_suite.py` that takes a callable `run(question) -> Answer` and runs the same 10 questions:

```powershell
pytest tests/test_frameworks.py -v -k pydantic_ai
pytest tests/test_frameworks.py -v          # all frameworks
```

Record per framework: accuracy, avg latency, avg tool calls, failures → write to `10_evaluation/results/frameworks.csv`.

Dependency-safety rule: **before installing each framework**, snapshot the env:
```powershell
pip freeze > requirements/snapshot_before_<framework>.txt
```
If an install breaks torch, roll back with that file.

### 7.3 Exit check
- [ ] Same task passing in ≥ 4 frameworks
- [ ] `docs/comparisons/frameworks.md` matrix filled in with **your** notes
- [ ] `torchenv` still imports torch correctly

---

## Phase 8 — Multi-Agent

**Folder:** `07_multi_agent/`

### 8.1 Build
1. `researcher_writer/` — sequential handoff (CrewAI + LangGraph versions)
2. `planner_executor/` — supervisor delegates to workers (LangGraph)
3. `debate/` — two agents argue N rounds, judge decides
4. `critique_loop/` — productionised version of Phase 6's `06_critique_loop.py`

### 8.2 Test
```powershell
pytest tests/test_multi_agent.py -v
```
- handoff: writer's output contains facts only the researcher could have retrieved
- supervisor never loops more than `max_turns`
- debate terminates and the judge returns one of the two positions
- critique loop measurably improves a deliberately-wrong first answer (assert final is correct)

### 8.3 Exit check
- [ ] All 4 patterns terminate reliably 5/5 runs

---

## Phase 9 — Memory & RAG

**Folders:** `08_memory/`, `09_rag/`

### 9.1 Docker services
```yaml
# infra/docker-compose.yml
services:
  chroma:    # port 8001
  postgres:  # port 5432, for long-term memory
```
```powershell
docker compose -f infra/docker-compose.yml up -d chroma postgres
```

### 9.2 Build
**Memory**
1. `short_term/` — message history + windowing + summarisation
2. `state/` — LangGraph checkpointer (SQLite → Postgres)
3. `long_term/` — user facts stored in Postgres, injected into prompt
4. `semantic/` — embeddings (`nomic-embed-text`) → Chroma → similarity recall
5. `episodic/` — store past task trajectories, retrieve similar past runs

**RAG**
1. `01_basic_rag.py` — chunk → embed → store → retrieve → answer
2. `02_rag_as_tool.py` — retriever exposed as an agent tool
3. `03_agentic_rag.py` — agent decides *whether* and *how often* to search, grades retrieved chunks
4. `04_mcp_rag.py` — the Phase 4 knowledge MCP server backed by Chroma
5. `05_multi_agent_rag.py` — retriever agent + answerer + critic

Corpus: put 10–20 markdown/PDF docs in `data/corpus/`.

### 9.3 Test
```powershell
pytest tests/test_memory.py -v
pytest tests/test_rag.py -v
```
- semantic memory: query returns the planted fact in top-3
- long-term memory survives a process restart (write, exit, re-run, read)
- basic RAG: 8/10 golden Q&A pairs answered from context
- agentic RAG: skips retrieval for "What is 2+2?" (assert 0 retriever calls)
- RAG answers cite a source doc id

### 9.4 Exit check
- [ ] Agentic RAG beats basic RAG on your golden set
- [ ] Containers start/stop cleanly, data persists in a volume

---

## Phase 10 — Evaluation & Tracing

**Folder:** `10_evaluation/`

### 10.1 Docker (optional but recommended)
```powershell
docker compose -f infra/docker-compose.yml up -d langfuse
```

### 10.2 Build
1. `common/trace.py` — decorator `@traced` that captures the trajectory JSON per run into `10_evaluation/traces/*.jsonl`:
   ```json
   {"task":"...","framework":"langgraph","model":"qwen3:8b","tool_calls":[],
    "steps":[],"final_answer":"...","latency_ms":0,"tokens":0,"success":true}
   ```
2. `datasets/` — 30 tasks: 10 calculator, 10 sqlite, 10 multi-hop, each with expected answer
3. `evaluators/` — exact match, numeric tolerance, LLM-as-judge, tool-selection accuracy
4. `runner.py` — run dataset × framework matrix → `results/*.csv`
5. `report.py` — render a markdown comparison table

### 10.3 Test
```powershell
python 10_evaluation/runner.py --framework all --dataset all
pytest tests/test_evaluation.py -v
```
- evaluator unit tests with hand-written fixtures (no LLM)
- trace files are valid JSONL and one line per run
- runner is resumable (kill it mid-run, restart, no duplicate rows)

### 10.4 Exit check
- [ ] One command produces a framework comparison table
- [ ] Traces visible in Langfuse (if enabled)

---

## Phase 11 — Capstone Projects

**Folder:** `11_projects/`

| Project | Build | Test |
| --- | --- | --- |
| `local_research_agent/` | LangGraph agent + search/filesystem/sqlite MCP + critic node | 5 research questions → answer with citations, all offline |
| `sql_agent/` | NL → SQL → execute → verify → explain | 20 golden NL/SQL pairs, ≥ 80% correct, 0 write statements executed |
| `mcp_assistant/` | One agent, all your MCP servers, CLI chat | 10-turn session without crash, correct server routing |
| `agent_arena/` | Same task → Agent A vs Agent B → evaluator compares trajectories | reproducible verdict, results written to CSV |
| `critique_loop/` | Flagship: A solves, B critiques, A revises, until agreement | converges within 4 rounds on 8/10 tasks; full trajectory persisted |

Ship each with a `README.md` (architecture diagram + how to run) and a `docker-compose.yml` if it needs services.

---

## Recurring checklist per module

Every single module you build:

1. `conda activate torchenv`
2. Write the smallest working script
3. Run it manually, read the output
4. Write `test_*.py` (at least one no-LLM unit test + one LLM behaviour test)
5. `pytest tests/test_<module>.py -v`
6. Write 5 lines in the folder `README.md`: *what I built, what surprised me, what broke*
7. `git commit -m "phase<N>: <module>"`

## Env-safety rules
- Snapshot before risky installs: `pip freeze > requirements/snapshot_<date>.txt`
- Verify torch after each framework install: `python -c "import torch; print(torch.__version__)"`
- If a framework demands conflicting pins → move that framework into Docker, keep `torchenv` clean
- Containers reach the host model at `http://host.docker.internal:11434`

## Suggested pacing
| Week | Phases |
| --- | --- |
| 1 | 0, 1 |
| 2 | 2, 3 |
| 3 | 4, 5 |
| 4 | 6 |
| 5 | 7A–7D |
| 6 | 7E–7F, 8 |
| 7 | 9 |
| 8 | 10, 11 |
