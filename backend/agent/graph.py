import os
from dotenv import load_dotenv
from pathlib import Path
from langgraph.graph import StateGraph, START, END
from langgraph.prebuilt import ToolNode
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage
from backend.agent.state import AgentState
from backend.agent.prompts import SYSTEM_PROMPT
from backend.agent.tools import ALL_TOOLS
from backend.browser.mcp_client import get_playwright_tools

# Load env
load_dotenv(Path(__file__).resolve().parent.parent.parent / ".env")


async def create_agent():
    # Get Playwright browser tools from MCP server
    browser_tools = await get_playwright_tools()

    # Combine custom tools with Playwright MCP tools
    all_tools = ALL_TOOLS + browser_tools

    model = ChatOpenAI(
        model="gpt-4o",
        max_tokens=4096,
        api_key=os.getenv("OPENAI_APIKEY"),
    ).bind_tools(all_tools)

    tool_node = ToolNode(all_tools, handle_tool_errors=True)

    def should_continue(state: AgentState):
        last_message = state["messages"][-1]
        if last_message.tool_calls:
            return "tools"
        return END

    # Build system prompt with credentials injected
    fb_email = os.getenv("FB_EMAIL", "")
    fb_password = os.getenv("FB_PASSWORD", "")
    credentials_block = ""
    if fb_email and fb_password:
        credentials_block = f"""

## Facebook Credentials (from env)
- Email: {fb_email}
- Password: {fb_password}

## IMPORTANT: How to use browser tools correctly
- After EVERY browser action (navigate, click, type), take a fresh browser_snapshot BEFORE your next action.
- Element refs (like e5, e12) change after every page update. NEVER reuse refs from a previous snapshot.
- Only call ONE browser action tool at a time, then snapshot again.

## Facebook Login Steps (follow exactly):
1. browser_navigate to https://www.facebook.com/login
2. browser_snapshot to see the page
3. Find the email input field ref in the snapshot (look for textbox with "Email" or "email")
4. browser_type with that ref and the email: {fb_email}
5. browser_snapshot again (refs change after typing!)
6. Find the password input field ref (look for textbox with "Password" or "password")
7. browser_type with that ref and the password: {fb_password}
8. browser_snapshot again
9. Find the "Log In" button ref
10. browser_click on the Log In button
11. browser_snapshot to confirm login succeeded
"""
    full_system_prompt = SYSTEM_PROMPT + credentials_block

    def call_model(state: AgentState):
        messages = state["messages"]
        if not messages or not isinstance(messages[0], SystemMessage):
            messages = [SystemMessage(content=full_system_prompt)] + messages
        response = model.invoke(messages)
        return {"messages": [response]}

    graph = StateGraph(AgentState)
    graph.add_node("agent", call_model)
    graph.add_node("tools", tool_node)
    graph.add_edge(START, "agent")
    graph.add_conditional_edges("agent", should_continue)
    graph.add_edge("tools", "agent")

    return graph.compile()
