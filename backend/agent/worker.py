"""Item Worker Agents — two workers that each open their own browser tab to search."""

import json
import re
from typing import Annotated, TypedDict

from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode
from langchain_core.messages import BaseMessage, SystemMessage, AIMessage, HumanMessage, ToolMessage

from backend.agent.state import SearchTask, MessagingTask
from backend.agent.prompts import WORKER_PROMPT, MESSAGING_WORKER_PROMPT


MAX_WORKER_STEPS = 30  # max tool-call rounds before forcing wrap-up


class WorkerState(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]
    tasks: list[SearchTask]  # multiple tasks for this worker
    step_count: int  # tracks how many tool rounds have executed


def _build_worker(worker_name: str, browser_tools, worker_model):
    """Build a compiled worker subgraph. Each worker opens its own tab."""

    worker_tool_node = ToolNode(browser_tools, handle_tool_errors=True)

    def _trim_messages(messages, keep_last_n=4):
        """Keep system prompt, first human message, and only the last N tool interactions.
        This prevents browser snapshots from accumulating and blowing up token usage.
        """
        if len(messages) <= keep_last_n + 2:
            return messages

        # Always keep: system prompt (index 0) + first human message (index 1)
        prefix = []
        rest_start = 0
        for i, msg in enumerate(messages):
            if isinstance(msg, (SystemMessage, HumanMessage)):
                prefix.append(msg)
                rest_start = i + 1
            else:
                break

        # From the remaining messages, keep only the last N
        # But make sure we don't split an AI message from its ToolMessage response
        tail = messages[rest_start:]
        if len(tail) <= keep_last_n:
            return prefix + tail

        trimmed_tail = tail[-keep_last_n:]
        # If the first message in the tail is a ToolMessage, we need the AI message before it
        if trimmed_tail and isinstance(trimmed_tail[0], ToolMessage):
            # Find the matching AI message
            idx = len(tail) - keep_last_n - 1
            if idx >= 0:
                trimmed_tail = [tail[idx]] + trimmed_tail

        return prefix + trimmed_tail

    def worker_agent(state: WorkerState):
        tasks = state["tasks"]
        step = state.get("step_count", 0)

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

Go FAST. Navigate directly to search URLs. Scan results. Return picks. Aim for 2-3 picks per item.
"""
        # If approaching step limit, inject an urgency message
        urgency = ""
        if step >= MAX_WORKER_STEPS - 5:
            urgency = (
                "\n\n⚠️ YOU ARE RUNNING OUT OF STEPS. "
                "You MUST output your [WORKER_RESULTS] JSON block NOW with whatever picks you have found so far. "
                "Do NOT make any more browser calls. Summarize and return results IMMEDIATELY."
            )

        messages = state["messages"]
        if not messages or not isinstance(messages[0], SystemMessage):
            messages = [SystemMessage(content=WORKER_PROMPT + task_block)] + messages

        if urgency:
            messages = messages + [HumanMessage(content=urgency)]

        # Trim old messages to avoid sending huge browser snapshots every turn
        messages = _trim_messages(messages, keep_last_n=6)

        response = worker_model.invoke(messages)
        return {"messages": [response], "step_count": step + 1}

    def should_continue(state: WorkerState):
        # Force stop if we've hit the step limit
        if state.get("step_count", 0) >= MAX_WORKER_STEPS:
            return END
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


# ---- Messaging Worker ----

MAX_MESSAGING_STEPS = 15


class MessagingWorkerState(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]
    messaging_task: MessagingTask
    step_count: int


def build_messaging_worker(browser_tools, worker_model):
    """Build a messaging worker subgraph that sends messages to sellers via Playwright."""

    tool_node = ToolNode(browser_tools, handle_tool_errors=True)

    def messaging_agent(state: MessagingWorkerState):
        step = state.get("step_count", 0)
        task = state["messaging_task"]

        task_block = f"""
## Your Messaging Task
- **Listing URL**: {task['product_url']}
- **Seller**: {task['seller_name']}
- **Message to send**: {task['message']}

Navigate to the listing URL, find the message button, type the message, and send it.
"""
        urgency = ""
        if step >= MAX_MESSAGING_STEPS - 3:
            urgency = (
                "\n\n⚠️ YOU ARE RUNNING OUT OF STEPS. "
                "Output your [MESSAGING_RESULTS] JSON block NOW. "
                "Report success if you sent the message, or failure if you couldn't."
            )

        messages = state["messages"]
        if not messages or not isinstance(messages[0], SystemMessage):
            messages = [SystemMessage(content=MESSAGING_WORKER_PROMPT + task_block)] + messages

        if urgency:
            messages = messages + [HumanMessage(content=urgency)]

        response = worker_model.invoke(messages)
        return {"messages": [response], "step_count": step + 1}

    def should_continue(state: MessagingWorkerState):
        if state.get("step_count", 0) >= MAX_MESSAGING_STEPS:
            return END
        last = state["messages"][-1]
        if hasattr(last, "tool_calls") and last.tool_calls:
            return "messaging_tools"
        return END

    graph = StateGraph(MessagingWorkerState)
    graph.add_node("messaging_agent", messaging_agent)
    graph.add_node("messaging_tools", tool_node)
    graph.add_edge(START, "messaging_agent")
    graph.add_conditional_edges(
        "messaging_agent",
        should_continue,
        {"messaging_tools": "messaging_tools", END: END},
    )
    graph.add_edge("messaging_tools", "messaging_agent")

    return graph.compile()


def parse_messaging_results(messages: list[BaseMessage]) -> dict:
    """Extract messaging result from the worker's final message."""
    for msg in reversed(messages):
        if isinstance(msg, AIMessage) and msg.content:
            content = msg.content
            match = re.search(
                r"\[MESSAGING_RESULTS\]\s*(.*?)\s*\[/MESSAGING_RESULTS\]",
                content,
                re.DOTALL,
            )
            if match:
                try:
                    return json.loads(match.group(1))
                except json.JSONDecodeError:
                    pass
            # Fallback: look for JSON with "success" key
            try:
                json_match = re.search(r'\{[^{}]*"success"\s*:', content, re.DOTALL)
                if json_match:
                    # Try to parse from this position
                    brace_start = json_match.start()
                    data = json.loads(content[brace_start:content.index("}", brace_start) + 1])
                    return data
            except (json.JSONDecodeError, AttributeError, ValueError):
                pass
    return {"success": False, "reasoning": "No messaging results found in worker output"}
