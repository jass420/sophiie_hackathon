import json
from langchain_core.tools import tool
from backend.search.scraper import search_marketplace as _search_marketplace


@tool
async def search_marketplace(
    query: str,
    marketplace: str = "all",
    max_price: float | None = None,
) -> str:
    """Search for furniture on online marketplaces like eBay, Facebook Marketplace, and Gumtree.

    Args:
        query: Search query for furniture (e.g. "mid-century coffee table", "blue sofa")
        marketplace: Which marketplace to search: "facebook", "ebay", "gumtree", or "all"
        max_price: Maximum price in dollars (optional)

    Returns:
        JSON string of product listings found on the marketplaces
    """
    try:
        products = await _search_marketplace(query, marketplace, max_price)

        return json.dumps({
            "status": "success",
            "query": query,
            "count": len(products),
            "products": [p.model_dump() for p in products],
        })
    except Exception as e:
        return json.dumps({
            "status": "error",
            "query": query,
            "error": str(e),
            "products": [],
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
    """Draft and send a message to a marketplace seller.

    Args:
        product_url: URL of the product listing
        message: Message to send to the seller
        seller_name: Name of the seller

    Returns:
        Status of the message
    """
    return json.dumps({
        "status": "message_drafted",
        "to": seller_name,
        "message": message,
        "note": "Message ready to send. Awaiting user approval.",
    })


ALL_TOOLS = [search_marketplace, add_to_shopping_list, contact_seller]
