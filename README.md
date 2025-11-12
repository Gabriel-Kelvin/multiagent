# Multi-Agent Data Assistant

- Python 3.10+
- LangGraph + LangChain
- **MCP (Model Context Protocol)** for tool integration
- SendGrid for email
- APScheduler for scheduling
- SQLite for state + logs
- fpdf2 for PDF generation

## Features

✨ **NEW: MCP Integration**
- Modular tool architecture using Model Context Protocol
- Internal MCP servers for database queries and email sending
- Clean separation between agent logic and tool implementations
- Easy to extend with new tools

## Quick Start

### 1. Install Dependencies

```bash
# Linux/Mac
chmod +x setup_mcp.sh
./setup_mcp.sh

# Windows
setup_mcp.bat

# Or manually
pip install -r requirements.txt
```

### 2. Configure Environment

Create `.env` from `env.example` and fill in:

```env
# Database (for db.query_supabase MCP tool)
DATA_DB_TYPE=postgres
DATA_DSN=postgresql://user:password@host:port/database
DATA_TABLE=your_table_name

# Email (for email.send_report MCP tool)
SENDGRID_API_KEY=your_key
EMAIL_FROM=sender@example.com
EMAIL_TO=recipient@example.com

# OpenAI (optional, for NLP)
OPENAI_API_KEY=your_key
```

### 3. Run the Application

```bash
# Option 1: Direct execution
python main.py

# Option 2: Start the API server
uvicorn server:app --host 0.0.0.0 --port 8010
```

### 4. Test MCP Integration

```bash
python test_mcp_integration.py
```

## Architecture

```
User Input
    ↓
NLP Agent (parses query)
    ↓
DB Agent → MCP: db.query_supabase → Supabase/PostgreSQL
    ↓
CSV Agent (creates CSV file)
    ↓
Report Agent (generates PDF)
    ↓
Email Agent → MCP: email.send_report → SendGrid
    ↓
Logs & Memory
```

## MCP Tools

### Internal MCP Servers

1. **db.query_supabase** (`mcp_servers/db_server.py`)
   - Execute safe, read-only SQL queries
   - Automatic query validation (SELECT-only)
   - Supports PostgreSQL, MySQL, SQLite

2. **email.send_report** (`mcp_servers/email_server.py`)
   - Send emails with attachments via SendGrid
   - Support for CSV, PDF, and other file types

See [MCP_INTEGRATION.md](MCP_INTEGRATION.md) for detailed documentation.

## API Endpoints

- `POST /run` - Run the multi-agent flow
- `GET /health` - Health check
- `GET /logs` - Retrieve logs
- `POST /scheduler/add` - Schedule recurring jobs
- `GET /scheduler/list` - List scheduled jobs

## Notes

- MCP servers start automatically with the backend
- Email sending is skipped if SendGrid config is missing
- NLP uses OpenAI when configured; otherwise uses a safe mock path
- All tool calls go through MCP for better observability and modularity
