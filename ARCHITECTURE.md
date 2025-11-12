# MCP Integration Architecture

## System Overview

```
┌─────────────────────────────────────────────────────────────────────┐
│                         User Interface                              │
│  ┌───────────────────┐              ┌──────────────────────┐       │
│  │  Python main.py   │              │  FastAPI REST API    │       │
│  │  (CLI Interface)  │              │  (server.py)         │       │
│  └─────────┬─────────┘              └──────────┬───────────┘       │
└────────────┼────────────────────────────────────┼───────────────────┘
             │                                    │
             └────────────────┬───────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────────┐
│                      LangGraph Multi-Agent System                   │
│                           (main.py: build_app)                      │
│                                                                     │
│  ┌────────────┐  ┌────────────┐  ┌────────────┐  ┌────────────┐  │
│  │    NLP     │→ │     DB     │→ │    CSV     │→ │   Report   │  │
│  │   Agent    │  │   Agent    │  │   Agent    │  │   Agent    │  │
│  └────────────┘  └──────┬─────┘  └────────────┘  └────────────┘  │
│                         │                                │          │
│                         │ MCP Call                       │          │
│                         ▼                                ▼          │
│                  ┌────────────┐                   ┌────────────┐   │
│                  │   Email    │ ←─────────────── │ Supervisor │   │
│                  │   Agent    │  MCP Call        │   Agent    │   │
│                  └──────┬─────┘                   └────────────┘   │
└─────────────────────────┼──────────────────────────────────────────┘
                          │
                          │ MCP Call
                          ▼
┌─────────────────────────────────────────────────────────────────────┐
│                     MCP Client Manager                              │
│                      (mcp_client.py)                                │
│                                                                     │
│  ┌─────────────────────────────────────────────────────────────┐  │
│  │  - Manages MCP server subprocesses                           │  │
│  │  - Handles stdio communication                               │  │
│  │  - Provides sync/async wrappers                              │  │
│  │  - Automatic cleanup on shutdown                             │  │
│  └─────────────────────────────────────────────────────────────┘  │
│                                                                     │
│        ┌───────────────────────┬───────────────────────┐          │
└────────┼───────────────────────┼───────────────────────┼──────────┘
         │                       │                       │
         │ stdio                 │ stdio                 │ (future)
         ▼                       ▼                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌──────────────────┐
│  DB MCP Server  │    │ Email MCP Server│    │ External MCP     │
│  (subprocess)   │    │  (subprocess)   │    │ Servers          │
├─────────────────┤    ├─────────────────┤    ├──────────────────┤
│ Tool:           │    │ Tool:           │    │ - filesystem     │
│ db.query_       │    │ email.send_     │    │ - fetch          │
│ supabase        │    │ report          │    │ - custom tools   │
└────────┬────────┘    └────────┬────────┘    └──────────────────┘
         │                      │
         │                      │
         ▼                      ▼
┌─────────────────┐    ┌─────────────────┐
│  PostgreSQL/    │    │    SendGrid     │
│  Supabase DB    │    │    Email API    │
└─────────────────┘    └─────────────────┘
```

## Data Flow

### Example: "Show me sales data and email report"

```
1. User Input
   └─→ "Show me sales data and email report"

2. NLP Agent
   └─→ Parses query: "SELECT * FROM sales WHERE date > '2025-10-01'"

3. DB Agent
   ├─→ call_mcp_tool_sync("db", "db.query_supabase", {...})
   │   └─→ MCP Client Manager
   │       └─→ DB MCP Server (subprocess)
   │           ├─→ Validates query (SELECT only)
   │           ├─→ Adds LIMIT if needed
   │           └─→ db_utils.execute_select(...)
   │               └─→ PostgreSQL/Supabase
   │                   └─→ Returns rows
   └─→ Returns data: [{date: '2025-10-01', sales: 1250}, ...]

4. CSV Agent
   └─→ csv_utils.write_csv_rows(data)
       └─→ Creates: artifacts/data-20251111-123456.csv

5. Report Agent
   ├─→ chart_utils.make_bar_chart(data)
   │   └─→ Creates: artifacts/chart-20251111-123456.png
   └─→ pdf_utils.create_pdf_summary(...)
       └─→ Creates: artifacts/report-20251111-123456.pdf

6. Email Agent
   └─→ call_mcp_tool_sync("email", "email.send_report", {
         subject: "...",
         attachments: [csv_path, pdf_path]
       })
       └─→ MCP Client Manager
           └─→ Email MCP Server (subprocess)
               ├─→ Validates files exist
               ├─→ Reads file contents
               └─→ sendgrid_utils.send_email(...)
                   └─→ SendGrid API
                       └─→ Email sent ✓

7. Memory Agent
   └─→ Saves conversation to SQLite

8. Response to User
   └─→ {status: "success", artifacts: {...}}
```

