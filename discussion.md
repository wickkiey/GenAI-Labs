Absolutely. For **GenAI Labs**, I would structure this as a progressive curriculum rather than putting every framework into one giant project. The goal should be:

> **Learn the same agent concept using different frameworks, with the same local Ollama model, and compare how each framework approaches the problem.**

One important 2026 update: **AutoGen is now in maintenance mode**, with Microsoft recommending new users look at Microsoft Agent Framework. I would still include AutoGen in your lab because understanding it is useful, but treat it as a framework-comparison module rather than your primary new framework. ([GitHub][1])

Also, the current ecosystem has good native/local Ollama paths: PydanticAI has an Ollama provider, LangChain has `ChatOllama`, Strands has `OllamaModel`, and Ollama exposes an OpenAI-compatible API. ([pydantic.dev][2])

# 1. Overall learning roadmap

I'd do this in **10 phases**:

```text
Phase 0  → Environment + Ollama
Phase 1  → LLM fundamentals
Phase 2  → First Agent
Phase 3  → Tools + Tool Calling
Phase 4  → MCP
Phase 5  → Agent Loops
Phase 6  → Framework comparison
Phase 7  → Multi-Agent
Phase 8  → Memory + RAG
Phase 9  → Evaluation + Tracing
Phase 10 → Build AgentArena / Critique Loop
```

The important thing is **not to start with CrewAI/LangGraph/etc. immediately**.

First understand what an agent actually does.

---

# 2. Recommended repository structure

I'd create:

```text
genai-labs/
│
├── README.md
├── pyproject.toml
├── uv.lock
├── .gitignore
├── .env.example
│
├── 00_setup/
│   ├── ollama_check.py
│   ├── model_test.py
│   └── README.md
│
├── 01_llm_basics/
│   ├── 01_simple_completion.py
│   ├── 02_system_prompt.py
│   ├── 03_structured_output.py
│   ├── 04_streaming.py
│   └── README.md
│
├── 02_agents/
│   ├── 01_basic_agent/
│   ├── 02_agent_with_system_prompt/
│   ├── 03_agent_with_structured_output/
│   └── README.md
│
├── 03_tools/
│   ├── 01_calculator/
│   ├── 02_weather/
│   ├── 03_file_search/
│   ├── 04_multiple_tools/
│   └── README.md
│
├── 04_mcp/
│   ├── servers/
│   │   ├── calculator/
│   │   ├── filesystem/
│   │   ├── sqlite/
│   │   └── knowledge/
│   │
│   ├── clients/
│   │   ├── pydantic_ai/
│   │   ├── langchain/
│   │   └── strands/
│   │
│   └── README.md
│
├── 05_loops/
│   ├── 01_react_loop/
│   ├── 02_plan_execute/
│   ├── 03_reflection/
│   ├── 04_retry/
│   ├── 05_verification/
│   └── README.md
│
├── 06_frameworks/
│   │
│   ├── pydantic_ai/
│   ├── langchain/
│   ├── langgraph/
│   ├── crewai/
│   ├── strands/
│   └── autogen/
│
├── 07_multi_agent/
│   ├── researcher_writer/
│   ├── planner_executor/
│   ├── debate/
│   └── critique_loop/
│
├── 08_memory/
│   ├── short_term/
│   ├── long_term/
│   ├── semantic/
│   └── episodic/
│
├── 09_rag/
│   ├── basic_rag/
│   ├── agentic_rag/
│   └── mcp_rag/
│
├── 10_evaluation/
│   ├── datasets/
│   ├── evaluators/
│   ├── traces/
│   └── framework_comparison/
│
├── 11_projects/
│   ├── local_research_agent/
│   ├── sql_agent/
│   ├── mcp_assistant/
│   ├── agent_arena/
│   └── critique_loop/
│
└── docs/
    ├── concepts/
    ├── architecture/
    ├── comparisons/
    └── notes/
```

