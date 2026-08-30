# Phase 7C: LangGraph

LangGraph is specialized for building multi-agent systems and complex workflows using
a graph-based architecture. It's the most complex framework but provides the most control.

## Setup

```powershell
pip install langgraph langchain-community langchain-ollama
# Verify torch still works
python -c "import torch; print(torch.__version__)"
```

## Files

- `01_basic_graph.py` - Create a simple graph with nodes and edges
- `02_agent_node.py` - Add an LLM-based agent node
- `03_tool_node.py` - Add tool-calling node that executes tools
- `04_conditional_edges.py` - Route between nodes based on state
- `05_react_agent.py` - Implement the ReAct (Thought/Action/Observation) loop
- `06_checkpoint_memory.py` - Persist and resume graph state
- `07_human_in_loop.py` - Add human approval/intervention nodes
- `08_multi_agent.py` - Coordinate multiple agents sequentially
- `09_mcp.py` - Pattern for MCP server integration
- `10_the_spec_task.py` - Complete spec task implementation

## Key Concepts

- **StateGraph**: Define graph structure with typed state
- **Nodes**: Functions that transform state
- **Edges**: Connections between nodes
- **Conditional Edges**: Route based on state values
- **Checkpointer**: Persist state for resumability
- **AgentExecutor**: Embedded agent for tool calling

## Run Tests

```powershell
python 06_frameworks/langgraph/10_the_spec_task.py "What is 1234 * 5678?"
pytest tests/test_framework_langgraph.py -v
```

## What Surprised Me

- LangGraph's graph-first approach is very powerful for complex workflows
- Checkpointing and resumability work out-of-the-box
- The state type system ensures type safety across the entire graph
- Conditional edges enable sophisticated routing logic

## What Broke

- Initial SqliteSaver path issues - needed to create .checkpoints directory
- Conditional edge routing required careful node naming
- State updates must return complete state dict, not partial updates
