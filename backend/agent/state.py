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


class AgentState(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]
    room_analysis: dict | None
    shopping_list: list[ProductListing]
    search_results: list[ProductListing]
