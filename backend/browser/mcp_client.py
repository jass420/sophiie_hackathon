"""
Playwright MCP Client - connects to TWO long-lived Playwright MCP HTTP servers
for true parallel browser automation (one per worker).

Start both servers first:
  npx @playwright/mcp@latest --port 3001 --no-sandbox --shared-browser-context --viewport-size 1920x1080
  npx @playwright/mcp@latest --port 3002 --no-sandbox --shared-browser-context --viewport-size 1920x1080
"""

from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain_core.tools import BaseTool


# Singleton client instances — one per worker
_client_a: MultiServerMCPClient | None = None
_client_b: MultiServerMCPClient | None = None
_tools_a: list[BaseTool] | None = None
_tools_b: list[BaseTool] | None = None

PLAYWRIGHT_MCP_URL_A = "http://localhost:3001/sse"
PLAYWRIGHT_MCP_URL_B = "http://localhost:3002/sse"

ALLOWED_TOOLS = {
    "browser_navigate",
    "browser_snapshot",
    "browser_click",
    "browser_type",
    "browser_press_key",
    "browser_fill_form",
    "browser_wait_for",
    "browser_take_screenshot",
    "browser_tab_new",
    "browser_tab_select",
    "browser_tab_list",
    "browser_tab_close",
    "browser_scroll_down",
    "browser_scroll_up",
}

# Keep a separate ref to the screenshot tool for the API endpoint
_screenshot_tool: BaseTool | None = None


def _create_client(url: str) -> MultiServerMCPClient:
    return MultiServerMCPClient({
        "playwright": {
            "url": url,
            "transport": "sse",
        }
    })


async def _get_tools_for(url: str) -> tuple[MultiServerMCPClient, list[BaseTool]]:
    """Connect to an MCP server and return (client, filtered_tools)."""
    client = _create_client(url)
    all_tools = await client.get_tools()
    tools = [t for t in all_tools if t.name in ALLOWED_TOOLS]
    return client, tools


async def get_playwright_tools_a() -> list[BaseTool]:
    """Get browser tools from MCP server A (port 3001) — for Worker A."""
    global _client_a, _tools_a, _screenshot_tool

    if _tools_a is not None:
        return _tools_a

    _client_a, _tools_a = await _get_tools_for(PLAYWRIGHT_MCP_URL_A)

    # Use server A for screenshots
    for t in _tools_a:
        if t.name == "browser_take_screenshot":
            _screenshot_tool = t
            break

    return _tools_a


async def get_playwright_tools_b() -> list[BaseTool]:
    """Get browser tools from MCP server B (port 3002) — for Worker B."""
    global _client_b, _tools_b

    if _tools_b is not None:
        return _tools_b

    _client_b, _tools_b = await _get_tools_for(PLAYWRIGHT_MCP_URL_B)
    return _tools_b


# Legacy alias — returns server A tools (used by orchestrator for compatibility)
async def get_playwright_tools() -> list[BaseTool]:
    return await get_playwright_tools_a()


async def take_screenshot() -> str | None:
    """Take a screenshot via the MCP tool. Returns base64 image data or None."""
    global _screenshot_tool
    if _screenshot_tool is None:
        return None
    try:
        result = await _screenshot_tool.ainvoke({})
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
    """Clean up the MCP client connections."""
    global _client_a, _client_b, _tools_a, _tools_b, _screenshot_tool
    _tools_a = None
    _tools_b = None
    _screenshot_tool = None
    _client_a = None
    _client_b = None
