import asyncio
import json
import uuid
import random
from backend.search.types import ProductListing


# Realistic furniture database for demo purposes
# In production, these would come from real marketplace APIs
FURNITURE_DB = {
    "sofa": [
        {"title": "Modern L-Shaped Sofa - Grey Fabric", "price": 450, "condition": "Used - Like New", "location": "Brisbane, QLD", "source": "facebook"},
        {"title": "3 Seater Leather Couch - Brown", "price": 280, "condition": "Used - Good", "location": "Gold Coast, QLD", "source": "gumtree"},
        {"title": "IKEA KIVIK Sofa - Charcoal", "price": 350, "condition": "Used - Like New", "location": "Brisbane CBD", "source": "facebook"},
        {"title": "Velvet 2-Seater Sofa - Navy Blue", "price": 200, "condition": "Used - Good", "location": "Sunshine Coast", "source": "ebay"},
        {"title": "Corner Sofa with Chaise - Beige Linen", "price": 600, "condition": "Used - Like New", "location": "Logan, QLD", "source": "gumtree"},
        {"title": "Mid-Century Modern Sofa - Mustard", "price": 520, "condition": "Used - Good", "location": "Paddington, QLD", "source": "facebook"},
        {"title": "Modular Couch 4 Pieces - Light Grey", "price": 380, "condition": "Used - Fair", "location": "Ipswich, QLD", "source": "ebay"},
        {"title": "Scandinavian Style Sofa - Cream", "price": 420, "condition": "New", "location": "Brisbane, QLD", "source": "ebay"},
    ],
    "coffee table": [
        {"title": "Solid Timber Coffee Table - Acacia Wood", "price": 120, "condition": "Used - Good", "location": "Brisbane, QLD", "source": "gumtree"},
        {"title": "Round Marble Coffee Table - White/Gold", "price": 180, "condition": "Used - Like New", "location": "New Farm, QLD", "source": "facebook"},
        {"title": "Industrial Style Coffee Table - Metal & Wood", "price": 95, "condition": "Used - Good", "location": "Woolloongabba, QLD", "source": "facebook"},
        {"title": "IKEA LACK Coffee Table - Black", "price": 25, "condition": "Used - Good", "location": "St Lucia, QLD", "source": "gumtree"},
        {"title": "Mid-Century Walnut Coffee Table", "price": 250, "condition": "Used - Like New", "location": "West End, QLD", "source": "ebay"},
        {"title": "Glass Top Coffee Table - Chrome Legs", "price": 75, "condition": "Used - Fair", "location": "Toowong, QLD", "source": "gumtree"},
        {"title": "Rattan Coffee Table - Natural", "price": 160, "condition": "New", "location": "Brisbane, QLD", "source": "ebay"},
    ],
    "dining table": [
        {"title": "6-Seater Dining Table - Solid Oak", "price": 350, "condition": "Used - Good", "location": "Brisbane, QLD", "source": "gumtree"},
        {"title": "Extendable Dining Table - White Gloss", "price": 280, "condition": "Used - Like New", "location": "Carindale, QLD", "source": "facebook"},
        {"title": "Round Dining Table 4 Seater - Timber", "price": 200, "condition": "Used - Good", "location": "Indooroopilly, QLD", "source": "facebook"},
        {"title": "IKEA BJURSTA Dining Table + 4 Chairs", "price": 180, "condition": "Used - Good", "location": "Chermside, QLD", "source": "gumtree"},
        {"title": "Live Edge Dining Table - Mango Wood", "price": 800, "condition": "New", "location": "Brisbane, QLD", "source": "ebay"},
        {"title": "Farmhouse Style Dining Table - Seats 8", "price": 450, "condition": "Used - Good", "location": "Springfield, QLD", "source": "facebook"},
    ],
    "bookshelf": [
        {"title": "IKEA KALLAX Shelf Unit 4x4 - White", "price": 80, "condition": "Used - Good", "location": "Brisbane, QLD", "source": "gumtree"},
        {"title": "Tall Timber Bookcase - 5 Shelves", "price": 120, "condition": "Used - Good", "location": "Milton, QLD", "source": "facebook"},
        {"title": "Industrial Pipe Bookshelf - Metal/Wood", "price": 200, "condition": "New", "location": "Brisbane, QLD", "source": "ebay"},
        {"title": "Corner Bookshelf - Bamboo", "price": 65, "condition": "Used - Like New", "location": "Taringa, QLD", "source": "gumtree"},
        {"title": "Floating Wall Shelves Set of 3", "price": 45, "condition": "New", "location": "Brisbane, QLD", "source": "ebay"},
    ],
    "bed": [
        {"title": "Queen Bed Frame - Timber & Upholstered", "price": 350, "condition": "Used - Like New", "location": "Brisbane, QLD", "source": "facebook"},
        {"title": "King Bed Frame - Black Metal", "price": 200, "condition": "Used - Good", "location": "Capalaba, QLD", "source": "gumtree"},
        {"title": "Queen Platform Bed - Walnut Finish", "price": 280, "condition": "Used - Good", "location": "Fortitude Valley", "source": "facebook"},
        {"title": "IKEA MALM Queen Bed + Mattress", "price": 300, "condition": "Used - Good", "location": "Kelvin Grove, QLD", "source": "gumtree"},
        {"title": "Upholstered Queen Bed - Grey Velvet", "price": 450, "condition": "New", "location": "Brisbane, QLD", "source": "ebay"},
        {"title": "Rustic Timber Queen Bed Frame", "price": 380, "condition": "Used - Like New", "location": "Toowoomba, QLD", "source": "ebay"},
    ],
    "desk": [
        {"title": "Standing Desk - Electric Adjustable", "price": 250, "condition": "Used - Like New", "location": "Brisbane CBD", "source": "facebook"},
        {"title": "L-Shaped Corner Desk - White", "price": 120, "condition": "Used - Good", "location": "South Brisbane", "source": "gumtree"},
        {"title": "Solid Timber Writing Desk", "price": 180, "condition": "Used - Good", "location": "Paddington, QLD", "source": "facebook"},
        {"title": "IKEA BEKANT Desk - 160x80cm", "price": 100, "condition": "Used - Good", "location": "St Lucia, QLD", "source": "gumtree"},
        {"title": "Mid-Century Desk - Walnut Veneer", "price": 220, "condition": "Used - Like New", "location": "Brisbane, QLD", "source": "ebay"},
    ],
    "chair": [
        {"title": "Ergonomic Office Chair - Mesh Back", "price": 150, "condition": "Used - Good", "location": "Brisbane CBD", "source": "facebook"},
        {"title": "Set of 4 Dining Chairs - Timber", "price": 120, "condition": "Used - Good", "location": "Annerley, QLD", "source": "gumtree"},
        {"title": "Accent Armchair - Green Velvet", "price": 200, "condition": "Used - Like New", "location": "New Farm, QLD", "source": "facebook"},
        {"title": "Rattan Lounge Chair - Natural", "price": 180, "condition": "New", "location": "Brisbane, QLD", "source": "ebay"},
        {"title": "Eames Style Dining Chairs x2", "price": 90, "condition": "Used - Good", "location": "West End, QLD", "source": "gumtree"},
    ],
    "rug": [
        {"title": "Large Area Rug 200x300cm - Cream/Grey", "price": 120, "condition": "Used - Like New", "location": "Brisbane, QLD", "source": "facebook"},
        {"title": "Persian Style Rug - Red/Navy", "price": 180, "condition": "Used - Good", "location": "Toowong, QLD", "source": "gumtree"},
        {"title": "Jute Rug Round 150cm - Natural", "price": 60, "condition": "New", "location": "Brisbane, QLD", "source": "ebay"},
        {"title": "Shag Rug - White 160x230cm", "price": 90, "condition": "Used - Good", "location": "Chermside, QLD", "source": "gumtree"},
    ],
    "lamp": [
        {"title": "Floor Lamp - Arc Style Gold/White", "price": 80, "condition": "Used - Like New", "location": "Brisbane, QLD", "source": "facebook"},
        {"title": "Table Lamp Set of 2 - Ceramic Base", "price": 45, "condition": "Used - Good", "location": "Indooroopilly", "source": "gumtree"},
        {"title": "Pendant Light - Rattan Shade", "price": 65, "condition": "New", "location": "Brisbane, QLD", "source": "ebay"},
        {"title": "Tripod Floor Lamp - Timber/Linen", "price": 95, "condition": "Used - Like New", "location": "New Farm, QLD", "source": "facebook"},
    ],
}

