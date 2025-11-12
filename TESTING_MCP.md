# Testing MCP Integration

This guide walks through testing the MCP integration step by step.

## Prerequisites

1. Python 3.10+ installed
2. Dependencies installed: `pip install -r requirements.txt`
3. `.env` file configured (copy from `env.example`)

## Test 1: MCP Server Initialization

This test verifies that MCP servers can start and communicate.

```bash
python test_mcp_integration.py
```

**Expected Output:**
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
```

**What This Tests:**
- ✓ MCP servers can be started as subprocesses
- ✓ Stdio communication works between client and servers
- ✓ Tools are discoverable via `list_tools()`
- ✓ Basic tool calls work

## Test 2: Database Query via MCP

Test the `db.query_supabase` tool with a real database.

### Prerequisites:
Configure in `.env`:
```env
DATA_DB_TYPE=postgres
DATA_DSN=postgresql://user:password@host:port/database
DATA_TABLE=your_table_name
```

### Test Commands:

```python
python -c "
from mcp_client import call_mcp_tool_sync, initialize_mcp_sync, cleanup_mcp_sync
import json

initialize_mcp_sync()

# Test simple query
result = call_mcp_tool_sync('db', 'db.query_supabase', {
    'query': 'SELECT 1 as test, NOW() as timestamp',
    'limit': 10
})

print(json.dumps(result, indent=2, default=str))
cleanup_mcp_sync()
"
```

**Expected Output:**
```json
{
  "status": "success",
  "rows": [
    {
      "test": 1,
      "timestamp": "2025-11-11 12:34:56"
    }
  ],
  "count": 1,
  "query": "SELECT 1 as test, NOW() as timestamp LIMIT 10"
}
```

**What This Tests:**
- ✓ Database connection works
- ✓ Query validation (SELECT-only)
- ✓ Automatic LIMIT clause injection
- ✓ Result parsing and JSON serialization

### Test Query Safety:

```python
python -c "
from mcp_client import call_mcp_tool_sync, initialize_mcp_sync, cleanup_mcp_sync
import json

initialize_mcp_sync()

# This should FAIL (unsafe query)
result = call_mcp_tool_sync('db', 'db.query_supabase', {
    'query': 'DROP TABLE users',
    'limit': 10
})

print(json.dumps(result, indent=2))
cleanup_mcp_sync()
"
```

**Expected Output:**
```json
{
  "status": "error",
  "error": "Only SELECT queries are allowed. INSERT, UPDATE, DELETE, DROP, etc. are forbidden."
}
```

**What This Tests:**
- ✓ Query validation prevents dangerous operations

## Test 3: Email Sending via MCP

Test the `email.send_report` tool.

### Prerequisites:
Configure in `.env`:
```env
SENDGRID_API_KEY=your_sendgrid_api_key
EMAIL_FROM=sender@example.com
EMAIL_TO=recipient@example.com
```

Create test files:
```bash
echo "test,data" > test.csv
echo "Test PDF content" > test.txt
```

### Test Command:

```python
python -c "
from mcp_client import call_mcp_tool_sync, initialize_mcp_sync, cleanup_mcp_sync
import json
import os

initialize_mcp_sync()

# Create a simple test file
with open('test_attachment.txt', 'w') as f:
    f.write('This is a test attachment.')

result = call_mcp_tool_sync('email', 'email.send_report', {
    'subject': 'MCP Test Email',
    'body_text': 'This is a test email sent via MCP.',
    'to_emails': ['your@email.com'],  # Replace with your email
    'from_email': 'sender@example.com',  # Replace with your sender email
    'attachments': [
        {
            'file_path': 'test_attachment.txt',
            'mime_type': 'text/plain',
            'file_name': 'test.txt'
        }
    ]
})

print(json.dumps(result, indent=2))

# Cleanup
os.remove('test_attachment.txt')
cleanup_mcp_sync()
"
```

**Expected Output:**
```json
{
  "status": "success",
  "data": {
    "status_code": 202
  }
}
```

**What This Tests:**
- ✓ SendGrid API integration
- ✓ File attachment handling
- ✓ Email validation

## Test 4: Full Agent Flow

Test the complete multi-agent workflow using MCP tools.

### Prerequisites:
- Database configured and accessible
- SendGrid configured
- `.env` file complete

### Test via Direct Execution:

```bash
python main.py
```

**Interaction:**
```
[Main] Initializing MCP servers...
[MCP] DB server started successfully
[MCP] Email server started successfully
[Main] MCP servers ready
Enter question: Show me all users
```

**Expected Flow:**
1. NLP Agent parses the question
2. DB Agent calls `db.query_supabase` via MCP
3. CSV Agent creates a CSV file (direct file I/O)
4. Report Agent generates a PDF with chart
5. Email Agent calls `email.send_report` via MCP
6. Memory Agent saves the conversation

**Check Logs:**
```bash
# View recent logs
python -c "
from app.database import Database
from app.config import settings

db = Database(settings.DB_PATH)
logs = db.get_logs(limit=20)

for log in logs:
    if 'mcp' in log.get('event', '').lower():
        print(f'{log[\"agent\"]}: {log[\"event\"]} - {log.get(\"data\", {})}')
