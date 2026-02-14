"""Entrypoint for langgraph dev server — exposes orchestrator + both worker graphs."""

import os
from dotenv import load_dotenv
from pathlib import Path
from langchain_openai import ChatOpenAI
from backend.agent.graph import create_agent
from backend.agent.worker import build_worker_a, build_worker_b
from backend.browser.mcp_client import get_playwright_tools

load_dotenv(Path(__file__).resolve().parent.parent.parent / ".env")


async def make_graph():
    """Async factory — returns the orchestrator graph (main entry point)."""
    return await create_agent()


async def _get_worker_deps():
    browser_tools = await get_playwright_tools()
    worker_model = ChatOpenAI(
        model="gpt-5",
        api_key=os.getenv("OPENAI_APIKEY"),
    ).bind_tools(browser_tools)
    return browser_tools, worker_model


async def make_worker_a():
    """Async factory — Worker A graph for Studio visibility."""
    browser_tools, worker_model = await _get_worker_deps()
    return build_worker_a(browser_tools, worker_model)


async def make_worker_b():
    """Async factory — Worker B graph for Studio visibility."""
    browser_tools, worker_model = await _get_worker_deps()
    return build_worker_b(browser_tools, worker_model)