This becomes more than a code repository. It becomes your **personal Agent Engineering textbook + laboratory**.

---

# 3. Phase 0 — Ollama foundation

First make every framework use the same model.

For example:

```bash
ollama pull qwen3:8b
```

or whichever tool-capable model performs well on your machine.

Then:

```bash
ollama list
```

and verify:

```bash
ollama run qwen3:8b
```

Ollama provides an OpenAI-compatible endpoint, including `/v1`, which is particularly useful because many frameworks can talk to it using OpenAI-compatible clients. ([Ollama][3])

Your standard configuration:

```text
OLLAMA_BASE_URL=http://localhost:11434/v1
OLLAMA_MODEL=qwen3:8b
```

Then create:

```text
00_setup/
    ollama_check.py
```

Goal:

```text
Python
  ↓
Ollama
  ↓
Local Model
  ↓
Response
```

Don't move forward until this works.

---

# 4. Phase 1 — Understand LLMs without agents

Learn:

### Experiment 1

```text
User → LLM → Answer
```

### Experiment 2

```text
System Prompt
      ↓
User
      ↓
LLM
      ↓
Answer
```

### Experiment 3

Structured output:

```text
User
 ↓
LLM
 ↓
Pydantic Model
```

Example:

```python
class Person(BaseModel):
    name: str
    age: int
    occupation: str
```

### Experiment 4

Streaming.

### Experiment 5

Conversation history.

You should understand:

```text
messages
system
user
assistant
tool
```

before agents.

---

# 5. Phase 2 — First real Agent

Now build the simplest possible agent:

```text
User
 ↓
Agent
 ↓
LLM
 ↓
Answer
```

Then add a tool:

```text
User
 ↓
Agent
 ↓
LLM ─────→ Tool
 ↑           │
 └───────────┘
       ↓
    Answer
```

Your first tool:

```python
def calculator(expression: str) -> str:
    ...
```

Then ask:

> What is 1234 × 5678?

The model should decide:

```text
I need calculator
       ↓
call calculator
       ↓
receive result
       ↓
final answer
```

This is the point where you start understanding **agentic behavior**.

---

# 6. Phase 3 — Tools

Build these tools in order:

### Tool 1 — Calculator

```text
calculator()
```

### Tool 2 — Date/time

```text
get_current_time()
```

### Tool 3 — File reader

```text
read_file()
```

### Tool 4 — Search

```text
search_documents()
```

### Tool 5 — SQLite

```text
query_database()
```

### Tool 6 — Multiple tools

Give the agent:

```text
calculator
filesystem
sqlite
search
```

Then test whether it selects the correct tool.

This teaches:

* tool schemas
* tool descriptions
* tool selection
* arguments
* tool results
* errors
* retries

---

# 7. Phase 4 — MCP

This should be a **major section** of GenAI Labs.

MCP standardizes how applications expose tools, resources and prompts to AI applications, and the official Python SDK supports MCP servers and clients with transports including stdio and Streamable HTTP. ([GitHub][4])

Build your own MCP servers.

## MCP Server #1 — Calculator

```text
04_mcp/
└── servers/
    └── calculator/
        ├── server.py
        ├── pyproject.toml
        └── README.md
```

Expose:

```text
add()
subtract()
multiply()
divide()
```

---

## MCP Server #2 — SQLite

Expose:

```text
list_tables()
describe_table()
query_database()
```

Architecture:

```text
                    ┌── calculator MCP
                    │
Agent ── MCP ───────┼── SQLite MCP
                    │
                    └── filesystem MCP
```

---

## MCP Server #3 — Filesystem

Expose:

```text
list_files()
read_file()
search_files()
```

Be careful to sandbox the accessible directory.

---

## MCP Server #4 — Knowledge Base

Expose:

```text
search_knowledge()
get_document()
```

Now you've built your own mini MCP ecosystem.

---

# 8. Phase 5 — MCP clients

Now connect agents to your MCP servers.

Start with:

