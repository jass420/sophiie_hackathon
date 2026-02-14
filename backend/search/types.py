from pydantic import BaseModel


class ProductListing(BaseModel):
    id: str
    title: str
    price: float
    currency: str = "AUD"
    image_url: str = ""
    source: str  # "ebay", "facebook", "gumtree"
    url: str = ""
    seller: str = ""
    condition: str = ""
    location: str = ""
    description: str = ""
