from pydantic import BaseModel, HttpUrl, field_validator
from enum import Enum
from typing import Optional
from datetime import date


class ProductCategory(str, Enum):
    cleanser = "cleanser"
    toner = "toner"
    serum = "serum"
    moisturiser = "moisturiser"
    spf = "spf"
    eye_cream = "eye_cream"
    exfoliant = "exfoliant"
    mask = "mask"
    treatment = "treatment"
    mist = "mist"
    oil = "oil"
    lip = "lip"
    body = "body"
    other = "other"


class ProductStatus(str, Enum):
    active = "active"
    finished = "finished"
    paused = "paused"
    destashed = "destashed"
    sample = "sample"


class ProductCreate(BaseModel):
    name: str
    brand: Optional[str] = None
    category: Optional[ProductCategory] = None
    rating: Optional[int] = None
    status: ProductStatus = ProductStatus.active
    ingredients_text: Optional[str] = None  # raw paste, parsed server-side
    notes: Optional[str] = None
    purchase_date: Optional[date] = None
    opened_date: Optional[date] = None

    @field_validator("rating")
    @classmethod
    def rating_range(cls, v):
        if v is not None and not (1 <= v <= 5):
            raise ValueError("Rating must be between 1 and 5")
        return v


class ProductUpdate(ProductCreate):
    name: Optional[str] = None
    status: Optional[ProductStatus] = None
    had_reaction: Optional[bool] = None


class FetchFromURL(BaseModel):
    url: HttpUrl


class ProductFromURL(BaseModel):
    """Scrape + save in one step. Only URL is required — everything else is optional."""
    url: HttpUrl
    category: Optional[ProductCategory] = None
    status: ProductStatus = ProductStatus.active
    notes: Optional[str] = None
    purchase_date: Optional[date] = None
    opened_date: Optional[date] = None


class ProductResponse(BaseModel):
    id: str
    name: str
    brand: Optional[str]
    category: Optional[ProductCategory]
    rating: Optional[int]
    status: ProductStatus
    had_reaction: bool
    ingredients_text: Optional[str]
    notes: Optional[str]
    purchase_date: Optional[date]
    opened_date: Optional[date]