```text
PydanticAI
    ↓
MCP
    ↓
Calculator
```

Then:

```text
LangChain
    ↓
MCP
    ↓
SQLite
```

Then:

```text
Strands
    ↓
MCP
    ↓
Filesystem
```

LangChain also has first-class MCP integration documentation showing MCP tools being consumed by LangChain agents. ([Docs by LangChain][5])

This is where MCP will really click.

---

# 9. Phase 6 — Agent loops

This is probably the **most important phase for you**.

Don't learn loops only through frameworks. Implement them yourself.

## Loop 1 — ReAct

```text
THINK
  ↓
ACT
  ↓
OBSERVE
  ↓
THINK
  ↓
ACT
  ↓
OBSERVE
  ↓
FINAL
```

---

## Loop 2 — Plan → Execute

```text
             ┌──────────────┐
             │    Planner   │
             └──────┬───────┘
                    ↓
              Task List
                    ↓
             ┌──────────────┐
             │   Executor   │
             └──────┬───────┘
                    ↓
                 Result
```

---

## Loop 3 — Reflection

```text
Agent
 ↓
Answer
 ↓
Critic
 ↓
Improve
 ↓
Answer
```

---

## Loop 4 — Verification

```text
Agent
 ↓
Solution
 ↓
Verifier
 ↓
PASS? ── Yes → Final
  │
  No
  ↓
Retry
```

---

## Loop 5 — Critique loop

This directly leads into your **Agent Critique Loop** project:

```text
Agent A
   ↓
Solution
   ↓
Agent B
   ↓
Critique
   ↓
Agent A
   ↓
Revision
   ↓
Agent B
   ↓
Agree?
  ↙   ↘
No    Yes
↓      ↓
Loop  Final
```

This should eventually become one of the flagship projects in `genai-labs`.

---

# 10. Phase 7 — Framework comparison

Now implement **the same agent five/six times**.

This is extremely valuable.

Use exactly the same:

```text
Model
Prompt
Task
Tools
MCP server
Temperature
Test cases
```

Only change the framework.

---

## 7.1 PydanticAI

Learn:

```text
Agent
Model
Tool
Dependency
Run
Structured Output
MCP
```

PydanticAI currently has explicit Ollama support through `OllamaModel` / `OllamaProvider`. ([pydantic.dev][2])

Folder:

```text
06_frameworks/pydantic_ai/
├── 01_basic_agent.py
├── 02_tools.py
├── 03_structured_output.py
├── 04_dependencies.py
├── 05_mcp.py
└── 06_agent_loop.py
```

Start here.

**Why first?**

Because PydanticAI makes the core agent concepts relatively explicit without immediately introducing a huge orchestration abstraction.

---

# 11. LangChain

Learn:

```text
ChatModel
Prompt
Tool
Agent
AgentExecutor / agent runtime
Structured Output
MCP
Callbacks
```

For Ollama, use the current `langchain-ollama` integration and `ChatOllama`. ([Docs by LangChain][6])

Folder:

```text
06_frameworks/langchain/
├── 01_chat.py
├── 02_tools.py
├── 03_agent.py
├── 04_structured_output.py
├── 05_mcp.py
└── 06_rag.py
```

Don't spend too long here.

Your objective is to understand **LangChain's abstractions**, not memorize APIs.

---

# 12. LangGraph

This should be one of your **deepest modules**.

Because this is where you'll really understand agent orchestration.

Learn:

```text
State
Node
Edge
Conditional Edge
Graph
Checkpoint
Interrupt
Human-in-the-loop
Subgraph
```

Architecture:

```text
             START
               ↓
          ┌──────────┐
          │  Agent   │
          └────┬─────┘
               ↓
           Tool Call?
           /       \
         Yes        No
          ↓          ↓
       Tool       END
          │
          └────→ Agent
```

Folder:

