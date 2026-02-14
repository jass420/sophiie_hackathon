"""Item Worker Agents — two workers that each open their own browser tab to search."""

import json
import re
from typing import Annotated, TypedDict

from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode
from langchain_core.messages import BaseMessage, SystemMessage, AIMessage

from backend.agent.state import SearchTask
from backend.agent.prompts import WORKER_PROMPT


class WorkerState(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]
    tasks: list[SearchTask]  # multiple tasks for this worker


def _build_worker(worker_name: str, browser_tools, worker_model):
    """Build a compiled worker subgraph. Each worker opens its own tab."""

    worker_tool_node = ToolNode(browser_tools, handle_tool_errors=True)

    def worker_agent(state: WorkerState):
        tasks = state["tasks"]
        # Build task descriptions for all assigned items
        task_lines = []
        for i, task in enumerate(tasks, 1):
            task_lines.append(
                f"### Task {i}: {task['item_type']}\n"
                f"- **Style**: {', '.join(task['style_keywords'])}\n"
                f"- **Max Budget**: ${task['max_budget']:.0f} AUD\n"
                f"- **Marketplace**: {task['marketplace']}\n"
                f"- **Constraints**: {task['constraints']}"
            )

        task_block = f"""
## You are: {worker_name}
## Your Assigned Tasks ({len(tasks)} items to find)

{"".join(task_lines)}

IMPORTANT: First, open a NEW browser tab with `browser_tab_new` so you have your own workspace.
Then search each marketplace for each item. Find the top 3 listings per item.
"""
        messages = state["messages"]
        if not messages or not isinstance(messages[0], SystemMessage):
            messages = [SystemMessage(content=WORKER_PROMPT + task_block)] + messages

        response = worker_model.invoke(messages)
        return {"messages": [response]}

    def should_continue(state: WorkerState):
        last = state["messages"][-1]
        if hasattr(last, "tool_calls") and last.tool_calls:
            return "worker_tools"
        return END

    graph = StateGraph(WorkerState)
    graph.add_node("worker_agent", worker_agent)
    graph.add_node("worker_tools", worker_tool_node)
    graph.add_edge(START, "worker_agent")
    graph.add_conditional_edges(
        "worker_agent",
        should_continue,
        {"worker_tools": "worker_tools", END: END},
    )
    graph.add_edge("worker_tools", "worker_agent")

    return graph.compile()


def build_worker_a(browser_tools, worker_model):
    """Build Worker A subgraph."""
    return _build_worker("Worker A", browser_tools, worker_model)


def build_worker_b(browser_tools, worker_model):
    """Build Worker B subgraph."""
    return _build_worker("Worker B", browser_tools, worker_model)


def parse_worker_results(messages: list[BaseMessage]) -> list[dict]:
    """Extract structured picks from the worker's final message."""
    for msg in reversed(messages):
        if isinstance(msg, AIMessage) and msg.content:
            content = msg.content
            # Look for [WORKER_RESULTS]...[/WORKER_RESULTS] block
            match = re.search(
                r"\[WORKER_RESULTS\]\s*(.*?)\s*\[/WORKER_RESULTS\]",
                content,
                re.DOTALL,
            )
            if match:
                try:
                    data = json.loads(match.group(1))
                    return data.get("picks", [])
                except json.JSONDecodeError:
                    pass
            # Fallback: try to find any JSON object with "picks" key
            try:
                json_match = re.search(r'\{[^{}]*"picks"\s*:\s*\[.*?\]\s*[^{}]*\}', content, re.DOTALL)
                if json_match:
                    data = json.loads(json_match.group(0))
                    return data.get("picks", [])
            except (json.JSONDecodeError, AttributeError):
                pass
    return []
