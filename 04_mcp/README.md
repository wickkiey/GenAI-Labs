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

---

# Phase 5: MCP Clients

**Folder:** `clients/`. `mcp_agent.py` holds the shared `MCPAgent` — the Phase-2-style
bounded tool loop, but dispatching tool calls over one or more MCP `ClientSession`s
instead of local Python functions.

- `raw_client.py` — connects to the calculator stdio server, converts its MCP tool
  schemas to OpenAI tool schemas, and drives them with `MCPAgent`.
- `multi_server.py` — connects to calculator + sqlite + filesystem at once and
  namespaces tool names (`calc__multiply`, `db__query_database`, `fs__read_file`)
  so the model can address any server without collisions.
- `http_client.py` — same as `raw_client.py`, but against the Dockerised
  `calculator_http` server over Streamable HTTP (start it first, see above).

Run:

```powershell
python 04_mcp/clients/raw_client.py "What is 1234 * 5678?"
python 04_mcp/clients/multi_server.py "How many employees are in Sales, then multiply that by 12?"
pytest tests/test_phase5.py -v
```

