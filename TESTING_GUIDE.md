# Testing Guide - Multi-Agent Data Assistant with MCP

This guide walks you through testing your application locally.

## 🚀 Quick Start

### Option 1: Use the Startup Script (Easiest)

```bash
start_app.bat
```

This will:
- Start the backend API on port 8010 (with MCP servers)
- Start the frontend on port 8011
- Open the browser automatically

### Option 2: Manual Start

**Terminal 1 - Backend:**
```powershell
.\venv\Scripts\Activate.ps1
uvicorn server:app --host 0.0.0.0 --port 8010 --reload
```

**Terminal 2 - Frontend:**
```powershell
cd frontend
npm run dev -- --port 8011
```

---

## 📋 Configuration Checklist

### Backend (.env in root directory)
```env
# Database (for MCP db.query_supabase)
DATA_DB_TYPE=postgres
DATA_DSN=postgresql://user:password@host:port/database
# OR use your Supabase
DATA_TABLE=your_table_name

# Email (for MCP email.send_report)
SENDGRID_API_KEY=your_key
EMAIL_FROM=sender@example.com
EMAIL_TO=recipient@example.com

# OpenAI (optional)
OPENAI_API_KEY=your_key

# Supabase (for auth)
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_ANON_KEY=your_anon_key
SUPABASE_POOLER_DSN=postgresql://...
```

### Frontend (frontend/.env)
```env
VITE_API_BASE_URL=http://localhost:8010
VITE_SUPABASE_URL=https://your-project.supabase.co
VITE_SUPABASE_ANON_KEY=your_anon_key
VITE_APP_URL=http://localhost:8011
```

---

## 🧪 Testing Methods

### Method 1: Web UI (Frontend)

1. **Open**: http://localhost:8011
2. **Sign In** (if you have Supabase auth configured)
3. **Enter a question** like:
   - "Show me all data"
   - "Get sales from last week"
   - "Show me user statistics"
4. **Click "Run Query"**
5. **View results**:
   - Data preview table
   - Download CSV
   - Download PDF report
   - Email report (if configured)

### Method 2: API Docs (Swagger UI)

1. **Open**: http://localhost:8010/docs
2. **Try the `/run` endpoint**:
   - Click "Try it out"
   - Enter a question
   - Check "use_env": true
   - Click "Execute"
3. **View the response** with artifacts

### Method 3: PowerShell/cURL

```powershell
# Simple query
Invoke-RestMethod -Uri http://localhost:8010/run `
  -Method POST `
  -ContentType "application/json" `
  -Body '{"question":"Show me all data","use_env":true}'

# Check health
Invoke-RestMethod -Uri http://localhost:8010/health

# View logs
Invoke-RestMethod -Uri http://localhost:8010/logs?limit=20
```

### Method 4: Python Script

```python
import requests

# Run a query
response = requests.post('http://localhost:8010/run', json={
    'question': 'Show me all users',
    'use_env': True
})

result = response.json()
print(f"Status: {result['status']}")
print(f"Artifacts: {result['artifacts']}")
print(f"Preview: {result['preview']}")
```

---

## 🔍 Verify MCP Integration

### Check MCP Servers Started

Look for these in the backend console:
```
[Server] Initializing MCP servers...
[MCP] DB server started successfully
[MCP] Email server started successfully
[Server] MCP servers initialized successfully
```

### Check MCP Tool Calls in Logs

```powershell
# View logs
Invoke-RestMethod -Uri http://localhost:8010/logs?limit=50 | 
  ConvertTo-Json -Depth 10 | 
  Select-String "mcp"
```

Look for:
- `db_query_executed_mcp` - Database queries via MCP
- `email_done_mcp` - Emails sent via MCP

### Test MCP Tools Directly

```python
# Run this with backend running
from mcp_client import call_mcp_tool_sync, initialize_mcp_sync, cleanup_mcp_sync

initialize_mcp_sync()

# Test DB query
result = call_mcp_tool_sync("db", "db.query_supabase", {
    "query": "SELECT 1 as test",
    "limit": 10
})
print(result)

