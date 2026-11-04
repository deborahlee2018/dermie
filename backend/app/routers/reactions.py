from __future__ import annotations

from fastapi import APIRouter
from app.models.reaction import ReactionCreate, ReactionResponse
from app.database import get_db

router = APIRouter(prefix="/reactions", tags=["reactions"])


@router.get("", response_model=list[ReactionResponse])
def list_reactions():
    db = get_db()
    result = db.table("reactions").select("*").order("created_at", desc=True).execute()
    return result.data


@router.post("", response_model=ReactionResponse, status_code=201)
def create_reaction(body: ReactionCreate):
    db = get_db()
    result = db.table("reactions").insert(body.model_dump(exclude_none=True)).execute()
    reaction = result.data[0]

    # auto-flag the ingredient
    db.table("ingredients").update({"is_flagged": True}).eq(
        "id", body.ingredient_id
    ).execute()

    return reaction


@router.delete("/{reaction_id}", status_code=204)
def delete_reaction(reaction_id: str):
    db = get_db()
    db.table("reactions").delete().eq("id", reaction_id).execute()