## Component Responsibilities

### MCP Client Manager (`mcp_client.py`)
**Responsibilities:**
- Start MCP server subprocesses
- Manage stdio streams (read/write)
- Route tool calls to correct servers
- Handle sync/async event loop issues
- Clean shutdown of all servers

**Key Methods:**
```python
initialize()           # Start all MCP servers
call_tool(server, tool, args)  # Call a tool
list_tools(server)     # Discover available tools
cleanup()             # Shutdown all servers
```

### DB MCP Server (`mcp_servers/db_server.py`)
**Responsibilities:**
- Expose `db.query_supabase` tool
- Validate SQL queries (SELECT only)
- Apply automatic LIMIT
- Execute queries via db_utils
- Return results as JSON

**Safety Features:**
- Regex validation: blocks INSERT, UPDATE, DELETE, DROP, etc.
- Automatic LIMIT injection if missing
- Exception handling and error reporting

### Email MCP Server (`mcp_servers/email_server.py`)
**Responsibilities:**
- Expose `email.send_report` tool
- Validate email parameters
- Check file attachments exist
- Send emails via SendGrid
- Return status

**Safety Features:**
- File existence validation
- Email address validation
- API key requirement
- Attachment mime type handling

## Lifecycle Management

### Startup Sequence

#### FastAPI Server (server.py)
```python
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    initialize_mcp_sync()  # Start MCP servers
    yield
    # Shutdown
    cleanup_mcp_sync()     # Stop MCP servers

app = FastAPI(lifespan=lifespan)
```

#### Direct Execution (main.py)
```python
if __name__ == "__main__":
    initialize_mcp_sync()  # Start MCP servers
    try:
        result = run_once(question)
    finally:
        cleanup_mcp_sync()  # Stop MCP servers
```

### Process Hierarchy

```
uvicorn (PID 1000)
└─→ Python FastAPI app (PID 1001)
    └─→ MCP Client Manager
        ├─→ DB Server subprocess (PID 1002)
        │   └─→ stdio communication
        └─→ Email Server subprocess (PID 1003)
            └─→ stdio communication
```

On CTRL+C:
1. FastAPI receives SIGINT
2. Lifespan shutdown triggered
3. `cleanup_mcp_sync()` called
4. All MCP sessions closed
5. All MCP subprocesses terminated
6. FastAPI exits

## Communication Protocol

### Tool Call Flow

```
Agent                MCP Client        MCP Server         External Service
  │                     │                   │                    │
  │ call_tool_sync()    │                   │                    │
  ├──────────────────→  │                   │                    │
  │                     │                   │                    │
  │                     │ call_tool()       │                    │
  │                     ├──────────────────→│                    │
  │                     │    (JSON-RPC)     │                    │
  │                     │                   │                    │
  │                     │                   │ execute()          │
  │                     │                   ├───────────────────→│
  │                     │                   │                    │
  │                     │                   │ ← result           │
  │                     │                   │←───────────────────┤
  │                     │                   │                    │
  │                     │ ← response        │                    │
  │                     │←──────────────────┤                    │
  │                     │  (JSON-RPC)       │                    │
  │                     │                   │                    │
  │ ← result           │                   │                    │
  │←──────────────────  │                   │                    │
  │                     │                   │                    │
```

### Message Format

#### Request (Agent → MCP Server):
```json
{
  "jsonrpc": "2.0",
  "method": "tools/call",
  "params": {
    "name": "db.query_supabase",
    "arguments": {
      "query": "SELECT * FROM users LIMIT 10",
      "limit": 10
    }
  },
  "id": 1
}
```

#### Response (MCP Server → Agent):
```json
{
  "jsonrpc": "2.0",
  "result": {
    "content": [
      {
        "type": "text",
        "text": "{\"status\":\"success\",\"rows\":[...],\"count\":10}"
      }
    ]
  },
  "id": 1
}
```

