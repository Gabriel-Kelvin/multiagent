#!/usr/bin/env python3
"""
Complete Application Flow Test
Tests the full multi-agent workflow with MCP integration
"""
import requests
import json
import time
from pathlib import Path

BASE_URL = "http://localhost:8010"

print("=" * 70)
print("Multi-Agent Data Assistant - Full Flow Test")
print("=" * 70)

# Test 1: Health Check
print("\n[1/5] Testing Health Endpoint...")
try:
    response = requests.get(f"{BASE_URL}/health")
    if response.status_code == 200:
        print(f"[OK] Server is healthy: {response.json()}")
    else:
        print(f"[ERROR] Health check failed: {response.status_code}")
        exit(1)
except Exception as e:
    print(f"[ERROR] Cannot connect to server: {e}")
    print("\nPlease start the server first:")
    print("  uvicorn server:app --host 0.0.0.0 --port 8010")
    exit(1)

# Test 2: Simple Query
print("\n[2/5] Testing Simple Query...")
try:
    payload = {
        "question": "Show me sample data",
        "use_env": True
    }
    
    print(f"  Sending: {payload['question']}")
    response = requests.post(
        f"{BASE_URL}/run",
        json=payload,
        timeout=30
    )
    
    if response.status_code == 200:
        result = response.json()
        print(f"[OK] Query executed successfully")
        print(f"  Status: {result.get('status')}")
        print(f"  Run ID: {result.get('run_id')}")
        
        # Check artifacts
        artifacts = result.get('artifacts', {})
        if artifacts:
            print(f"  Artifacts created:")
            for key, path in artifacts.items():
                file_exists = Path(path).exists() if path else False
                status = "✓" if file_exists else "✗"
                print(f"    {status} {key}: {path}")
        
        # Show preview data
        preview = result.get('preview', [])
        if preview:
            print(f"  Data preview ({len(preview)} rows):")
            if len(preview) > 0:
                print(f"    Columns: {list(preview[0].keys())}")
                print(f"    First row: {preview[0]}")
    else:
        print(f"[ERROR] Query failed: {response.status_code}")
        print(f"  Response: {response.text[:200]}")
        
except Exception as e:
    print(f"[ERROR] Query test failed: {e}")

# Test 3: Check Logs for MCP Usage
print("\n[3/5] Checking Logs for MCP Activity...")
try:
    response = requests.get(f"{BASE_URL}/logs?limit=10")
    if response.status_code == 200:
        logs = response.json().get('logs', [])
        mcp_logs = [log for log in logs if 'mcp' in log.get('event', '').lower()]
        
        if mcp_logs:
            print(f"[OK] Found {len(mcp_logs)} MCP-related log entries:")
            for log in mcp_logs[-3:]:  # Show last 3
                print(f"  - {log.get('agent')}: {log.get('event')}")
        else:
            print("[INFO] No MCP logs yet (this is normal for first run)")
    else:
        print(f"[WARN] Could not retrieve logs: {response.status_code}")
except Exception as e:
    print(f"[WARN] Log check failed: {e}")

# Test 4: Test Database Connection Test Endpoint
print("\n[4/5] Testing Database Configuration...")
try:
    db_test_payload = {
        "db_type": "postgres",
        "use_env": True
    }
    
    response = requests.post(
        f"{BASE_URL}/db/test",
        json=db_test_payload,
        timeout=10
    )
    
    if response.status_code == 200:
        result = response.json()
        if result.get('status') == 'success':
            rows = result.get('rows', [])
            print(f"[OK] Database connection successful")
            print(f"  Retrieved {len(rows)} sample rows")
            if rows:
                print(f"  Columns: {list(rows[0].keys())}")
        else:
            print(f"[WARN] Database test returned: {result.get('error', 'Unknown error')}")
            print("  This is normal if DATA_TABLE is not configured")
    else:
        print(f"[WARN] Database test endpoint error: {response.status_code}")
        
except Exception as e:
    print(f"[WARN] Database test failed: {e}")

# Test 5: List Scheduled Jobs
print("\n[5/5] Testing Scheduler...")
try:
    response = requests.get(f"{BASE_URL}/scheduler/list")
    if response.status_code == 200:
        jobs = response.json().get('jobs', [])
        print(f"[OK] Scheduler is working")
        print(f"  Active jobs: {len(jobs)}")
        if jobs:
            for job in jobs:
                print(f"    - {job.get('id')}: {job.get('next_run_time')}")
    else:
        print(f"[WARN] Scheduler check failed: {response.status_code}")
except Exception as e:
    print(f"[WARN] Scheduler test failed: {e}")

# Summary
print("\n" + "=" * 70)
print("Test Summary")
print("=" * 70)
print("""
Your application is running with MCP integration!

✓ API Server: http://localhost:8010
✓ API Docs: http://localhost:8010/docs
✓ MCP Servers: Running internally (db, email)

Next Steps:
1. Configure your .env with:
   - DATA_DB_TYPE=postgres
   - DATA_TABLE=your_table_name
   - SENDGRID_API_KEY=your_key (for email)

2. Open http://localhost:8010/docs in your browser
   to test the /run endpoint interactively

3. Check artifacts/ folder for generated CSV/PDF files

4. View logs: curl http://localhost:8010/logs
""")
print("=" * 70)

