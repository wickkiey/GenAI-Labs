# Phase 7 Quick Start Guide

## 🚀 Get Started in 5 Minutes

### 1. Understand the Task
All frameworks solve the same problem:
```
Question: "What is 1234 * 5678?"
Answer:
{
  "value": "7006652",
  "reasoning": "Used calculator tool for multiplication",
  "tools_used": ["calculator"],
  "confidence": "high"
}
```

### 2. Choose Your Framework

**I want the cleanest code:**
```bash
cd 06_frameworks/pydantic_ai
pip install pydantic-ai
python 06_the_spec_task.py "What is 1234 * 5678?"
```

**I want the most powerful:**
```bash
cd 06_frameworks/langgraph
pip install langgraph langchain langchain-community
python 10_the_spec_task.py "What is 1234 * 5678?"
```

**I want maximum flexibility:**
```bash
cd 06_frameworks/langchain
pip install langchain langchain-community langchain-ollama
python 06_the_spec_task.py "What is 1234 * 5678?"
```

### 3. Run Tests

```bash
# Run single framework
python 06_frameworks/pydantic_ai/06_the_spec_task.py

# Run all frameworks (if installed)
pytest tests/test_phase7.py -v

# Run specific test
pytest tests/test_phase7.py::test_pydantic_ai -v
```

### 4. Compare Results

See `06_frameworks/README.md` for:
- Feature comparison matrix
- Strengths/weaknesses of each
- When to use which framework
- Installation safety tips

---

## 📋 Implementation Checklist

After each framework:
- [ ] Script runs without errors
- [ ] Returns valid Answer model with all fields
- [ ] All 10 test questions answered (or at least 8/10)
- [ ] torch still works: `python -c "import torch"`
- [ ] No dependency conflicts
- [ ] README completed with findings

---

## 🔒 Safety First

Before installing a new framework:

```bash
# 1. Backup current environment
pip freeze > requirements/snapshot_before_<framework>.txt

# 2. Install
pip install <framework_deps>

# 3. Verify torch works
python -c "import torch; print(torch.__version__)"

# 4. If broken, restore
pip install -r requirements/snapshot_before_<framework>.txt

# 5. If conflicts persist, use Docker
docker-compose -f 06_frameworks/<framework>/docker-compose.yml up
```

---

## 📊 Framework Recommendations

| Need | Framework | Why |
|------|-----------|-----|
| Type safety | PydanticAI | Built-in Pydantic validation |
| Workflow control | LangGraph | Graph-based state management |
| RAG + tools | LangChain | Largest ecosystem |
| Team agents | CrewAI | Role-based design |
| Multi-agent chat | AutoGen | Conversation patterns |
| Reliability | Strands | Error handling focus |

---

## 🚨 Known Issues & Solutions

**CrewAI / AutoGen won't install:**
```bash
# Solution: Use Docker
docker-compose -f 06_frameworks/crewai/docker-compose.yml up
```

**torch breaks after install:**
```bash
# Solution: Rollback
pip install -r requirements/snapshot_before_<framework>.txt

# Then use Docker for that framework
```

**Ollama not responding:**
```bash
# Make sure Ollama is running
ollama serve

# In another terminal
ollama pull qwen3:8b
python 06_frameworks/pydantic_ai/06_the_spec_task.py
```

---

## 📚 Learning Path

1. **Start:** PydanticAI (clearest patterns)
2. **Expand:** LangChain (flexibility)
3. **Master:** LangGraph (advanced workflows)
4. **Explore:** Others as needed

---

## 💡 Key Takeaways

After Phase 7, you'll understand:
- ✓ What each framework does well
- ✓ How to implement the same task 6 ways
- ✓ Trade-offs between frameworks
- ✓ When to use which framework
- ✓ How to handle dependency conflicts
- ✓ How to build production-ready agents

---

**Next Phase:** Phase 8 - Multi-Agent Patterns
(researcher/writer, debate, critique loop)

Questions? See `06_frameworks/README.md` for detailed framework docs.