cleanup_mcp_sync()
```

---

## 📊 Test the Complete Flow

### Full "Query → Report → Email" Flow

1. **Make sure you have configured**:
   - ✅ DATA_DB_TYPE, DATA_TABLE (database)
   - ✅ SENDGRID_API_KEY, EMAIL_FROM, EMAIL_TO (email)

2. **Run a query** (any method above)

3. **Expected flow**:
   ```
   User Input
       ↓
   NLP Agent (parses query)
       ↓
   DB Agent → [MCP] db.query_supabase → Supabase
       ↓
   CSV Agent → Creates artifacts/data-*.csv
       ↓
   Report Agent → Creates artifacts/report-*.pdf
       ↓
   Email Agent → [MCP] email.send_report → SendGrid
       ↓
   Memory Agent → Saves to database
   ```

4. **Check results**:
   - ✅ Response status: "success"
   - ✅ Artifacts folder has new CSV and PDF files
   - ✅ Email received (check your inbox)
   - ✅ Logs show MCP calls

---

## 🎯 What to Test

### ✅ Basic Functionality
- [ ] Backend starts without errors
- [ ] Frontend loads in browser
- [ ] Health endpoint returns OK
- [ ] API docs are accessible

### ✅ MCP Integration
- [ ] MCP servers initialize on startup
- [ ] Database queries work through MCP
- [ ] Email sending works through MCP
- [ ] Logs show "via: mcp" entries

### ✅ Agent Flow
- [ ] Can submit a question
- [ ] NLP agent parses the question
- [ ] DB agent retrieves data
- [ ] CSV file is created
- [ ] PDF report is generated
- [ ] Email is sent (if configured)

### ✅ Frontend Features
- [ ] Sign in/authentication (if Supabase configured)
- [ ] Query input form
- [ ] Results display
- [ ] Download CSV button works
- [ ] Download PDF button works
- [ ] View logs page

### ✅ API Endpoints
- [ ] `POST /run` - Run query flow
- [ ] `GET /health` - Health check
- [ ] `GET /logs` - View logs
- [ ] `POST /db/test` - Test database connection
- [ ] `POST /scheduler/add` - Schedule jobs
- [ ] `GET /scheduler/list` - List scheduled jobs

---

## 🐛 Troubleshooting

### Backend won't start
```powershell
# Check if port is in use
netstat -ano | findstr :8010

# Activate venv
.\venv\Scripts\Activate.ps1

# Check Python version
python --version  # Should be 3.10+

# Reinstall dependencies
pip install -r requirements.txt
```

### Frontend won't start
```powershell
cd frontend

# Install dependencies
npm install

# Check Node version
node --version  # Should be 16+

# Start dev server
npm run dev -- --port 8011
```

### MCP servers not starting
- Check that `mcp_servers/` folder exists
- Verify `db_server.py` and `email_server.py` are present
- Check logs for initialization errors

### Database queries fail
- Verify `DATA_DB_TYPE=postgres` in .env
- Check `DATA_DSN` or `SUPABASE_POOLER_DSN` is set
- Test connection: 
  ```powershell
  python -c "from app.config import settings; from utils import db_utils; print(db_utils.connect(settings))"
  ```

### Email sending fails
- Verify `SENDGRID_API_KEY` is valid
- Check sender email is verified in SendGrid
- Confirm recipient emails are valid
- Look for error in logs: `http://localhost:8010/logs`

---

## 📁 Generated Files

After running queries, check the `artifacts/` folder:
```
artifacts/
  ├── data-20251111-123456.csv      # CSV export
  ├── chart-20251111-123456.png     # Chart image
  └── report-20251111-123456.pdf    # PDF report
```

These files are also served statically at:
- http://localhost:8010/artifacts/data-20251111-123456.csv
- http://localhost:8010/artifacts/report-20251111-123456.pdf

---

## 📝 Sample Questions to Try

```
"Show me all data"
"Get sales from last month"
"Show me top 10 customers"
"List recent orders"
"Display user statistics"
"Get revenue by category"
```

---

## 🎉 Success Indicators

You know everything is working when:
- ✅ Both servers start without errors
- ✅ Frontend loads and you can submit queries
- ✅ API returns 200 responses
- ✅ CSV and PDF files are created
- ✅ Logs show MCP tool calls
- ✅ Emails are received (if configured)

---

## 📚 Additional Resources

- **API Documentation**: http://localhost:8010/docs
- **MCP Integration Guide**: [MCP_INTEGRATION.md](MCP_INTEGRATION.md)
- **Architecture Details**: [ARCHITECTURE.md](ARCHITECTURE.md)
- **Detailed MCP Testing**: [TESTING_MCP.md](TESTING_MCP.md)

---

**Need help?** Check the console logs in both terminal windows for error messages!