```text
06_frameworks/langgraph/
├── 01_basic_graph.py
├── 02_agent_node.py
├── 03_tool_node.py
├── 04_conditional_edges.py
├── 05_react_agent.py
├── 06_memory.py
├── 07_human_loop.py
├── 08_multi_agent.py
└── 09_mcp.py
```

LangGraph is specifically positioned as an orchestration/runtime layer for more complex agentic workflows. ([LangChain][7])

---

# 13. CrewAI

Then learn:

```text
Agent
Task
Crew
Process
Flow
Tools
Memory
```

Basic architecture:

```text
Researcher
    ↓
Research Task
    ↓
Writer
    ↓
Writing Task
    ↓
Final
```

Folder:

```text
06_frameworks/crewai/
├── 01_agent.py
├── 02_task.py
├── 03_crew.py
├── 04_sequential.py
├── 05_parallel.py
├── 06_tools.py
├── 07_memory.py
└── 08_mcp.py
```

CrewAI supports multiple LLM providers and can be configured around local providers such as Ollama. ([CrewAI Documentation][8])

---

# 14. Strands

Then:

```text
06_frameworks/strands/
├── 01_basic_agent.py
├── 02_tools.py
├── 03_streaming.py
├── 04_mcp.py
├── 05_multi_agent.py
└── 06_workflows.py
```

Strands has native Ollama support through `OllamaModel`, including tool/function calling and streaming. ([Strands Agents SDK][9])

This is worth learning because its approach is quite different from graph-heavy orchestration.

---

# 15. AutoGen

Include it, but put a warning in the README:

```text
⚠️ AutoGen is included for learning/comparison.
Microsoft currently considers AutoGen to be in maintenance mode
and recommends Microsoft Agent Framework for new projects.
```

The official repository currently says exactly that. ([GitHub][1])

Folder:

```text
06_frameworks/autogen/
├── 01_single_agent.py
├── 02_two_agents.py
├── 03_group_chat.py
├── 04_tools.py
└── 05_ollama.py
```

Ollama has historically been usable with AutoGen through its OpenAI-compatible interface. ([Microsoft GitHub][10])

---

# 16. Framework learning matrix

Eventually create this in:

```text
docs/comparisons/frameworks.md
```

| Concept           | PydanticAI | LangChain | LangGraph | CrewAI | Strands | AutoGen |
| ----------------- | ---------- | --------- | --------- | ------ | ------- | ------- |
| Basic Agent       | ✓          | ✓         | ✓         | ✓      | ✓       | ✓       |
| Tools             | ✓          | ✓         | ✓         | ✓      | ✓       | ✓       |
| Structured Output | ✓          | ✓         | ✓         | ✓      | ✓       | ✓       |
| MCP               | ✓          | ✓         | ✓         | ✓      | ✓       | ✓       |
| Agent Loop        | ✓          | ✓         | ⭐         | ✓      | ✓       | ✓       |
| Graph Workflow    | —          | —         | ⭐⭐⭐       | —      | —       | —       |
| Multi-Agent       | ✓          | ✓         | ⭐⭐⭐       | ⭐⭐⭐    | ✓       | ⭐⭐⭐     |
| Memory            | ✓          | ✓         | ⭐⭐⭐       | ✓      | ✓       | ✓       |
| Human-in-loop     | ✓          | ✓         | ⭐⭐⭐       | ✓      | ✓       | ✓       |
| Local Ollama      | ✓          | ✓         | ✓         | ✓      | ✓       | ✓       |
| Learning value    | ⭐⭐⭐⭐⭐      | ⭐⭐⭐⭐      | ⭐⭐⭐⭐⭐     | ⭐⭐⭐⭐   | ⭐⭐⭐⭐    | ⭐⭐⭐     |

Don't treat those stars as objective benchmarks; they're your **personal learning notes**.

---

# 17. Phase 8 — Memory

Now investigate memory independently.

### Level 1

Conversation history:

```text
message history
```

### Level 2

Short-term state:

```text
Agent State
```

### Level 3

Long-term memory:

