from fastapi import APIRouter
from app.database import get_db

router = APIRouter(prefix="/ingredients", tags=["ingredients"])


@router.get("")
def list_ingredients(flagged_only: bool = False):
    db = get_db()
    query = db.table("ingredients").select("*")
    if flagged_only:
        query = query.eq("is_flagged", True)
    result = query.order("name").execute()
    return result.data


@router.patch("/{ingredient_id}/flag")
def toggle_flag(ingredient_id: str, flagged: bool):
    db = get_db()
    result = (
        db.table("ingredients")
        .update({"is_flagged": flagged})
        .eq("id", ingredient_id)
        .execute()
    )
    return result.data[0]
