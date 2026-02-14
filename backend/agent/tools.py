import json
from langchain_core.tools import tool


@tool
def propose_shortlist(items_json: str) -> str:
    """Propose a shortlist of items for the user to approve or reject.
    Call this BEFORE adding items to the shopping list or contacting sellers.
    The user will see the proposal and can approve, reject, or select specific items.

    Args:
        items_json: JSON string of an array of items. Each item must have:
            - id: unique identifier
            - title: item name
            - price: item price (number)
            - source: marketplace name
            - url: link to listing
            - image_url: product image URL (optional)
            - seller: seller name (optional)
            - draft_message: draft message to seller (optional, include if proposing to contact)

    Returns:
        Confirmation that the proposal was submitted for user review
    """
    try:
        items = json.loads(items_json)
        has_messages = any(item.get("draft_message") for item in items)
        proposal_type = "contact_sellers" if has_messages else "shortlist"

        return json.dumps({
            "status": "pending_approval",
            "type": proposal_type,
            "item_count": len(items),
            "items": items,
            "message": f"Proposed {len(items)} items for user approval. Waiting for user to approve/reject.",
        })
    except json.JSONDecodeError:
        return json.dumps({
            "status": "error",
            "message": "Invalid JSON in items_json. Please provide a valid JSON array.",
        })


@tool
def add_to_shopping_list(
    product_id: str,
    title: str,
    price: float,
    source: str,
    url: str,
    image_url: str = "",
) -> str:
    """Add a furniture item to the user's shopping list.
    Only call this AFTER the user has approved the item via propose_shortlist.

    Args:
        product_id: Unique identifier for the product
        title: Product title/name
        price: Product price
        source: Marketplace source (ebay, facebook, gumtree)
        url: Link to the product listing
        image_url: URL of the product image

    Returns:
        Confirmation message
    """
    return json.dumps({
        "status": "added",
        "product_id": product_id,
        "title": title,
        "price": price,
        "source": source,
        "message": f"Added '{title}' (${price}) to your shopping list!",
    })


@tool
def contact_seller(
    product_url: str,
    message: str,
    seller_name: str = "Seller",
) -> str:
    """Send a message to a marketplace seller.
    Only call this AFTER the user has approved via propose_shortlist with draft_message.

    Args:
        product_url: URL of the product listing
        message: Message to send to the seller
        seller_name: Name of the seller

    Returns:
        Status of the message
    """
    return json.dumps({
        "status": "message_sent",
        "to": seller_name,
        "message": message,
        "note": "Message sent to seller.",
    })


@tool
def dispatch_searches(tasks_json: str) -> str:
    """Create search tasks for item worker agents. Each task searches ONE marketplace for ONE item type.
    Call this when you have analyzed the room and know what furniture to search for.

    Args:
        tasks_json: JSON string of an array of search tasks. Each task must have:
            - id: unique task identifier (e.g., "task_1")
            - item_type: what to search for (e.g., "sofa", "coffee table", "rug")
            - style_keywords: list of style terms (e.g., ["mid-century", "walnut", "minimalist"])
            - max_budget: maximum price in AUD
            - marketplace: which site to search ("ebay", "facebook", "gumtree")
            - constraints: any size/location/condition constraints (e.g., "must fit 2m wall, pickup Brisbane")

    Returns:
        Confirmation that workers have been dispatched
    """
    try:
        tasks = json.loads(tasks_json)
        return json.dumps({
            "status": "dispatched",
            "task_count": len(tasks),
            "tasks": tasks,
            "message": f"Dispatched {len(tasks)} search tasks to item workers. Results will be merged when all complete.",
        })
    except json.JSONDecodeError:
        return json.dumps({
            "status": "error",
            "message": "Invalid JSON in tasks_json. Please provide a valid JSON array.",
        })


# Tools for the orchestrator (no browser tools)
ORCHESTRATOR_TOOLS = [propose_shortlist, add_to_shopping_list, contact_seller, dispatch_searches]

# Legacy alias
ALL_TOOLS = ORCHESTRATOR_TOOLS
