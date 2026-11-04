from __future__ import annotations

from fastapi import APIRouter
from app.models.wishlist import WishlistCreate, WishlistResponse
from app.database import get_db

router = APIRouter(prefix="/wishlist", tags=["wishlist"])


@router.get("", response_model=list[WishlistResponse])
def list_wishlist():
    db = get_db()
    result = db.table("wishlist").select("*").order("created_at", desc=True).execute()
    return result.data


@router.post("", response_model=WishlistResponse, status_code=201)
def add_to_wishlist(body: WishlistCreate):
    db = get_db()
    result = db.table("wishlist").insert(body.model_dump(exclude_none=True)).execute()
    return result.data[0]


@router.delete("/{item_id}", status_code=204)
def remove_from_wishlist(item_id: str):
    db = get_db()
    db.table("wishlist").delete().eq("id", item_id).execute()
