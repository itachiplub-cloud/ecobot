from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class GroupRankingModel(BaseModel):
    user_id: int
    group_id: int
    xp_earned: int = 0
    messages_sent: int = 0
    coins_earned: int = 0
    games_played: int = 0
    level: int = 1
    title: str = ""
    joined_at: datetime = Field(default_factory=datetime.utcnow)
    last_active: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        arbitrary_types_allowed = True

    def to_dict(self) -> dict:
        return self.model_dump(exclude_unset=True)

    @classmethod
    def from_doc(cls, doc: dict) -> Optional["GroupRankingModel"]:
        if doc is None:
            return None
        doc.pop("_id", None)
        return cls(**doc)
