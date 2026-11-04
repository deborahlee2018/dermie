from pydantic import BaseModel
from enum import Enum
from typing import Optional


class ReactionType(str, Enum):
    redness = "redness"
    breakout = "breakout"
    itching = "itching"
    burning = "burning"
    stinging = "stinging"
    peeling = "peeling"
    dryness = "dryness"
    purging = "purging"


class Severity(str, Enum):
    mild = "mild"
    moderate = "moderate"
    severe = "severe"


class ReactionCreate(BaseModel):
    ingredient_id: str
    reaction_type: ReactionType
    severity: Severity
    source_product_id: Optional[str] = None
    notes: Optional[str] = None


class ReactionResponse(ReactionCreate):
    id: str
