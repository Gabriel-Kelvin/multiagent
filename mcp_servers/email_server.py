#!/usr/bin/env python3
"""
MCP Server for Email Sending via SendGrid
Provides: email.send_report - send emails with optional attachments (CSV, PDF, etc.)
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

from utils import sendgrid_utils
from app.config import settings


app = Server("email-server")


@app.list_tools()
async def list_tools() -> list[Tool]:
    """List available email tools."""
    return [
        Tool(
            name="email.send_report",
            description=(
                "Send an email with optional file attachments using SendGrid. "
                "Supports CSV, PDF, and other file types. "
                "Requires SendGrid API key and email addresses to be configured."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "subject": {
                        "type": "string",
                        "description": "Email subject line",
                    },
                    "body_text": {
                        "type": "string",
                        "description": "Plain text email body",
                    },
                    "to_emails": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "List of recipient email addresses",
                    },
                    "from_email": {
                        "type": "string",
                        "description": "Sender email address",
                    },
                    "attachments": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "file_path": {"type": "string", "description": "Path to the file to attach"},
                                "mime_type": {"type": "string", "description": "MIME type (e.g., text/csv, application/pdf)"},
                                "file_name": {"type": "string", "description": "Display name for the attachment"},
                            },
                            "required": ["file_path"],
                        },
                        "description": "Optional list of file attachments",
                    },
                    "api_key": {
                        "type": "string",
                        "description": "SendGrid API key (optional, uses environment if not provided)",
                    },
                },
                "required": ["subject", "body_text", "to_emails", "from_email"],
            },
        ),
    ]


@app.call_tool()
async def call_tool(name: str, arguments: Any) -> Sequence[TextContent]:
    """Handle tool execution."""
    if name != "email.send_report":
        raise ValueError(f"Unknown tool: {name}")

    subject = arguments.get("subject", "")
    body_text = arguments.get("body_text", "")
    to_emails = arguments.get("to_emails", [])
    from_email = arguments.get("from_email", "")
    attachments = arguments.get("attachments", [])
    api_key = arguments.get("api_key") or getattr(settings, "SENDGRID_API_KEY", "")

    # Validation
    if not subject or not body_text:
        return [
            TextContent(
                type="text",
                text=json.dumps({
                    "status": "error",
                    "error": "Subject and body_text are required"
                }),
            )
        ]

    if not to_emails or not isinstance(to_emails, list):
        return [
            TextContent(
                type="text",
                text=json.dumps({
                    "status": "error",
                    "error": "to_emails must be a non-empty list"
                }),
            )
        ]

    if not from_email:
        return [
            TextContent(
                type="text",
                text=json.dumps({
                    "status": "error",
                    "error": "from_email is required"
                }),
            )
        ]

    if not api_key:
        return [
            TextContent(
                type="text",
                text=json.dumps({
                    "status": "error",
                    "error": "SendGrid API key is required (provide via api_key parameter or SENDGRID_API_KEY environment variable)"
                }),
            )
        ]

    # Validate attachments exist
    validated_attachments = []
    for att in attachments:
        file_path = att.get("file_path")
        if not file_path:
            continue
        if not os.path.exists(file_path):
            return [
                TextContent(
                    type="text",
                    text=json.dumps({
                        "status": "error",
                        "error": f"Attachment file not found: {file_path}"
                    }),
                )
            ]
        validated_attachments.append(att)

    try:
        # Send email using the existing sendgrid_utils
        result = sendgrid_utils.send_email(
            subject=subject,
            body_text=body_text,
            to_emails=to_emails,
            from_email=from_email,
            attachments=validated_attachments,
            api_key=api_key,
        )

        return [
            TextContent(
                type="text",
                text=json.dumps(result),
            )
        ]

    except Exception as e:
        return [
            TextContent(
                type="text",
                text=json.dumps({
                    "status": "error",
                    "error": str(e),
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