"
```

**Expected Log Entries:**
```
db: db_query_executed_mcp - {'rows': 42, 'via': 'mcp'}
email: email_done_mcp - {'status': 'success', 'via': 'mcp'}
```

**What This Tests:**
- ✓ Complete workflow integration
- ✓ MCP tools called correctly from agents
- ✓ State passing between agents
- ✓ Artifact creation (CSV, PDF)
- ✓ Email delivery with attachments

## Test 5: API Server with MCP

Test the FastAPI server with MCP integration.

### Start the Server:

```bash
uvicorn server:app --host 0.0.0.0 --port 8010
```

**Expected Startup Output:**
```
[Server] Initializing MCP servers...
[MCP] DB server started successfully
[MCP] Email server started successfully
[Server] MCP servers initialized successfully
INFO:     Uvicorn running on http://0.0.0.0:8010 (Press CTRL+C to quit)
```

### Test via API:

```bash
curl -X POST http://localhost:8010/run \
  -H "Content-Type: application/json" \
  -d '{
    "question": "Show me sales data for last month",
    "use_env": true
  }'
```

**Expected Response:**
```json
{
  "status": "success",
  "artifacts": {
    "csv_path": "artifacts/data-20251111-123456.csv",
    "pdf_path": "artifacts/report-20251111-123456.pdf"
  },
  "preview": [
    {"date": "2025-10-01", "sales": 1250.00},
    {"date": "2025-10-02", "sales": 1430.00}
  ],
  "run_id": "abc-123-def-456"
}
```

**What This Tests:**
- ✓ FastAPI lifespan events initialize MCP
- ✓ API endpoints work with MCP integration
- ✓ Multiple concurrent requests handled correctly

### Test Server Shutdown:

Press `CTRL+C` in the server terminal.

**Expected Shutdown Output:**
```
INFO:     Shutting down
[Server] Shutting down MCP servers...
[MCP] All MCP connections cleaned up
[Server] MCP servers shut down successfully
```

**What This Tests:**
- ✓ Clean shutdown of MCP servers
- ✓ No orphaned processes

## Test 6: Error Handling

Test that errors are handled gracefully.

### Test Invalid Query:

```python
python -c "
from mcp_client import call_mcp_tool_sync, initialize_mcp_sync, cleanup_mcp_sync
import json

initialize_mcp_sync()

result = call_mcp_tool_sync('db', 'db.query_supabase', {
    'query': 'SELECT * FROM nonexistent_table',
    'limit': 10
})

print('Status:', result.get('status'))
print('Error:', result.get('error', 'No error'))

cleanup_mcp_sync()
"
```

**Expected Output:**
```
Status: error
Error: relation "nonexistent_table" does not exist
```

### Test Missing Attachment:

```python
python -c "
from mcp_client import call_mcp_tool_sync, initialize_mcp_sync, cleanup_mcp_sync
import json

initialize_mcp_sync()

result = call_mcp_tool_sync('email', 'email.send_report', {
    'subject': 'Test',
    'body_text': 'Test',
    'to_emails': ['test@example.com'],
    'from_email': 'sender@example.com',
    'attachments': [{'file_path': '/nonexistent/file.pdf'}]
})

print('Status:', result.get('status'))
print('Error:', result.get('error', 'No error'))

cleanup_mcp_sync()
"
```

**Expected Output:**
```
Status: error
Error: Attachment file not found: /nonexistent/file.pdf
```

**What This Tests:**
- ✓ Database errors are caught and reported
- ✓ File validation before email sending
- ✓ Graceful error handling throughout

## Troubleshooting Common Issues

### Issue: MCP servers don't start

**Symptoms:**
```
[Server] Warning: Failed to initialize MCP servers
ModuleNotFoundError: No module named 'mcp'
```

**Solution:**
```bash
pip install mcp httpx
```

### Issue: Database connection fails

**Symptoms:**
```
Status: error
Error: could not connect to server
```

**Solution:**
1. Check `.env` database configuration
2. Test connection manually:
```bash
python -c "from utils import db_utils; from app.config import settings; print(db_utils.connect(settings))"
```

### Issue: Email sending fails

**Symptoms:**
```
Status: error
Error: The provided authorization grant is invalid
```

**Solution:**
1. Verify `SENDGRID_API_KEY` in `.env`
2. Check API key has send permissions in SendGrid dashboard
3. Verify sender email is authorized

### Issue: Event loop conflicts

**Symptoms:**
```
RuntimeError: This event loop is already running
```

**Solution:**
This should be handled automatically by `call_mcp_tool_sync()`. If you see this error, ensure you're using the `_sync` version of functions when calling from synchronous code.

## Performance Testing

Test MCP overhead and throughput.

```python
import time
from mcp_client import call_mcp_tool_sync, initialize_mcp_sync, cleanup_mcp_sync

initialize_mcp_sync()

# Warm up
for _ in range(3):
    call_mcp_tool_sync('db', 'db.query_supabase', {
        'query': 'SELECT 1',
        'limit': 1
    })

# Benchmark
iterations = 100
start = time.time()

for _ in range(iterations):
    result = call_mcp_tool_sync('db', 'db.query_supabase', {
        'query': 'SELECT 1',
        'limit': 1
    })
    assert result['status'] == 'success'

elapsed = time.time() - start
print(f"Completed {iterations} queries in {elapsed:.2f}s")
print(f"Average: {(elapsed/iterations)*1000:.2f}ms per query")

cleanup_mcp_sync()
```

**Expected Performance:**
- Cold start: 1-2 seconds (server initialization)
- Warm queries: 10-50ms per query (depending on database latency)

## Summary

After completing all tests, you should have verified:

- ✓ MCP servers start and communicate correctly
- ✓ Database queries work via MCP
- ✓ Email sending works via MCP
- ✓ Full agent workflow uses MCP tools
- ✓ API server integrates MCP properly
- ✓ Error handling is robust
- ✓ Performance is acceptable

If any test fails, refer to the troubleshooting section or [MCP_INTEGRATION.md](MCP_INTEGRATION.md) for more details.

