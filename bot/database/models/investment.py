from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class InvestmentModel(BaseModel):
    user_id: int
    investment_id: str
    amount: int
    investment_type: str = "fixed"
    interest_rate: float = 0.05
    returns: int = 0
    risk_level: str = "low"
    status: str = "active"
    started_at: datetime = Field(default_factory=datetime.utcnow)
    matures_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None

    class Config:
        arbitrary_types_allowed = True

    def to_dict(self) -> dict:
        return self.model_dump(exclude_unset=True)

    @classmethod
    def from_doc(cls, doc: dict) -> InvestmentModel:
        if doc is None:
            return None
        doc.pop("_id", None)
        return cls(**doc)


class GamePassModel(BaseModel):
    user_id: int
    season: int = 1
    tier: int = 1
    xp: int = 0
    xp_needed: int = 100
    premium: bool = False
    daily_missions_completed: list = Field(default_factory=list)
    weekly_missions_completed: list = Field(default_factory=list)
    unlocked_rewards: list = Field(default_factory=list)
    claimed_rewards: list = Field(default_factory=list)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        arbitrary_types_allowed = True

    def to_dict(self) -> dict:
        return self.model_dump(exclude_unset=True)

    @classmethod
    def from_doc(cls, doc: dict) -> GamePassModel:
        if doc is None:
            return None
        doc.pop("_id", None)
        return cls(**doc)
