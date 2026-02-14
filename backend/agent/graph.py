import json
import os
from dotenv import load_dotenv
from pathlib import Path
from langgraph.graph import StateGraph, START, END
from langgraph.prebuilt import ToolNode
from langgraph.types import interrupt, Command
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage, ToolMessage
from backend.agent.state import AgentState
from backend.agent.prompts import SYSTEM_PROMPT
from backend.agent.tools import ALL_TOOLS
from backend.browser.mcp_client import get_playwright_tools

# Load env
load_dotenv(Path(__file__).resolve().parent.parent.parent / ".env")

# Tool name that triggers the approval interrupt
PROPOSAL_TOOL = "propose_shortlist"


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

    def route_after_tools(state: AgentState) -> str:
        """Check if the last tool call was a proposal that needs approval."""
        messages = state["messages"]
        # Walk backwards to find the most recent tool call and its result
        for msg in reversed(messages):
            if isinstance(msg, ToolMessage):
                try:
                    result = json.loads(msg.content)
                    if result.get("status") == "pending_approval":
                        return "human_approval"
                except (json.JSONDecodeError, TypeError):
                    pass
                break
        return "agent"

    def human_approval(state: AgentState):
        """Interrupt the graph and wait for user to approve/reject the proposal."""
        # Find the proposal from the last tool message
        proposal_data = None
        for msg in reversed(state["messages"]):
            if isinstance(msg, ToolMessage):
                try:
                    result = json.loads(msg.content)
                    if result.get("status") == "pending_approval":
                        proposal_data = result
                except (json.JSONDecodeError, TypeError):
                    pass
                break

        if not proposal_data:
            return {"pending_proposal": None, "approved_items": []}

        # This pauses the graph and sends the proposal to the user
        # The user's response comes back as the return value of interrupt()
        user_decision = interrupt({
            "type": proposal_data.get("type", "shortlist"),
            "items": proposal_data.get("items", []),
            "item_count": proposal_data.get("item_count", 0),
            "message": "Please review the proposed items. You can approve all, reject all, or select specific items.",
        })

        # user_decision is whatever the user sends back when resuming:
        # e.g. {"action": "approve_all"} or {"action": "approve_selected", "selected_ids": ["id1","id2"]}
        #      or {"action": "reject"}
        action = user_decision.get("action", "reject") if isinstance(user_decision, dict) else str(user_decision)

        if action == "approve_all":
            approved_ids = [item["id"] for item in proposal_data.get("items", [])]
            approval_msg = "User approved all proposed items."
        elif action == "approve_selected":
            approved_ids = user_decision.get("selected_ids", [])
            selected_titles = [
                item["title"]
                for item in proposal_data.get("items", [])
                if item["id"] in approved_ids
            ]
            approval_msg = f"User approved these items: {', '.join(selected_titles)}"
        else:
            approved_ids = []
            approval_msg = "User rejected the proposal."

        return {
            "messages": [HumanMessage(content=approval_msg)],
            "pending_proposal": None,
            "approved_items": approved_ids,
        }

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
    graph.add_node("human_approval", human_approval)
    graph.add_edge(START, "agent")
    graph.add_conditional_edges("agent", should_continue, {"tools": "tools", END: END})
    graph.add_conditional_edges("tools", route_after_tools, {"human_approval": "human_approval", "agent": "agent"})
    graph.add_edge("human_approval", "agent")

    return graph.compile()
