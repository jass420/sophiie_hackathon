"""
Playwright MCP Client - connects to a long-lived Playwright MCP HTTP server
and provides browser automation tools to the LangGraph agent.

Start the server first:
  DISPLAY=:1 npx @playwright/mcp@latest --port 3001 --no-sandbox --shared-browser-context
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
    "browser_take_screenshot",
}

# Keep a separate ref to the screenshot tool for the API endpoint
_screenshot_tool: BaseTool | None = None


def _create_client() -> MultiServerMCPClient:
    return MultiServerMCPClient({
        "playwright": {
            "url": PLAYWRIGHT_MCP_URL,
            "transport": "sse",
        }
    })


async def get_playwright_tools() -> list[BaseTool]:
    """Get Playwright browser tools from the MCP server."""
    global _client, _tools, _screenshot_tool

    if _tools is not None:
        return _tools

    _client = _create_client()
    all_tools = await _client.get_tools()

    _tools = [t for t in all_tools if t.name in ALLOWED_TOOLS]

    for t in _tools:
        if t.name == "browser_take_screenshot":
            _screenshot_tool = t
            break

    return _tools


async def take_screenshot() -> str | None:
    """Take a screenshot via the MCP tool. Returns base64 image data or None."""
    global _screenshot_tool
    if _screenshot_tool is None:
        return None
    try:
        result = await _screenshot_tool.ainvoke({})
        # Result is a list of content blocks from LangChain MCP adapter
        # Find the image block and extract base64
        if isinstance(result, list):
            for block in result:
                if isinstance(block, dict) and block.get("type") == "image":
                    return block.get("base64")
        elif isinstance(result, str):
            return result
        return None
    except Exception:
        return None


async def cleanup():
    """Clean up the MCP client connection."""
    global _client, _tools, _screenshot_tool
    _tools = None
    _screenshot_tool = None
    _client = None
