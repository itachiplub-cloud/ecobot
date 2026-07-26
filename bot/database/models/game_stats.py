from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class GameStatsModel(BaseModel):
    user_id: int
    games_played: int = 0
    games_won: int = 0
    games_lost: int = 0
    total_coins_won: int = 0
    total_coins_lost: int = 0
    highest_win: int = 0
    highest_bet: int = 0
    current_win_streak: int = 0
    current_lose_streak: int = 0
    longest_win_streak: int = 0
    longest_lose_streak: int = 0
    favorite_game: str = ""
    daily_games: int = 0
    weekly_games: int = 0
    monthly_games: int = 0
    lifetime_games: int = 0
    last_game_date: Optional[datetime] = None
    daily_reset: Optional[datetime] = None
    weekly_reset: Optional[datetime] = None
    monthly_reset: Optional[datetime] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        arbitrary_types_allowed = True

    def to_dict(self) -> dict:
        return self.model_dump(exclude_unset=True)

    @classmethod
    def from_doc(cls, doc: dict) -> GameStatsModel:
        if doc is None:
            return None
        doc.pop("_id", None)
        return cls(**doc)
