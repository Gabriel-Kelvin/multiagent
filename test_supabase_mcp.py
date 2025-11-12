#!/usr/bin/env python3
"""
Quick test for Supabase connection through MCP
"""
from mcp_client import call_mcp_tool_sync, initialize_mcp_sync, cleanup_mcp_sync
from app.config import settings
import json

print("Testing Supabase Connection via MCP")
print("=" * 60)

# Check configuration
print("\nConfiguration:")
print(f"  DATA_DB_TYPE: {settings.DATA_DB_TYPE or '(not set)'}")
print(f"  Has DATA_DSN: {bool(settings.DATA_DSN)}")
print(f"  Has SUPABASE_POOLER_DSN: {bool(settings.SUPABASE_POOLER_DSN)}")
print(f"  Has SUPABASE_DIRECT_DSN: {bool(settings.SUPABASE_DIRECT_DSN)}")
print(f"  DATA_TABLE: {settings.DATA_TABLE or '(not set)'}")

if not settings.DATA_DB_TYPE:
    print("\n[ERROR] DATA_DB_TYPE is not set!")
    print("Please add to your .env file:")
    print("  DATA_DB_TYPE=postgres")
    print("  DATA_TABLE=your_table_name")
    exit(1)

# Initialize MCP
print("\nInitializing MCP...")
initialize_mcp_sync()
print("[OK] MCP initialized")

try:
    # Test simple query
    print("\nTesting simple query: SELECT 1 as test...")
    result = call_mcp_tool_sync("db", "db.query_supabase", {
        "query": "SELECT 1 as test, NOW() as timestamp",
        "limit": 5
    })
    
    if result.get("status") == "success":
        print("[OK] Simple query successful!")
        print(f"  Result: {result.get('rows')}")
    else:
        print(f"[ERROR] Query failed: {result.get('error')}")
        exit(1)
    
    # Test table query if configured
    if settings.DATA_TABLE:
        print(f"\nTesting table query: SELECT * FROM {settings.DATA_TABLE} LIMIT 5...")
        result = call_mcp_tool_sync("db", "db.query_supabase", {
            "query": f"SELECT * FROM {settings.DATA_TABLE} LIMIT 5",
            "limit": 5
        })
        
        if result.get("status") == "success":
            rows = result.get("rows", [])
            print(f"[OK] Table query successful! Got {len(rows)} row(s)")
            if rows:
                print(f"  First row columns: {list(rows[0].keys())}")
                print(f"  Sample data: {rows[0]}")
        else:
            print(f"[ERROR] Table query failed: {result.get('error')}")
    else:
        print("\n[INFO] DATA_TABLE not configured, skipping table test")
    
    print("\n" + "=" * 60)
    print("[SUCCESS] Supabase MCP integration is working!")
    print("=" * 60)

except Exception as e:
    print(f"\n[ERROR] {e}")
    import traceback
    traceback.print_exc()
    exit(1)

finally:
    cleanup_mcp_sync()
    print("\nMCP cleanup complete")

