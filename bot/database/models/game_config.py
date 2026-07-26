from __future__ import annotations

from datetime import datetime
from typing import Any, Optional

from pydantic import BaseModel, Field


class GameConfigModel(BaseModel):
    game_type: str
    cooldown_seconds: int = 60
    min_bet: int = 10
    max_bet: int = 10000
    multiplier: float = 2.0
    difficulty: str = "normal"
    house_edge: float = 0.05
    win_chance: float = 0.5
    xp_reward: int = 10
    coins_reward: int = 0
    bonus_reward: int = 0
    daily_limit: int = 100
    is_enabled: bool = True
    settings: dict = Field(default_factory=dict)
    updated_by: Optional[int] = None
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    created_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        arbitrary_types_allowed = True

    def to_dict(self) -> dict:
        return self.model_dump(exclude_unset=True)

    @classmethod
    def from_doc(cls, doc: dict) -> GameConfigModel:
        if doc is None:
            return None
        doc.pop("_id", None)
        return cls(**doc)
