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


class AgentState(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]
    room_analysis: dict | None
    shopping_list: list[ProductListing]
    search_results: list[ProductListing]
    pending_proposal: Proposal | None
    approved_items: list[str]  # list of approved item IDs
