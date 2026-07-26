from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field


class BattlePassModel(BaseModel):
    user_id: int
    season: int = 1
    tier: int = 1
    xp: int = 0
    xp_needed: int = 100
    premium: bool = False
    unlocked_tiers: list = Field(default_factory=list)
    claimed_rewards: list = Field(default_factory=list)
    total_xp_earned: int = 0
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        arbitrary_types_allowed = True

    def to_dict(self) -> dict:
        return self.model_dump(exclude_unset=True)

    @classmethod
    def from_doc(cls, doc: dict) -> BattlePassModel:
        if doc is None:
            return None
        doc.pop("_id", None)
        return cls(**doc)
