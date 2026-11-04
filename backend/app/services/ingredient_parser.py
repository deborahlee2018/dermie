from __future__ import annotations

import re


def parse_ingredients(raw_text: str) -> list[str]:
    """
    Parse a raw ingredient list string into a normalised array.
    Handles comma-separated lists from sources like incidecoder/skinsort.
    """
    ingredients = []
    for item in raw_text.split(","):
        # strip whitespace, asterisks, bullets, and percentage annotations e.g. (10%)
        clean = re.sub(r"\([^)]*%[^)]*\)", "", item)  # remove (10%) style notes
        clean = re.sub(r"[*•·†‡]", "", clean)          # remove symbol prefixes
        clean = clean.strip().lower()
        if clean:
            ingredients.append(clean)
    return ingredients
