"""Orchestrator Agent Graph — dispatches tasks to Worker A and Worker B in parallel."""

import asyncio
import json
import os
from dotenv import load_dotenv
from pathlib import Path
from langgraph.graph import StateGraph, START, END
from langgraph.prebuilt import ToolNode
from langgraph.types import interrupt
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage, ToolMessage
from backend.agent.state import AgentState, WorkerResult
from backend.agent.prompts import ORCHESTRATOR_PROMPT
from backend.agent.tools import ORCHESTRATOR_TOOLS
from backend.agent.worker import build_worker_a, build_worker_b, parse_worker_results
from backend.browser.mcp_client import get_playwright_tools_a, get_playwright_tools_b

load_dotenv(Path(__file__).resolve().parent.parent.parent / ".env")


async def create_agent():
    # Each worker gets its own Playwright MCP server for true parallel browsing
    browser_tools_a = await get_playwright_tools_a()  # port 3001
    browser_tools_b = await get_playwright_tools_b()  # port 3002

    orchestrator_model = ChatOpenAI(
        model="gpt-5",
        api_key=os.getenv("OPENAI_APIKEY"),
    ).bind_tools(ORCHESTRATOR_TOOLS)

    worker_model_a = ChatOpenAI(
        model="gpt-5",
        api_key=os.getenv("OPENAI_APIKEY"),
    ).bind_tools(browser_tools_a)

    worker_model_b = ChatOpenAI(
        model="gpt-5",
        api_key=os.getenv("OPENAI_APIKEY"),
    ).bind_tools(browser_tools_b)

    worker_a_subgraph = build_worker_a(browser_tools_a, worker_model_a)
    worker_b_subgraph = build_worker_b(browser_tools_b, worker_model_b)
    orchestrator_tool_node = ToolNode(ORCHESTRATOR_TOOLS, handle_tool_errors=True)

    # ---- System prompt with optional FB credentials ----
    fb_email = os.getenv("FB_EMAIL", "")
    fb_password = os.getenv("FB_PASSWORD", "")
    credentials_block = ""
    if fb_email and fb_password:
        credentials_block = f"""

## Facebook Credentials (from env)
- Email: {fb_email}
- Password: {fb_password}

Workers will handle Facebook login if needed using these credentials.
"""
    full_prompt = ORCHESTRATOR_PROMPT + credentials_block

    # ---- Nodes ----

    def orchestrator(state: AgentState):
        messages = state["messages"]
        if not messages or not isinstance(messages[0], SystemMessage):
            messages = [SystemMessage(content=full_prompt)] + messages
        response = orchestrator_model.invoke(messages)
        return {"messages": [response]}

    def process_dispatch(state: AgentState):
        """Split tasks between Worker A and Worker B."""
        tasks = []
        for msg in reversed(state["messages"]):
            if isinstance(msg, ToolMessage):
                try:
                    result = json.loads(msg.content)
                    if result.get("status") == "dispatched":
                        tasks = result.get("tasks", [])
                except (json.JSONDecodeError, TypeError):
                    pass
                break

        # Split by item type: group tasks by item_type, then assign
        # each item type group to a different worker.
        # e.g. Worker A searches for "bed" on all marketplaces,
        #      Worker B searches for "sidetable" on all marketplaces.
        from collections import OrderedDict
        groups = OrderedDict()
        for t in tasks:
            groups.setdefault(t["item_type"], []).append(t)

        item_types = list(groups.keys())
        mid = (len(item_types) + 1) // 2
        tasks_a = [t for it in item_types[:mid] for t in groups[it]]
        tasks_b = [t for it in item_types[mid:] for t in groups[it]]

        return {
            "search_tasks": tasks,  # keep full list for reference
            "current_task_index": 0,
            "worker_results": [],
            # Store splits in the tasks themselves via tagging
            "_tasks_a": tasks_a,
            "_tasks_b": tasks_b,
        }

    async def _run_single_worker(subgraph, tasks, worker_name):
        """Run one worker subgraph and parse its results."""
        if not tasks:
            return []

        # Build a detailed, unique message for this specific worker
        task_details = []
        for i, t in enumerate(tasks, 1):
            task_details.append(
                f"{i}. {t['item_type']} on {t['marketplace']} "
                f"(style: {', '.join(t.get('style_keywords', []))}, "
                f"budget: ${t.get('max_budget', 'N/A')} AUD, "
                f"constraints: {t.get('constraints', 'none')})"
            )
        task_list_str = "\n".join(task_details)

        # Include FB credentials if available so workers can log in if needed
        creds_info = ""
        if fb_email and fb_password:
            creds_info = (
                f"\n\nFacebook Login Credentials (use ONLY if you see a login page):\n"
                f"- Email: {fb_email}\n"
                f"- Password: {fb_password}\n"
            )

        try:
            worker_state = await asyncio.wait_for(
                subgraph.ainvoke(
                    {
                        "messages": [HumanMessage(content=(
                            f"You are {worker_name}. Search for ONLY these specific items:\n"
                            f"{task_list_str}\n\n"
                            f"Navigate DIRECTLY to the search URL for each item. Do NOT go to the marketplace homepage. Go fast."
                            f"{creds_info}"
                        ))],
                        "tasks": tasks,
                        "step_count": 0,
                    },
                    config={"recursion_limit": 100},
                ),
                timeout=180,  # 3 minute timeout per worker
            )
        except asyncio.TimeoutError:
            # Worker took too long — return empty results
            results = []
            for task in tasks:
                results.append(WorkerResult(
                    task_id=task["id"],
                    item_type=task["item_type"],
                    picks=[],
                    reasoning=f"{worker_name} timed out searching for {task['item_type']} on {task['marketplace']}",
                ))
            return results

        picks = parse_worker_results(worker_state["messages"])
        results = []
        for task in tasks:
            task_picks = [p for p in picks if p.get("source", "") == task["marketplace"]]
            if not task_picks:
                task_picks = picks  # fallback: assign all picks
            results.append(WorkerResult(
                task_id=task["id"],
                item_type=task["item_type"],
                picks=task_picks[:3],
                reasoning=f"{worker_name} found {len(task_picks)} picks for {task['item_type']} on {task['marketplace']}",
            ))
        return results

    async def run_workers(state: AgentState):
        """Run Worker A and Worker B in parallel using asyncio.gather."""
        tasks_a = state.get("_tasks_a", [])
        tasks_b = state.get("_tasks_b", [])

        # Launch both workers concurrently — each opens its own browser tab
        results_a, results_b = await asyncio.gather(
            _run_single_worker(worker_a_subgraph, tasks_a, "Worker A"),
            _run_single_worker(worker_b_subgraph, tasks_b, "Worker B"),
        )

        all_results = results_a + results_b
        return {"worker_results": all_results}

    def merge_results(state: AgentState):
        """Combine all worker results into a summary for the orchestrator."""
        results = state.get("worker_results", [])
        if not results:
            summary = "No worker results were found. The searches may have failed."
        else:
            lines = ["## Search Results from Workers\n"]
            for wr in results:
                lines.append(f"### {wr['item_type']} ({wr['reasoning']})")
                for i, pick in enumerate(wr.get("picks", []), 1):
                    lines.append(
                        f"  {i}. **{pick.get('title', 'Unknown')}** — ${pick.get('price', 'N/A')} on {pick.get('source', '?')}\n"
                        f"     Condition: {pick.get('condition', '')} | Location: {pick.get('location', '')}\n"
                        f"     Reason: {pick.get('reason', '')}\n"
                        f"     URL: {pick.get('url', '')}"
                    )
                lines.append("")
            summary = "\n".join(lines)
            summary += "\nReview these results and present your curated picks to the user. Then call `propose_shortlist` with your top recommendations."

        return {
            "messages": [HumanMessage(content=summary)],
            "search_tasks": [],
            "current_task_index": 0,
        }

    def human_approval(state: AgentState):
        """Interrupt the graph and wait for user approval."""
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

        user_decision = interrupt({
            "type": proposal_data.get("type", "shortlist"),
            "items": proposal_data.get("items", []),
            "item_count": proposal_data.get("item_count", 0),
            "message": "Please review the proposed items.",
        })

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

    # ---- Routing ----

    def route_orchestrator(state: AgentState):
        last = state["messages"][-1]
        if hasattr(last, "tool_calls") and last.tool_calls:
            return "orchestrator_tools"
        return END

    def route_after_orchestrator_tools(state: AgentState) -> str:
        for msg in reversed(state["messages"]):
            if isinstance(msg, ToolMessage):
                try:
                    result = json.loads(msg.content)
                    if result.get("status") == "pending_approval":
                        return "human_approval"
                    if result.get("status") == "dispatched":
                        return "process_dispatch"
                except (json.JSONDecodeError, TypeError):
                    pass
                break
        return "orchestrator"

    # ---- Build graph ----
    #
    # Flow:
    #   START → orchestrator → route
    #     ├→ END
    #     └→ orchestrator_tools → route_after_tools
    #          ├→ human_approval → orchestrator
    #          ├→ process_dispatch → run_workers (A+B parallel) → merge_results → orchestrator
    #          └→ orchestrator (loop)

    graph = StateGraph(AgentState)

    graph.add_node("orchestrator", orchestrator)
    graph.add_node("orchestrator_tools", orchestrator_tool_node)
    graph.add_node("process_dispatch", process_dispatch)
    graph.add_node("run_workers", run_workers)
    graph.add_node("merge_results", merge_results)
    graph.add_node("human_approval", human_approval)

    graph.add_edge(START, "orchestrator")
    graph.add_conditional_edges(
        "orchestrator",
        route_orchestrator,
        {"orchestrator_tools": "orchestrator_tools", END: END},
    )
    graph.add_conditional_edges(
        "orchestrator_tools",
        route_after_orchestrator_tools,
        {"human_approval": "human_approval", "process_dispatch": "process_dispatch", "orchestrator": "orchestrator"},
    )
    graph.add_edge("process_dispatch", "run_workers")
    graph.add_edge("run_workers", "merge_results")
    graph.add_edge("merge_results", "orchestrator")
    graph.add_edge("human_approval", "orchestrator")

    return graph.compile()
