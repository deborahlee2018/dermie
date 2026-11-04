from __future__ import annotations

from fastapi import APIRouter, HTTPException
from app.models.product import ProductCreate, ProductUpdate, ProductResponse, FetchFromURL, ProductFromURL
from app.services.scraper import scrape_incidecoder
from app.services.ingredient_parser import parse_ingredients
from app.database import get_db

router = APIRouter(prefix="/products", tags=["products"])


@router.get("", response_model=list[ProductResponse])
def list_products():
    db = get_db()
    result = db.table("products").select("*").order("created_at", desc=True).execute()
    return result.data


@router.get("/{product_id}", response_model=ProductResponse)
def get_product(product_id: str):
    db = get_db()
    result = db.table("products").select("*").eq("id", product_id).single().execute()
    if not result.data:
        raise HTTPException(status_code=404, detail="Product not found")
    return result.data


@router.post("/fetch-url")
def fetch_from_url(body: FetchFromURL):
    """Preview scraped data from an incidecoder URL without saving."""
    return scrape_incidecoder(str(body.url))


@router.post("/from-url", response_model=ProductResponse, status_code=201)
def create_product_from_url(body: ProductFromURL):
    """Scrape an incidecoder URL and save the product in one step."""
    db = get_db()
    scraped = scrape_incidecoder(str(body.url))

    product_data = {
        "name": scraped["product_name"],
        "brand": scraped["brand"],
        "ingredients_text": scraped["ingredients_text"],
        # merge any extra fields the user provided (category, notes, etc.)
        **body.model_dump(exclude={"url"}, exclude_none=True, mode="json"),
    }
    result = db.table("products").insert(product_data).execute()
    product = result.data[0]

    if scraped["ingredients_text"]:
        _store_ingredients(db, product["id"], scraped["ingredients_text"])

    return product


@router.post("", response_model=ProductResponse, status_code=201)
def create_product(body: ProductCreate):
    db = get_db()
    product_data = body.model_dump(exclude_none=True, mode="json")
    result = db.table("products").insert(product_data).execute()
    product = result.data[0]

    if body.ingredients_text:
        _store_ingredients(db, product["id"], body.ingredients_text)

    return product


@router.patch("/{product_id}", response_model=ProductResponse)
def update_product(product_id: str, body: ProductUpdate):
    db = get_db()
    updates = body.model_dump(exclude_none=True, mode="json")

    if "ingredients_text" in updates:
        db.table("product_ingredients").delete().eq("product_id", product_id).execute()
        _store_ingredients(db, product_id, updates["ingredients_text"])

    result = db.table("products").update(updates).eq("id", product_id).execute()
    return result.data[0]


@router.delete("/{product_id}", status_code=204)
def delete_product(product_id: str):
    db = get_db()
    db.table("products").delete().eq("id", product_id).execute()


def _store_ingredients(db, product_id: str, ingredients_text: str):
    """Parse ingredient text and upsert into ingredients + product_ingredients tables."""
    names = parse_ingredients(ingredients_text)
    for rank, name in enumerate(names, start=1):
        # upsert ingredient
        ing_result = (
            db.table("ingredients")
            .upsert({"name": name}, on_conflict="name")
            .execute()
        )
        ingredient_id = ing_result.data[0]["id"]

        # link to product
        db.table("product_ingredients").upsert(
            {"product_id": product_id, "ingredient_id": ingredient_id, "rank": rank},
            on_conflict="product_id,ingredient_id",
        ).execute()