# Generic fallback listings
GENERIC_LISTINGS = [
    {"price": 150, "condition": "Used - Good", "location": "Brisbane, QLD", "source": "facebook"},
    {"price": 80, "condition": "Used - Fair", "location": "Gold Coast, QLD", "source": "gumtree"},
    {"price": 220, "condition": "Used - Like New", "location": "Sunshine Coast", "source": "ebay"},
    {"price": 300, "condition": "New", "location": "Brisbane CBD", "source": "facebook"},
    {"price": 120, "condition": "Used - Good", "location": "Logan, QLD", "source": "gumtree"},
    {"price": 95, "condition": "Used - Good", "location": "Ipswich, QLD", "source": "ebay"},
]


def find_matching_category(query: str) -> str | None:
    """Find the best matching furniture category for a query."""
    query_lower = query.lower()
    for category in FURNITURE_DB:
        if category in query_lower:
            return category
    # Check partial matches
    category_aliases = {
        "sofa": ["couch", "lounge", "settee"],
        "coffee table": ["side table", "accent table"],
        "dining table": ["kitchen table", "table and chairs"],
        "bookshelf": ["shelving", "shelf", "bookcase", "shelves"],
        "bed": ["bed frame", "bedframe", "mattress"],
        "desk": ["work desk", "study desk", "office desk", "computer desk"],
        "chair": ["seat", "armchair", "stool", "dining chair"],
        "rug": ["carpet", "mat", "floor covering"],
        "lamp": ["light", "lighting", "floor lamp", "table lamp"],
    }
    for category, aliases in category_aliases.items():
        for alias in aliases:
            if alias in query_lower:
                return category
    return None


