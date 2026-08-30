# Phase 4: MCP Servers

Four stdio MCP servers built with `mcp.server.fastmcp.FastMCP`, plus one calculator
variant over Streamable HTTP. Filesystem, SQLite, and knowledge servers are thin
`@mcp.tool()` wrappers around the Phase 3 tool functions in `03_tools/tools/` —
proving the separation between tool logic and tool protocol.

| Server | Tools | Transport |
| --- | --- | --- |
| `servers/calculator/server.py` | `add`, `subtract`, `multiply`, `divide` | stdio |
| `servers/filesystem/server.py` | `list_files`, `read_file`, `search_files` (sandboxed to `data/sandbox/`) | stdio |
| `servers/sqlite/server.py` | `list_tables`, `describe_table`, `query_database` (read-only) | stdio |
| `servers/knowledge/server.py` | `search_knowledge`, `get_document` | stdio |
| `servers/calculator_http/server.py` | same as calculator | Streamable HTTP, containerised |

## Manual check with the Inspector

```powershell
mcp dev 04_mcp/servers/calculator/server.py
```

List tools, call `multiply(1234, 5678)`, expect `7006652`.

## Automated tests (no LLM involved)

```powershell
pytest tests/test_mcp_servers.py -v
```

Each test spawns the target server over stdio via `mcp.client.stdio` and asserts:
- `list_tools()` returns the expected tool names
- each tool returns the correct result
- `divide(1, 0)` comes back as an MCP tool error, the server keeps running
- the filesystem server rejects path traversal, the sqlite server rejects writes

## HTTP variant

```powershell
docker compose -f 04_mcp/servers/calculator_http/docker-compose.yml up -d
curl http://localhost:8000/mcp
docker compose -f 04_mcp/servers/calculator_http/docker-compose.yml down
```
