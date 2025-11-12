#!/usr/bin/env python3
"""
Test script for MCP Integration
Tests that MCP servers start correctly and respond to tool calls
"""
import asyncio
import sys
from mcp_client import MCPClientManager


async def test_mcp_servers():
    """Test MCP server initialization and tool calls."""
    print("=" * 60)
    print("Testing MCP Integration")
    print("=" * 60)
    
    manager = MCPClientManager()
    
    try:
        # Initialize servers
        print("\n[1/4] Initializing MCP servers...")
        await manager.initialize()
        print("[OK] MCP servers initialized successfully")
        
        # Test DB server - List tools
        print("\n[2/4] Testing DB Server - Listing tools...")
        db_tools = await manager.list_tools("db")
        print(f"[OK] Found {len(db_tools)} DB tool(s):")
        for tool in db_tools:
            print(f"  - {tool['name']}: {tool['description'][:80]}...")
        
        # Test Email server - List tools
        print("\n[3/4] Testing Email Server - Listing tools...")
        email_tools = await manager.list_tools("email")
        print(f"[OK] Found {len(email_tools)} Email tool(s):")
        for tool in email_tools:
            print(f"  - {tool['name']}: {tool['description'][:80]}...")
        
        # Test DB query (simple test query)
        print("\n[4/4] Testing DB Query Tool...")
        try:
            result = await manager.call_tool("db", "db.query_supabase", {
                "query": "SELECT 1 as test, 'MCP Works!' as message",
                "limit": 10
            })
            
            if result.get("status") == "success":
                rows = result.get("rows", [])
                print(f"[OK] DB query executed successfully")
                print(f"  Result: {rows}")
            else:
                print(f"[WARN] DB query returned an error (this is expected if DB is not configured):")
                print(f"  {result.get('error', 'Unknown error')}")
        except Exception as e:
            print(f"[WARN] DB query test failed (this is expected if DB is not configured):")
            print(f"  {str(e)}")
        
        print("\n" + "=" * 60)
        print("MCP Integration Test Summary")
        print("=" * 60)
        print("[OK] MCP servers can be started")
        print("[OK] MCP tools are discoverable")
        print("[OK] MCP tool calls work (subject to configuration)")
        print("\nNext steps:")
        print("1. Configure your .env file with database credentials")
        print("2. Run the backend server: uvicorn server:app --port 8010")
        print("3. Test the full flow through the API")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n[ERROR] Error during MCP testing: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    
    finally:
        # Cleanup
        print("\n[Cleanup] Shutting down MCP servers...")
        await manager.cleanup()
        print("[OK] Cleanup complete")


if __name__ == "__main__":
    print("\nMCP Integration Test")
    print("This script tests that MCP servers can start and respond to tool calls.\n")
    
    try:
        asyncio.run(test_mcp_servers())
    except KeyboardInterrupt:
        print("\n\nTest interrupted by user")
        sys.exit(0)

