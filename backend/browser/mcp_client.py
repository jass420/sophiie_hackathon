"""
Playwright MCP Client - connects to a long-lived Playwright MCP HTTP server
and provides browser automation tools to the LangGraph agent.

Start the server first:
  DISPLAY=:1 npx @playwright/mcp@latest --port 3001 --no-sandbox
"""

from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain_core.tools import BaseTool


# Singleton client instance
_client: MultiServerMCPClient | None = None
_tools: list[BaseTool] | None = None

PLAYWRIGHT_MCP_URL = "http://localhost:3001/sse"

ALLOWED_TOOLS = {
    "browser_navigate",
    "browser_snapshot",
    "browser_click",
    "browser_type",
    "browser_press_key",
    "browser_fill_form",
    "browser_wait_for",
}


def _create_client() -> MultiServerMCPClient:
    return MultiServerMCPClient({
        "playwright": {
            "url": PLAYWRIGHT_MCP_URL,
            "transport": "sse",
        }
    })


async def get_playwright_tools() -> list[BaseTool]:
    """Get Playwright browser tools from the MCP server."""
    global _client, _tools

    if _tools is not None:
        return _tools

    _client = _create_client()
    all_tools = await _client.get_tools()

    _tools = [t for t in all_tools if t.name in ALLOWED_TOOLS]
    return _tools


async def cleanup():
    """Clean up the MCP client connection."""
    global _client, _tools
    _tools = None
    _client = None
