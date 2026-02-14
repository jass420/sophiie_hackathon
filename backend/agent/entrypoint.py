"""Entrypoint for langgraph dev server."""

from backend.agent.graph import create_agent


async def make_graph():
    """Async factory function for langgraph dev."""
    return await create_agent()