async def search_marketplace(query: str, marketplace: str = "all", max_price: float | None = None) -> list[ProductListing]:
    """Search for furniture across marketplaces.

    Uses a curated database of realistic Australian marketplace listings.
    In production, this would integrate with real marketplace APIs and
    browser automation for sites without APIs.
    """
    category = find_matching_category(query)

    if category and category in FURNITURE_DB:
        listings = FURNITURE_DB[category].copy()
    else:
        # Generate generic listings based on query
        listings = []
        for base in GENERIC_LISTINGS:
            listings.append({
                **base,
                "title": f"{query.title()} - {base['condition']}",
            })

    # Filter by marketplace
    if marketplace != "all":
        listings = [l for l in listings if l["source"] == marketplace]

    # Filter by max price
    if max_price:
        listings = [l for l in listings if l["price"] <= max_price]

    # Shuffle for variety
    random.shuffle(listings)

    # Convert to ProductListing objects
    products = []
    for listing in listings:
        source = listing["source"]
        url_map = {
            "ebay": "https://www.ebay.com.au",
            "facebook": "https://www.facebook.com/marketplace",
            "gumtree": "https://www.gumtree.com.au",
        }
        products.append(ProductListing(
            id=str(uuid.uuid4()),
            title=listing["title"],
            price=float(listing["price"]),
            currency="AUD",
            image_url="",
            source=source,
            url=url_map.get(source, ""),
            seller=f"{source.title()} Seller",
            condition=listing.get("condition", "Used"),
            location=listing.get("location", "Brisbane, QLD"),
        ))

    return products


async def search_all_marketplaces(query: str, max_price: float | None = None) -> list[ProductListing]:
    """Search all marketplaces."""
    return await search_marketplace(query, "all", max_price)
