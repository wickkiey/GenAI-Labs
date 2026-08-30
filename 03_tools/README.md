# Phase 3: Tools

Five tools registered into a shared `tools.registry.TOOL_REGISTRY`, all backed by the
same `MultiToolAgent` used across `04_multiple_tools.py` and `05_error_handling.py`.

- `tools/calculator.py` — safe arithmetic via an AST whitelist, never raw `eval`.
- `tools/datetime_tool.py` — `get_current_time(timezone)`.
- `tools/filesystem.py` — `list_files` / `read_file`, sandboxed to `data/sandbox/`.
- `tools/sqlite_tool.py` — `list_tables` / `describe_table` / `query_database`, read-only
  (rejects anything that isn't a single `SELECT`), seeded on first use from
  `data/labs.db`.
- `tools/search.py` — keyword search over `data/docs/*.txt`.
- `04_multiple_tools.py` — gives the agent all tools and lets it pick.
- `05_error_handling.py` — a deliberately flaky tool that fails once, so the agent
  must recover from a tool error instead of crashing.

Run:

```powershell
python 03_tools/04_multiple_tools.py "How many employees are in Sales?"
python 03_tools/05_error_handling.py
pytest tests/test_tools.py -v
pytest tests/test_phase3.py -v
```