## Error Handling

### Error Propagation

```
External Service Error
    ↓
MCP Server catches & formats
    ↓
Returns {"status": "error", "error": "..."}
    ↓
MCP Client receives response
    ↓
Agent receives error dict
    ↓
Agent handles gracefully (log, skip, retry)
    ↓
Workflow continues or exits cleanly
```

### Example Error Handling

```python
# In DB Agent
try:
    result = call_mcp_tool_sync("db", "db.query_supabase", {...})
    if result.get("status") == "error":
        logger.error(run_id, "db", "query_failed", result)
        return {"status": "error", "data": {}}
    rows = result.get("rows", [])
except Exception as e:
    logger.exception(run_id, "db", "mcp_error", {"error": str(e)})
    return {"status": "error", "data": {}}
```

## Security Considerations

### Query Validation (DB Server)
```python
FORBIDDEN = re.compile(
    r"\b(insert|update|delete|drop|alter|create|truncate|grant|revoke)\b",
    re.IGNORECASE
)

def is_safe_select(query: str) -> bool:
    if not SELECT_START.search(query):
        return False
    if FORBIDDEN.search(query):
        return False
    return True
```

### File Validation (Email Server)
```python
for att in attachments:
    file_path = att.get("file_path")
    if not os.path.exists(file_path):
        return error("File not found")
    # Only allow files from artifacts directory
    if not os.path.abspath(file_path).startswith(ARTIFACTS_DIR):
        return error("Access denied")
```

## Performance Characteristics

### Overhead
- MCP initialization: 1-2 seconds (one-time)
- Tool call overhead: 5-20ms per call
- Subprocess communication: 1-5ms
- JSON serialization: < 1ms

### Optimization Opportunities
1. **Connection pooling**: Reuse database connections in MCP server
2. **Caching**: Cache frequent queries
3. **Batch operations**: Send multiple tool calls in one request
4. **Process reuse**: Keep MCP servers running between requests

## Scalability

### Current Design
- Single MCP server instance per tool type
- Stdio communication (single-threaded)
- Suitable for: Single server, moderate load

### Future Scaling Options
1. **Multiple server instances**: Run multiple DB/Email servers
2. **HTTP transport**: Replace stdio with HTTP for network distribution
3. **Load balancing**: Route tool calls to least-busy server
4. **Async tool calls**: Parallel execution of multiple tools

## Extension Points

### Adding a New MCP Tool

1. **Create server file:**
```python
# mcp_servers/new_tool_server.py
app = Server("new-tool-server")

@app.list_tools()
async def list_tools():
    return [Tool(name="new.tool", ...)]

@app.call_tool()
async def call_tool(name, arguments):
    # Implementation
    pass
```

2. **Register in client manager:**
```python
# mcp_client.py
async def _start_new_tool_server(self):
    # Similar to _start_db_server
    pass

async def initialize(self):
    await self._start_new_tool_server()
```

3. **Use in agent:**
```python
# agents/new_agent.py
result = call_mcp_tool_sync("new-tool", "new.tool", {...})
```

## Monitoring & Observability

### Logs to Watch
```
[MCP] DB server started successfully
[MCP] Email server started successfully
db: db_query_executed_mcp - {'rows': 42, 'via': 'mcp'}
email: email_done_mcp - {'status': 'success', 'via': 'mcp'}
```

### Metrics to Track
- MCP server uptime
- Tool call latency
- Tool call success/failure rate
- Query validation failures
- Email delivery rate

## Troubleshooting Guide

### Problem: MCP servers not starting
**Check:**
- Python can find `mcp` module
- Server scripts exist in `mcp_servers/`
- File permissions allow execution

### Problem: Tool calls failing
**Check:**
- MCP servers are running (`ps aux | grep mcp_servers`)
- Stdio streams not blocked
- Event loop issues (use `call_mcp_tool_sync` in sync code)

### Problem: Performance degradation
**Check:**
- MCP server memory usage
- Number of open file descriptors
- Database connection pool exhaustion
- Event loop blocked by long-running operations

---

**See Also:**
- [MCP_INTEGRATION.md](MCP_INTEGRATION.md) - Integration details
- [TESTING_MCP.md](TESTING_MCP.md) - Testing procedures
- [MCP Specification](https://modelcontextprotocol.io/)

