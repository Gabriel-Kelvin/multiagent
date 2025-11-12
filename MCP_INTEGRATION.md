# MCP Integration Guide

This document describes the MCP (Model Context Protocol) integration in the Multi-Agent Data Assistant.

## Overview

The application now uses MCP to modularize and standardize tool calls across agents. MCP provides a clean separation between the agent logic and the actual tool implementations.

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│                   FastAPI Server                        │
│                    (server.py)                          │
└────────────────────────┬────────────────────────────────┘
                         │
                         ▼
          ┌──────────────────────────────┐
          │     MCP Client Manager        │
          │      (mcp_client.py)          │
          └──────────────┬────────────────┘
                         │
          ┌──────────────┴────────────────┐
          │                               │
          ▼                               ▼
┌──────────────────┐          ┌──────────────────┐
│   DB MCP Server  │          │ Email MCP Server │
│  (db_server.py)  │          │ (email_server.py)│
└──────────────────┘          └──────────────────┘
          │                               │
          ▼                               ▼
┌──────────────────┐          ┌──────────────────┐
│  Supabase/PG DB  │          │     SendGrid     │
└──────────────────┘          └──────────────────┘
```

## Components

### 1. MCP Servers (Internal)

#### a. Database Server (`mcp_servers/db_server.py`)
- **Tool**: `db.query_supabase`
- **Purpose**: Execute safe, read-only SQL queries on PostgreSQL/Supabase
- **Features**:
  - Validates queries are SELECT-only (no INSERT, UPDATE, DELETE, DROP, etc.)
  - Automatically applies LIMIT if not present
  - Supports PostgreSQL, MySQL, and SQLite

#### b. Email Server (`mcp_servers/email_server.py`)
- **Tool**: `email.send_report`
- **Purpose**: Send emails with attachments via SendGrid
- **Features**:
  - Support for multiple recipients
  - File attachments (CSV, PDF, etc.)
  - Validates file existence before sending

### 2. MCP Client Manager (`mcp_client.py`)

The client manager handles:
- Starting MCP servers as subprocesses
- Managing stdio communication with servers
- Providing a simple API for agents to call tools
- Cleanup on shutdown

**Key Functions**:
```python
# Initialize all MCP servers
initialize_mcp_sync()

# Call a tool
result = call_mcp_tool_sync("db", "db.query_supabase", {
    "query": "SELECT * FROM users LIMIT 10",
    "limit": 10
})

# Cleanup
cleanup_mcp_sync()
```

### 3. Updated Agents

#### DB Agent (`agents/db_agent.py`)
Now uses `db.query_supabase` MCP tool instead of direct `db_utils` calls:
```python
result = call_mcp_tool_sync("db", "db.query_supabase", {
    "query": sql_query,
    "limit": 500
})
```

#### Email Agent (`agents/email_agent.py`)
Now uses `email.send_report` MCP tool instead of direct `sendgrid_utils` calls:
```python
result = call_mcp_tool_sync("email", "email.send_report", {
    "subject": "Report",
    "body_text": "See attached",
    "to_emails": ["user@example.com"],
    "from_email": "sender@example.com",
    "attachments": [...]
})
```

#### CSV Agent (`agents/csv_agent.py`)
Continues to use direct file I/O (filesystem MCP integration is optional for simple operations).

## Installation & Setup

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

This includes:
- `mcp` - MCP SDK
- `httpx` - HTTP client for MCP
- All existing dependencies

### 2. Configure Environment

Your `.env` file should include:

```env
# Database Configuration (for db.query_supabase)
DATA_DB_TYPE=postgres
DATA_DSN=postgresql://user:password@host:port/database
# or use individual parameters:
DATA_HOST=localhost
DATA_PORT=5432
DATA_NAME=your_database
DATA_USER=your_user
DATA_PASSWORD=your_password
DATA_TABLE=your_table_name

# Email Configuration (for email.send_report)
SENDGRID_API_KEY=your_sendgrid_api_key
EMAIL_FROM=sender@example.com
EMAIL_TO=recipient1@example.com,recipient2@example.com
```

### 3. Test MCP Integration

Run the test script to verify MCP servers start correctly:

```bash
python test_mcp_integration.py
```

Expected output:
```
============================================================
Testing MCP Integration
============================================================

[1/4] Initializing MCP servers...
[MCP] DB server started successfully
[MCP] Email server started successfully
✓ MCP servers initialized successfully

[2/4] Testing DB Server - Listing tools...
✓ Found 1 DB tool(s):
  - db.query_supabase: Execute a safe, read-only SQL SELECT query...

