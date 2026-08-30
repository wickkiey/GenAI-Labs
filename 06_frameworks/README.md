# Phase 7: Frameworks — Same Task, Six Times

**Objective:** Implement the same agent task using six different frameworks to understand
their strengths, weaknesses, and best use cases.

## The Invariant Task

```
Answer the question using calculator + sqlite tools, verify the result,
and return Answer(value, reasoning, tools_used, confidence).
```

All frameworks:
- Use the same Ollama model (`qwen3:8b`)
- Use the same tools (calculator + sqlite)
- Use the same 10 test questions
- Return the same `Answer` Pydantic model
- Run with temperature=0 for determinism

## Frameworks Implemented

### 7A: PydanticAI ⭐ Start here
**Best for:** Type-safe, structured outputs, small to medium agents

```powershell
pip install pydantic-ai
python 06_frameworks/pydantic_ai/06_the_spec_task.py "What is 1234 * 5678?"
```

**Strengths:**
- Excellent type safety and validation
- Structured output built-in
- Dependency injection pattern
- Clean API

**Weaknesses:**
- Smaller ecosystem than LangChain/LangGraph
- Fewer advanced patterns

---

### 7B: LangChain
**Best for:** Flexibility, RAG, memory management

```powershell
pip install langchain langchain-community langchain-ollama
python 06_frameworks/langchain/06_the_spec_task.py "What is 1234 * 5678?"
```

**Strengths:**
- Very flexible abstractions
- Huge ecosystem (memory, RAG, etc.)
- Mature and well-documented

**Weaknesses:**
- Abstraction layers can be opaque
- Verbose in places

---

### 7C: LangGraph ⭐⭐⭐ Most powerful for workflows
**Best for:** Complex multi-agent systems, state management, reproducible workflows

```powershell
pip install langgraph langchain-community langchain-ollama
python 06_frameworks/langgraph/10_the_spec_task.py "What is 1234 * 5678?"
```

**Strengths:**
- Graph-based architecture is intuitive for complex workflows
- State checkpointing and resumability
- Excellent for multi-agent systems
- Type-safe state management

**Weaknesses:**
- Steeper learning curve
- More verbose for simple tasks

---

### 7D: Strands
**Best for:** Reliability and observability

```powershell
pip install strands-agents strands-agents-tools
python 06_frameworks/strands/01_agent.py "What is 1234 * 5678?"
```

**Strengths:**
- Focus on reliability and retry logic
- Good observability features
- Production-ready error handling

**Weaknesses:**
- Smaller community
- Less documentation

---

### 7E: CrewAI ⚠️ Dependency conflicts possible
**Best for:** Multi-agent role-based systems, team-like workflows

```powershell
pip install crewai crewai-tools
python 06_frameworks/crewai/01_agent.py "What is 1234 * 5678?"

# If dependencies conflict with torch, use Docker:
docker-compose -f 06_frameworks/crewai/docker-compose.yml up
```

**Strengths:**
- Role-based agent design
- Task-oriented workflows
- Good for team-like multi-agent systems

**Weaknesses:**
- ⚠️ Aggressive dependency pinning (may break torch)
- May require Docker to avoid conflicts

---

### 7F: AutoGen ⚠️ Maintenance mode
**Best for:** Multi-agent conversations, human-in-the-loop

```powershell
pip install autogen-agentchat autogen-ext
python 06_frameworks/autogen/01_agent.py "What is 1234 * 5678?"

# If dependencies conflict:
docker-compose -f 06_frameworks/autogen/docker-compose.yml up
```

**Strengths:**
- Excellent conversational patterns
- Group chat support
- Human-in-the-loop capabilities

**Weaknesses:**
- ⚠️ In maintenance mode (v0.2)
- New API still stabilizing
- Consider LangGraph for new projects

---

## Test Suite

Shared test harness that validates all frameworks:

```powershell
# Run all framework tests
pytest tests/test_phase7.py -v

# Run individual framework
pytest tests/test_phase7.py::test_pydantic_ai -v

# Run framework script directly
python 06_frameworks/pydantic_ai/06_the_spec_task.py
```

Test validation:
- ✓ Returns valid `Answer` Pydantic model
- ✓ Has non-empty value and reasoning
- ✓ Lists correct tools used
- ✓ Confidence is one of ["high", "medium", "low"]
- ✓ All 10 test questions answered

---

## Framework Comparison Matrix

| Feature | PydanticAI | LangChain | LangGraph | Strands | CrewAI | AutoGen |
|---------|-----------|-----------|-----------|---------|--------|---------|
| Basic Agent | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| Tools | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| Structured Output | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| State/Memory | ✓ | ✓ | ⭐⭐⭐ | ✓ | ✓ | ✓ |
| Multi-Agent | ✓ | ✓ | ⭐⭐⭐ | ✓ | ⭐⭐ | ⭐⭐ |
| Graph Workflows | — | — | ⭐⭐⭐ | — | — | — |
| Human-in-Loop | ✓ | ✓ | ✓ | — | — | ⭐⭐ |
| RAG Support | ✓ | ⭐⭐⭐ | ✓ | ✓ | ✓ | — |
| Memory Management | ✓ | ⭐⭐ | ✓ | ✓ | ⭐ | ✓ |
| Production Ready | ✓ | ✓ | ✓ | ✓ | ⚠️ | ⚠️ |
| Dependency Safety | ✓ | ✓ | ✓ | ✓ | ⚠️ | ⚠️ |

---

## Installation Safety

Before installing each framework:

```powershell
# Snapshot current environment
pip freeze > requirements/snapshot_before_<framework>.txt

# Install framework
pip install <framework>

# Verify torch still works
python -c "import torch; print(torch.__version__)"
```

If a framework breaks torch, rollback:
```powershell
pip install -r requirements/snapshot_before_<framework>.txt
```

---

## Recommendations

**For Most Projects:** Start with **LangGraph**
- Most powerful and flexible
- Excellent for multi-agent systems
- Great state management

**For Type-Safe Agents:** Use **PydanticAI**
- Best type safety
- Cleanest API
- Good for structured outputs

**For RAG and Retrieval:** Use **LangChain**
- Largest ecosystem
- Best documented
- Most integrations

**For Team-Based Workflows:** Use **CrewAI**
- Role-based design
- Task-oriented
- But watch dependency conflicts

**Avoid for New Projects:** AutoGen v0.2 and Strands
- AutoGen: Use new autogen-agentchat instead
- Strands: Smaller ecosystem

---

## Next Steps

After Phase 7:
1. **Phase 8:** Multi-Agent patterns (researcher/writer, debate, etc.)
2. **Phase 9:** Memory and RAG systems
3. **Phase 10:** Evaluation and tracing
4. **Phase 11:** Capstone projects

---

## Quick Start Commands

```powershell
# PydanticAI (recommended to start)
cd 06_frameworks/pydantic_ai
pip install pydantic-ai
python 06_the_spec_task.py "What is 1234 * 5678?"

# LangGraph (recommended for complex workflows)
cd 06_frameworks/langgraph
pip install langgraph langchain-community langchain-ollama
python 10_the_spec_task.py "What is 1234 * 5678?"

# Run full test suite
pytest tests/test_phase7.py -v
```

---

See individual framework READMEs for detailed information about each implementation.
