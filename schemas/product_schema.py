from pydantic import BaseModel
from typing import Optional


class ProductSchema(BaseModel):
    product_id: int
    name: str
    category: str
    brand: str
    price: float

    description: Optional[str] = None
    specifications: Optional[str] = None
    features: Optional[str] = None

    rating: Optional[float] = None
    stock_count: Optional[int] = None