```text
User
 ↓
Memory Store
 ↓
Retrieve
 ↓
Agent
```

### Level 4

Semantic memory:

```text
Embedding
 ↓
Vector DB
 ↓
Similarity Search
```

### Level 5

Episodic memory:

```text
Past task
Past decision
Past result
Past feedback
```

This is where you can experiment with:

```text
Chroma
FAISS
SQLite
Postgres
```

---

# 18. Phase 9 — Agentic RAG

Don't start with complicated agentic RAG.

Go:

```text
01_basic_rag
02_rag_with_tool
03_agentic_rag
04_mcp_rag
05_multi_agent_rag
```

Basic:

```text
Question
 ↓
Retriever
 ↓
Context
 ↓
LLM
 ↓
Answer
```

Agentic:

```text
Question
 ↓
Agent
 ↓
Should I search?
 ├── No → Answer
 │
 └── Yes
      ↓
   Retriever
      ↓
   Evaluate
      ↓
   More search?
      ↓
   Answer
```

---

# 19. Phase 10 — Evaluation

This is where your learning repo becomes **serious engineering**.

Create:

```text
10_evaluation/
├── datasets/
├── evaluators/
├── traces/
├── metrics/
└── framework_comparison/
```

Measure:

```text
Task Success
Tool Selection Accuracy
Tool Argument Accuracy
Final Answer Quality
Latency
Token Usage
Number of Tool Calls
Number of Iterations
Failure Rate
```

For every agent execution capture:

```json
{
  "task": "...",
  "framework": "langgraph",
  "model": "qwen3:8b",
  "tools": [],
  "steps": [],
  "tool_calls": [],
  "final_answer": "...",
  "latency_ms": 1234,
  "success": true
}
```

This will become extremely useful for **AgentArena** later.

---

# 20. The MCP experiments I'd specifically recommend

Build these in order:

### MCP-01 — Calculator

```text
Agent → MCP → calculator
```

### MCP-02 — Filesystem

```text
Agent → MCP → files
```

### MCP-03 — SQLite

```text
Agent → MCP → SQL
```

### MCP-04 — Git

```text
Agent → MCP → Git repository
```

### MCP-05 — Knowledge

```text
Agent → MCP → RAG
```

### MCP-06 — Multiple MCP servers

```text
             ┌── Calculator
             │
Agent ─ MCP ─┼── SQLite
             │
             ├── Filesystem
             │
             └── Knowledge
```

### MCP-07 — MCP + Agent Loop

```text
Agent
 ↓
Select MCP tool
 ↓
Execute
 ↓
Observe
 ↓
Reason
 ↓
Another MCP tool?
 ↓
Final
```

### MCP-08 — MCP + Multi-Agent

```text
Research Agent
      ↓
   MCP tools
      ↓
Critic Agent
      ↓
   MCP tools
      ↓
Final Agent
```

---

# 21. Your first major project

After completing the phases, build:

## Local Research Agent

```text
                   ┌──────────────┐
                   │    Ollama    │
                   └──────┬───────┘
                          │
                    Research Agent
                          │
             ┌────────────┼────────────┐
             ↓            ↓            ↓
          Search       Files        SQLite
           MCP           MCP           MCP
             │            │            │
             └────────────┼────────────┘
                          ↓
                       Critic
                          ↓
                     Final Answer
```

Everything runs locally.

---

# 22. Then build AgentArena

Your existing idea fits perfectly here.

```text
                    Task
                     │
           ┌─────────┴─────────┐
           ↓                   ↓
       Agent A              Agent B
           │                   │
        Tools/MCP           Tools/MCP
           │                   │
           ↓                   ↓
       Trajectory A        Trajectory B
           │                   │
           └─────────┬─────────┘
                     ↓
                  Evaluator
                     ↓
             Comparison Result
```

Now you aren't just learning agents.

You're **experimentally comparing them**.

---

# 23. Then Agent Critique Loop

Finally:

