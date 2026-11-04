from fastapi import APIRouter
from app.database import get_db

router = APIRouter(prefix="/culprit", tags=["culprit"])


@router.get("")
def find_culprits():
    """
    Returns ingredients that appear in more than one reacted product,
    ordered by how many reacted products contain them.
    """
    db = get_db()

    # get IDs of products where had_reaction = true
    reacted = (
        db.table("products")
        .select("id")
        .eq("had_reaction", True)
        .execute()
    )
    reacted_ids = [r["id"] for r in reacted.data]

    if not reacted_ids:
        return []

    # get ingredient counts across those products
    result = (
        db.table("product_ingredients")
        .select("ingredient_id, ingredients(name, is_flagged)")
        .in_("product_id", reacted_ids)
        .execute()
    )

    counts: dict[str, dict] = {}
    for row in result.data:
        iid = row["ingredient_id"]
        if iid not in counts:
            counts[iid] = {
                "ingredient_id": iid,
                "name": row["ingredients"]["name"],
                "is_flagged": row["ingredients"]["is_flagged"],
                "reacted_product_count": 0,
            }
        counts[iid]["reacted_product_count"] += 1

    suspects = [v for v in counts.values() if v["reacted_product_count"] > 1]
    return sorted(suspects, key=lambda x: x["reacted_product_count"], reverse=True)


@router.get("/check")
def check_product_ingredients(product_id: str):
    """
    Given a product ID, returns any of its ingredients that are flagged.
    Used to warn the user before they add / start using a product.
    """
    db = get_db()
    result = (
        db.table("product_ingredients")
        .select("ingredients(id, name, is_flagged)")
        .eq("product_id", product_id)
        .execute()
    )
    flagged = [
        row["ingredients"]
        for row in result.data
        if row["ingredients"]["is_flagged"]
    ]
    return {"flagged_ingredients": flagged}
