"""
MCP Client Manager
Manages connections to internal and external MCP servers
"""
import asyncio
import json
import os
import sys
from typing import Any, Dict, List, Optional
from contextlib import asynccontextmanager

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


class MCPClientManager:
    """Manages multiple MCP client connections."""

    def __init__(self):
        self.sessions: Dict[str, ClientSession] = {}
        self.connections: Dict[str, Any] = {}  # Store connection contexts
        self._initialized = False

    async def initialize(self):
        """Initialize all MCP server connections."""
        if self._initialized:
            return

        try:
            # Start internal MCP servers
            await self._start_db_server()
            await self._start_email_server()

            # Note: External MCP servers (filesystem, fetch) would be configured here
            # if they are running separately. For now, we'll handle filesystem operations
            # directly in the agents since they're simple file operations.

            self._initialized = True
            print("[MCP] All MCP servers initialized successfully")

        except Exception as e:
            print(f"[MCP] Error initializing MCP servers: {e}")
            raise

    async def _start_db_server(self):
        """Start the internal database MCP server."""
        try:
            server_script = os.path.join(os.path.dirname(__file__), "mcp_servers", "db_server.py")
            if not os.path.exists(server_script):
                raise FileNotFoundError(f"DB server script not found: {server_script}")

            server_params = StdioServerParameters(
                command=sys.executable,
                args=[server_script],
                env=None,
            )

            # Create stdio client connection and keep the context manager
            stdio_context = stdio_client(server_params)
            read_stream, write_stream = await stdio_context.__aenter__()

            # Create session
            session = ClientSession(read_stream, write_stream)
            await session.__aenter__()
            
            # Initialize the session
            await session.initialize()

            self.sessions["db"] = session
            self.connections["db"] = stdio_context
            print("[MCP] DB server started successfully")

        except Exception as e:
            print(f"[MCP] Error starting DB server: {e}")
            raise

    async def _start_email_server(self):
        """Start the internal email MCP server."""
        try:
            server_script = os.path.join(os.path.dirname(__file__), "mcp_servers", "email_server.py")
            if not os.path.exists(server_script):
                raise FileNotFoundError(f"Email server script not found: {server_script}")

            server_params = StdioServerParameters(
                command=sys.executable,
                args=[server_script],
                env=None,
            )

            # Create stdio client connection and keep the context manager
            stdio_context = stdio_client(server_params)
            read_stream, write_stream = await stdio_context.__aenter__()

            # Create session
            session = ClientSession(read_stream, write_stream)
            await session.__aenter__()
            
            # Initialize the session
            await session.initialize()

            self.sessions["email"] = session
            self.connections["email"] = stdio_context
            print("[MCP] Email server started successfully")

        except Exception as e:
            print(f"[MCP] Error starting Email server: {e}")
            raise

    async def call_tool(self, server: str, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """
        Call a tool on a specific MCP server.
        
        Args:
            server: Server name ("db", "email", etc.)
            tool_name: Tool name (e.g., "db.query_supabase", "email.send_report")
            arguments: Tool arguments as a dictionary
            
        Returns:
            Parsed response from the tool
        """
        if not self._initialized:
            await self.initialize()

        session = self.sessions.get(server)
        if not session:
            raise ValueError(f"MCP server '{server}' not found or not initialized")

        try:
            result = await session.call_tool(tool_name, arguments)
            
            # Parse the result
            if result and len(result.content) > 0:
                content = result.content[0]
                if hasattr(content, 'text'):
                    return json.loads(content.text)
            
            return {"status": "error", "error": "Empty response from MCP server"}

        except Exception as e:
            return {"status": "error", "error": str(e)}

    async def list_tools(self, server: str) -> List[Dict[str, Any]]:
        """List available tools from a specific server."""
        if not self._initialized:
            await self.initialize()

        session = self.sessions.get(server)
        if not session:
            raise ValueError(f"MCP server '{server}' not found")

        try:
            result = await session.list_tools()
            return [
                {
                    "name": tool.name,
                    "description": tool.description,
                    "inputSchema": tool.inputSchema,
                }
                for tool in result.tools
            ]
        except Exception as e:
            print(f"[MCP] Error listing tools from {server}: {e}")
            return []

    async def cleanup(self):
        """Clean up all MCP connections."""
        for server_name, session in list(self.sessions.items()):
            try:
                await session.__aexit__(None, None, None)
            except Exception as e:
                print(f"[MCP] Error closing session {server_name}: {e}")

        for server_name, connection in list(self.connections.items()):
            try:
                await connection.__aexit__(None, None, None)
            except Exception as e:
                print(f"[MCP] Error closing connection {server_name}: {e}")

        self.sessions.clear()
        self.connections.clear()
        self._initialized = False
        print("[MCP] All MCP connections cleaned up")


# Global singleton instance
_mcp_manager: Optional[MCPClientManager] = None


def get_mcp_manager() -> MCPClientManager:
    """Get or create the global MCP manager instance."""
    global _mcp_manager
    if _mcp_manager is None:
        _mcp_manager = MCPClientManager()
    return _mcp_manager


async def initialize_mcp():
    """Initialize the global MCP manager."""
    manager = get_mcp_manager()
    await manager.initialize()


async def cleanup_mcp():
    """Cleanup the global MCP manager."""
    global _mcp_manager
    if _mcp_manager:
        await _mcp_manager.cleanup()
        _mcp_manager = None


# Synchronous wrappers for use in non-async code
def call_mcp_tool_sync(server: str, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
    """Synchronous wrapper for calling MCP tools."""
    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
    
    if loop.is_running():
        # If we're already in an event loop, create a new thread
        import concurrent.futures
        with concurrent.futures.ThreadPoolExecutor() as executor:
            future = executor.submit(asyncio.run, _async_call_tool(server, tool_name, arguments))
            return future.result()
    else:
        # Run in the current loop
        return loop.run_until_complete(_async_call_tool(server, tool_name, arguments))


async def _async_call_tool(server: str, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
    """Helper for async tool calls."""
    manager = get_mcp_manager()
    return await manager.call_tool(server, tool_name, arguments)


def initialize_mcp_sync():
    """Synchronous wrapper for initializing MCP."""
    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
    
    if not loop.is_running():
        loop.run_until_complete(initialize_mcp())


def cleanup_mcp_sync():
    """Synchronous wrapper for cleaning up MCP."""
    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        return  # No loop, nothing to cleanup
    
    if not loop.is_running():
        loop.run_until_complete(cleanup_mcp())


if __name__ == "__main__":
    # Test the MCP client manager
    async def test():
        manager = MCPClientManager()
        await manager.initialize()
        
        # List tools
        print("\n=== DB Server Tools ===")
        db_tools = await manager.list_tools("db")
        for tool in db_tools:
            print(f"  - {tool['name']}: {tool['description']}")
        
        print("\n=== Email Server Tools ===")
        email_tools = await manager.list_tools("email")
        for tool in email_tools:
            print(f"  - {tool['name']}: {tool['description']}")
        
        # Test query (if configured)
        print("\n=== Testing DB Query ===")
        result = await manager.call_tool("db", "db.query_supabase", {
            "query": "SELECT 1 as test",
            "limit": 10
        })
        print(f"Result: {json.dumps(result, indent=2)}")
        
        await manager.cleanup()
    
    asyncio.run(test())

