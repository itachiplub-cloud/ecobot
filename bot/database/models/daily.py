from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class DailyRewardModel(BaseModel):
    user_id: int
    daily_streak: int = 0
    weekly_streak: int = 0
    monthly_streak: int = 0
    yearly_streak: int = 0
    last_daily: Optional[datetime] = None
    last_weekly: Optional[datetime] = None
    last_monthly: Optional[datetime] = None
    last_yearly: Optional[datetime] = None
    total_claimed: int = 0
    best_streak: int = 0
    claims_history: list = Field(default_factory=list)
    created_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        arbitrary_types_allowed = True

    def to_dict(self) -> dict:
        return self.model_dump(exclude_unset=True)

    @classmethod
    def from_doc(cls, doc: dict) -> DailyRewardModel:
        if doc is None:
            return None
        doc.pop("_id", None)
        return cls(**doc)
