from __future__ import annotations

from pydantic import BaseModel
from enum import Enum
from typing import Optional


class SkinType(str, Enum):
    normal = "normal"
    dry = "dry"
    oily = "oily"
    combination = "combination"
    sensitive = "sensitive"


class SkinConcern(str, Enum):
    acne = "acne"
    hyperpigmentation = "hyperpigmentation"
    dryness = "dryness"
    sensitivity = "sensitivity"
    redness = "redness"
    aging = "aging"
    texture = "texture"
    pores = "pores"
    dark_circles = "dark_circles"
    dehydration = "dehydration"
    brightening = "brightening"


class ProfileUpdate(BaseModel):
    skin_type: Optional[SkinType] = None
    concerns: Optional[list[SkinConcern]] = None
    notes: Optional[str] = None


class ProfileResponse(BaseModel):
    id: int
    skin_type: Optional[SkinType]
    concerns: Optional[list[SkinConcern]]
    notes: Optional[str]
