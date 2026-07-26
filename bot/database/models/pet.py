from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class PetModel(BaseModel):
    user_id: int
    pet_id: str
    pet_type: str
    name: str
    level: int = 1
    xp: int = 0
    xp_needed: int = 100
    happiness: int = 100
    hunger: int = 100
    health: int = 100
    attack: int = 10
    defense: int = 10
    speed: int = 10
    skills: list = Field(default_factory=list)
    equipped: bool = False
    evolution_level: int = 0
    max_evolution: int = 3
    rarity: str = "common"
    last_fed: Optional[datetime] = None
    last_played: Optional[datetime] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        arbitrary_types_allowed = True

    def to_dict(self) -> dict:
        return self.model_dump(exclude_unset=True)

    @classmethod
    def from_doc(cls, doc: dict) -> PetModel:
        if doc is None:
            return None
        doc.pop("_id", None)
        return cls(**doc)
