#!/usr/bin/env python3
"""
MCP Server for Supabase/PostgreSQL Database Queries
Provides: db.query_supabase - safe, read-only SQL queries
"""
import asyncio
import json
import os
import sys
from typing import Any, Sequence

# Add parent directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from mcp.server import Server
from mcp.types import Tool, TextContent
from mcp.server.stdio import stdio_server

from utils import db_utils
from app.config import settings


app = Server("db-server")


@app.list_tools()
async def list_tools() -> list[Tool]:
    """List available database tools."""
    return [
        Tool(
            name="db.query_supabase",
            description=(
                "Execute a safe, read-only SQL SELECT query on Supabase (PostgreSQL). "
                "Only SELECT queries are allowed. INSERT, UPDATE, DELETE, DROP, etc. are forbidden. "
                "Queries are automatically limited to 500 rows if no LIMIT clause is present. "
                "Returns a list of rows as dictionaries."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "SQL SELECT query to execute (read-only)",
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Maximum number of rows to return (default: 500)",
                        "default": 500,
                    },
                    "dsn": {
                        "type": "string",
                        "description": "PostgreSQL DSN connection string (optional, uses .env if not provided)",
                    },
                    "db_type": {
                        "type": "string",
                        "description": "Database type (postgres, mysql, sqlite)",
                    },
                    "host": {
                        "type": "string",
                        "description": "Database host",
                    },
                    "port": {
                        "type": "integer",
                        "description": "Database port",
                    },
                    "name": {
                        "type": "string",
                        "description": "Database name",
                    },
                    "user": {
                        "type": "string",
                        "description": "Database user",
                    },
                    "password": {
                        "type": "string",
                        "description": "Database password",
                    },
                    "sslmode": {
                        "type": "string",
                        "description": "SSL mode (require, prefer, disable)",
                    },
                },
                "required": ["query"],
            },
        ),
    ]


@app.call_tool()
async def call_tool(name: str, arguments: Any) -> Sequence[TextContent]:
    """Handle tool execution."""
    if name != "db.query_supabase":
        raise ValueError(f"Unknown tool: {name}")

    query = arguments.get("query", "")
    limit = arguments.get("limit", 500)

    if not query:
        return [
            TextContent(
                type="text",
                text=json.dumps({
                    "status": "error",
                    "error": "Query parameter is required"
                }),
            )
        ]

    try:
        # Check if query is safe (read-only SELECT)
        if not db_utils.is_safe_select(query):
            return [
                TextContent(
                    type="text",
                    text=json.dumps({
                        "status": "error",
                        "error": "Only SELECT queries are allowed. INSERT, UPDATE, DELETE, DROP, etc. are forbidden."
                    }),
                )
            ]

        # Use provided connection parameters or fall back to settings
        # Create a custom settings object if parameters are provided
        if arguments.get("dsn") or arguments.get("host"):
            class CustomSettings:
                pass
            custom_settings = CustomSettings()
            custom_settings.DATA_DB_TYPE = arguments.get("db_type") or settings.DATA_DB_TYPE
            custom_settings.DATA_DSN = arguments.get("dsn") or settings.DATA_DSN
            custom_settings.DATA_HOST = arguments.get("host") or settings.DATA_HOST
            custom_settings.DATA_PORT = str(arguments.get("port") or settings.DATA_PORT)
            custom_settings.DATA_NAME = arguments.get("name") or settings.DATA_NAME
            custom_settings.DATA_USER = arguments.get("user") or settings.DATA_USER
            custom_settings.DATA_PASSWORD = arguments.get("password") or settings.DATA_PASSWORD
            custom_settings.DATA_SSLMODE = arguments.get("sslmode") or settings.DATA_SSLMODE
            connection_settings = custom_settings
        else:
            connection_settings = settings

        # Execute the query
        rows = db_utils.execute_select(connection_settings, query, limit=limit)

        return [
            TextContent(
                type="text",
                text=json.dumps({
                    "status": "success",
                    "rows": rows,
                    "count": len(rows),
                    "query": query,
                }),
            )
        ]

    except Exception as e:
        return [
            TextContent(
                type="text",
                text=json.dumps({
                    "status": "error",
                    "error": str(e),
                    "query": query,
                }),
            )
        ]


async def main():
    """Run the MCP server using stdio transport."""
    async with stdio_server() as (read_stream, write_stream):
        await app.run(
            read_stream,
            write_stream,
            app.create_initialization_options()
        )


if __name__ == "__main__":
    asyncio.run(main())

