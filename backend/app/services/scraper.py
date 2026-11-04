import requests
from bs4 import BeautifulSoup
from fastapi import HTTPException

HEADERS = {"User-Agent": "Mozilla/5.0 (compatible; Derme/1.0; personal-use)"}


def scrape_incidecoder(url: str) -> dict:
    if "incidecoder.com" not in url:
        raise HTTPException(status_code=400, detail="Only incidecoder.com URLs are supported")

    try:
        response = requests.get(url, headers=HEADERS, timeout=10)
        response.raise_for_status()
    except requests.RequestException as e:
        raise HTTPException(status_code=502, detail=f"Failed to fetch URL: {e}")

    soup = BeautifulSoup(response.text, "html.parser")

    product_name = soup.find("h1").get_text(strip=True) if soup.find("h1") else None

    brand_tag = soup.find("a", href=lambda h: h and "/brands/" in h)
    brand = brand_tag.get_text(strip=True) if brand_tag else None

    ingredient_tags = soup.find_all("a", href=lambda h: h and "/ingredients/" in h)
    ingredients_text = ", ".join(tag.get_text(strip=True) for tag in ingredient_tags)

    return {
        "product_name": product_name,
        "brand": brand,
        "ingredients_text": ingredients_text,
    }
