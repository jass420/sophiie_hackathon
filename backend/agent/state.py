from typing import Annotated, TypedDict
from langgraph.graph.message import add_messages
from langchain_core.messages import BaseMessage


class ProductListing(TypedDict):
    id: str
    title: str
    price: float
    currency: str
    image_url: str
    source: str  # "ebay", "facebook", "gumtree"
    url: str
    seller: str
    condition: str
    location: str


class ProposalItem(TypedDict, total=False):
    id: str
    title: str
    price: float
    source: str
    url: str
    image_url: str
    seller: str
    draft_message: str  # optional draft message to seller


class Proposal(TypedDict, total=False):
    type: str  # "shortlist" or "contact_sellers"
    items: list[ProposalItem]
    summary: str


class SearchTask(TypedDict):
    id: str
    item_type: str           # "sofa", "coffee table", "rug"
    style_keywords: list[str]  # ["mid-century", "walnut"]
    max_budget: float
    marketplace: str          # "ebay", "facebook", "gumtree"
    constraints: str          # "must fit 2.5m wall"


class WorkerResult(TypedDict):
    task_id: str
    item_type: str
    picks: list[ProposalItem]  # top 3 picks
    reasoning: str


class AgentState(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]
    room_analysis: dict | None
    shopping_list: list[ProductListing]
    search_results: list[ProductListing]
    pending_proposal: Proposal | None
    approved_items: list[str]  # list of approved item IDs
    search_tasks: list[SearchTask]
    current_task_index: int
    worker_results: list[WorkerResult]
    _tasks_a: list[SearchTask]  # tasks assigned to Worker A
    _tasks_b: list[SearchTask]  # tasks assigned to Worker B
