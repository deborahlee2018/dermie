from __future__ import annotations

import anthropic
from app.config import settings
from app.database import get_db

client = anthropic.Anthropic(api_key=settings.claude_api_key)


def _build_system_prompt() -> str:
    db = get_db()

    profile = db.table("profile").select("*").eq("id", 1).maybe_single().execute()
    products = db.table("products").select("name, brand, rating, status, had_reaction").execute()
    flagged = db.table("ingredients").select("name").eq("is_flagged", True).execute()

    profile_data = profile.data or {}
    skin_type = profile_data.get("skin_type", "unknown")
    concerns = ", ".join(profile_data.get("concerns") or []) or "none listed"
    flagged_ings = ", ".join(i["name"] for i in (flagged.data or [])) or "none"
    stash_summary = "\n".join(
        f"- {p['name']} by {p['brand']} (status: {p['status']}, rating: {p.get('rating', 'unrated')})"
        for p in (products.data or [])
    )

    return f"""You are Dermé, a knowledgeable skincare assistant. You give personalised, practical advice.

User skin profile:
- Skin type: {skin_type}
- Concerns: {concerns}
- Known irritants: {flagged_ings}

Current stash:
{stash_summary or "No products logged yet."}

Guidelines:
- Reference the user's profile and stash when relevant
- Flag any known irritants if recommending or discussing products
- Be concise but thorough
- When recommending products, offer to add them to the wishlist"""


def chat_with_context(message: str, history: list[dict]) -> str:
    system = _build_system_prompt()

    messages = history + [{"role": "user", "content": message}]

    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=1024,
        system=system,
        messages=messages,
    )
    return response.content[0].text
