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

    def call_model(state: AgentState):
        messages = state["messages"]
        if not messages or not isinstance(messages[0], SystemMessage):
            messages = [SystemMessage(content=SYSTEM_PROMPT)] + messages
        response = model.invoke(messages)
        return {"messages": [response]}

    graph = StateGraph(AgentState)
    graph.add_node("agent", call_model)
    graph.add_node("tools", tool_node)
    graph.add_edge(START, "agent")
    graph.add_conditional_edges("agent", should_continue)
    graph.add_edge("tools", "agent")

    return graph.compile()