[3/4] Testing Email Server - Listing tools...
✓ Found 1 Email tool(s):
  - email.send_report: Send an email with optional file attachments...

[4/4] Testing DB Query Tool...
✓ DB query executed successfully
  Result: [{'test': 1, 'message': 'MCP Works!'}]
```

## Running the Application

### Option 1: Direct Execution (main.py)

```bash
python main.py
```

The MCP servers will be initialized automatically when the script starts.

### Option 2: FastAPI Server

```bash
uvicorn server:app --host 0.0.0.0 --port 8010
```

MCP servers are initialized automatically via FastAPI's lifespan events.

You should see:
```
[Server] Initializing MCP servers...
[MCP] DB server started successfully
[MCP] Email server started successfully
[Server] MCP servers initialized successfully
INFO:     Uvicorn running on http://0.0.0.0:8010
```

## Testing the Full Flow

### 1. Test via API

```bash
curl -X POST http://localhost:8010/run \
  -H "Content-Type: application/json" \
  -d '{
    "question": "Show me all users",
    "use_env": true
  }'
```

### 2. Test via Python Script

```python
from main import run_once

result = run_once("Show me all users")
print(result)
```

### 3. Check Logs

The application logs MCP operations:
- `db_query_executed_mcp` - DB queries via MCP
- `email_done_mcp` - Emails sent via MCP

Example log entry:
```json
{
  "run_id": "abc-123",
  "agent": "db",
  "event": "db_query_executed_mcp",
  "data": {"rows": 42, "via": "mcp"}
}
```

## Troubleshooting

### MCP Servers Not Starting

**Symptom**: `[Server] Warning: Failed to initialize MCP servers`

**Solutions**:
1. Ensure Python can find the `mcp` package: `pip install mcp`
2. Check that `mcp_servers/db_server.py` and `email_server.py` exist
3. Verify file permissions (servers need to be readable)

### DB Queries Failing

**Symptom**: `db.query_supabase` returns errors

**Solutions**:
1. Verify database configuration in `.env`
2. Test connection: `python -c "from utils import db_utils; from app.config import settings; print(db_utils.execute_select(settings, 'SELECT 1'))"`
3. Ensure query is a SELECT statement (INSERT/UPDATE/DELETE are forbidden)

### Email Sending Failing

**Symptom**: `email.send_report` returns errors

**Solutions**:
1. Verify SendGrid API key in `.env`
2. Check that attachments exist (CSV and PDF must be created first)
3. Verify recipient email addresses are valid

### Event Loop Issues

**Symptom**: `RuntimeError: This event loop is already running`

**Solution**: The `call_mcp_tool_sync()` function handles this automatically by detecting running loops and using a thread pool executor when necessary.

## Benefits of MCP Integration

1. **Modularity**: Tools are isolated in separate processes
2. **Safety**: MCP servers can validate inputs before execution
3. **Observability**: All tool calls go through a central manager
4. **Extensibility**: Easy to add new MCP servers for new capabilities
5. **Testing**: Mock MCP servers for testing without real services

## Future Enhancements

1. **External MCP Servers**: Connect to external filesystem and fetch servers
2. **Rate Limiting**: Add rate limiting to MCP tools
3. **Caching**: Cache MCP responses for frequently-used queries
4. **Monitoring**: Add metrics collection for MCP operations
5. **Security**: Add authentication/authorization for MCP tools

## Development

### Adding a New MCP Server

1. Create a new server file in `mcp_servers/`:

```python
# mcp_servers/my_server.py
from mcp.server import Server
from mcp.types import Tool, TextContent
from mcp.server.stdio import stdio_server

app = Server("my-server")

@app.list_tools()
async def list_tools() -> list[Tool]:
    return [Tool(name="my.tool", description="...", inputSchema={...})]

@app.call_tool()
async def call_tool(name: str, arguments: Any) -> Sequence[TextContent]:
    # Implementation
    pass
```

2. Update `mcp_client.py` to start the new server:

```python
async def _start_my_server(self):
    server_script = os.path.join(os.path.dirname(__file__), "mcp_servers", "my_server.py")
    # ... (similar to _start_db_server)
    self.sessions["my"] = session
```

3. Call the tool from an agent:

```python
result = call_mcp_tool_sync("my", "my.tool", {...})
```

## References

- [MCP Specification](https://modelcontextprotocol.io/)
- [MCP Python SDK](https://github.com/modelcontextprotocol/python-sdk)
- SendGrid API: https://sendgrid.com/docs/api-reference/
- Supabase/PostgreSQL: https://supabase.com/docs

