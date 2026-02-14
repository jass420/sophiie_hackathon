"""
Playwright MCP Client - connects to Microsoft's Playwright MCP server
and provides browser automation tools to the LangGraph agent.
"""

import asyncio
from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain_core.tools import BaseTool


# Singleton client instance
_client: MultiServerMCPClient | None = None
_tools: list[BaseTool] | None = None

# Start simple - just navigate
ALLOWED_TOOLS = {
    "browser_navigate",
    "browser_snapshot",
}


def _create_client() -> MultiServerMCPClient:
    return MultiServerMCPClient({
        "playwright": {
            "command": "npx",
            "args": [
                "@playwright/mcp@latest",
                "--headless",
                "--no-sandbox",
            ],
            "transport": "stdio",
        }
    })


async def get_playwright_tools() -> list[BaseTool]:
    """Get Playwright browser tools from the MCP server.

    Returns a filtered list of LangChain-compatible tools for browser automation.
    """
    global _client, _tools

    if _tools is not None:
        return _tools

    _client = _create_client()
    all_tools = await _client.get_tools()

    # Filter to only the tools we need
    _tools = [t for t in all_tools if t.name in ALLOWED_TOOLS]
    return _tools


async def cleanup():
    """Clean up the MCP client connection."""
    global _client, _tools
    _tools = None
    _client = None