```text
                     Task
                      ↓
                  Agent A
                      ↓
                  Solution
                      ↓
                  Agent B
                      ↓
                   Critique
                      ↓
              ┌──── Agree? ────┐
              │                │
             No               Yes
              ↓                ↓
           Revision          Final
              │
              └──────→ Critique
```

And capture the entire trajectory:

```text
Run
 ├── Task
 ├── Agent A
 │    ├── reasoning/action trace
 │    ├── tool calls
 │    └── result
 │
 ├── Agent B
 │    ├── critique
 │    └── evidence
 │
 ├── Revision
 │
 └── Final
```

That connects beautifully with your original goal of making agent behavior useful for **learning**.

---

# 24. Recommended order — don't deviate too much

If I were doing this as your personal learning curriculum, I'd follow exactly this sequence:

```text
WEEK 1
│
├── Ollama
├── LLM APIs
├── Structured output
└── Streaming
        ↓
WEEK 2
│
├── Agents
├── Tools
├── Tool calling
└── ReAct
        ↓
WEEK 3
│
├── MCP fundamentals
├── Build MCP server
├── Build MCP client
└── MCP + tools
        ↓
WEEK 4
│
├── PydanticAI
├── LangChain
└── Strands
        ↓
WEEK 5
│
├── LangGraph
├── State
├── Nodes
├── Edges
└── Loops
        ↓
WEEK 6
│
├── CrewAI
├── AutoGen
└── Multi-agent
        ↓
WEEK 7
│
├── Memory
├── RAG
└── Agentic RAG
        ↓
WEEK 8
│
├── Evaluation
├── Tracing
├── AgentArena
└── Critique Loop
```

---

# 25. One very important rule for GenAI Labs

For **every framework**, don't just write:

```python
agent = Agent(...)
agent.run(...)
```

and move on.

Instead, implement the **same problem**:

> "Research a topic, use tools, verify the result, and produce structured output."

using:

```text
PydanticAI
LangChain
LangGraph
CrewAI
Strands
AutoGen
```

Then document:

```text
What is an Agent?
How does it call tools?
Where is state stored?
How does the loop work?
How does it retry?
How does it handle errors?
How does MCP integrate?
How does memory work?
How do I trace it?
How easy is it to customize?
```

That will teach you **agent engineering**, rather than just teaching you six Python libraries.

And I would make **Ollama + one consistent local model the invariant across the entire repository**. That way, when something changes between experiments, you know the difference came from the framework/architecture rather than the model.

[1]: https://github.com/microsoft/autogen?utm_source=chatgpt.com "microsoft/autogen: A programming framework for agentic AI"
[2]: https://pydantic.dev/docs/ai/models/ollama/?utm_source=chatgpt.com "Ollama | Pydantic Docs"
[3]: https://docs.ollama.com/api/openai-compatibility?utm_source=chatgpt.com "OpenAI compatibility"
[4]: https://github.com/modelcontextprotocol/python-sdk?utm_source=chatgpt.com "The official Python SDK for Model Context Protocol servers ..."
[5]: https://docs.langchain.com/oss/python/langchain/mcp?utm_source=chatgpt.com "Model Context Protocol (MCP) - Docs by LangChain"
[6]: https://docs.langchain.com/oss/python/integrations/providers/ollama?utm_source=chatgpt.com "Ollama integrations - Docs by LangChain"
[7]: https://www.langchain.com/langgraph?utm_source=chatgpt.com "LangGraph: Agent Orchestration Framework for Reliable AI ..."
[8]: https://docs.crewai.com/en/concepts/llms?utm_source=chatgpt.com "LLMs"
[9]: https://strandsagents.com/docs/user-guide/concepts/model-providers/ollama/?utm_source=chatgpt.com "Ollama | Strands Agents SDK"
[10]: https://microsoft.github.io/autogen/0.2/docs/topics/non-openai-models/local-ollama/?utm_source=chatgpt.com "Ollama | AutoGen 0.2"
