from pydantic import BaseModel
from enum import Enum
from typing import Optional
from app.models.product import ProductCategory


class WishlistSource(str, Enum):
    chatbot = "chatbot"
    manual = "manual"


class WishlistCreate(BaseModel):
    name: str
    brand: Optional[str] = None
    category: Optional[ProductCategory] = None
    source: WishlistSource = WishlistSource.manual
    notes: Optional[str] = None


class WishlistResponse(WishlistCreate):
    id: str
