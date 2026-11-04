from fastapi import APIRouter
from app.models.profile import ProfileUpdate, ProfileResponse
from app.database import get_db

router = APIRouter(prefix="/profile", tags=["profile"])


@router.get("", response_model=ProfileResponse)
def get_profile():
    db = get_db()
    result = db.table("profile").select("*").eq("id", 1).single().execute()
    return result.data


@router.put("", response_model=ProfileResponse)
def upsert_profile(body: ProfileUpdate):
    db = get_db()
    result = (
        db.table("profile")
        .upsert({"id": 1, **body.model_dump(exclude_none=True)})
        .execute()
    )
    return result.data[0]
