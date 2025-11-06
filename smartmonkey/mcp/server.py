#!/usr/bin/env python3
"""
SmartMonkey MCP Server

Model Context Protocol server for SmartMonkey Android app testing tool.

Usage:
    python -m smartmonkey.mcp.server

Or configure in Claude Desktop config:
    ~/Library/Application Support/Claude/claude_desktop_config.json
"""

import asyncio
import sys
from pathlib import Path

# Ensure smartmonkey is in path
smartmonkey_root = Path(__file__).parent.parent.parent
if str(smartmonkey_root) not in sys.path:
    sys.path.insert(0, str(smartmonkey_root))

from mcp.server import Server
from mcp.server.stdio import stdio_server
from .tools import TOOLS
from .handlers import handle_tool_call


# Create MCP server
app = Server("smartmonkey")


@app.list_tools()
async def list_tools() -> list[dict]:
    """Return available tools"""
    return TOOLS


@app.call_tool()
async def call_tool(name: str, arguments: dict) -> list[dict]:
    """Execute a tool and return results"""
    result = await handle_tool_call(name, arguments)

    # Wrap result in MCP format
    return [{
        "type": "text",
        "text": str(result)
    }]


async def main():
    """Run the MCP server"""
    async with stdio_server() as (read_stream, write_stream):
        await app.run(
            read_stream,
            write_stream,
            app.create_initialization_options()
        )


if __name__ == "__main__":
    asyncio.run(main())
