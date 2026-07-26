from __future__ import annotations

from datetime import datetime as _datetime, date as _date

from pydantic import BaseModel, Field


class StatisticsModel(BaseModel):
    stat_date: _date = Field(default_factory=_date.today)
    total_users: int = 0
    active_users: int = 0
    new_users: int = 0
    messages_received: int = 0
    commands_executed: int = 0
    transactions: int = 0
    total_coins_earned: int = 0
    total_coins_spent: int = 0
    games_played: int = 0
    crimes_attempted: int = 0
    guilds_created: int = 0
    items_traded: int = 0
    uptime_seconds: int = 0
    errors: int = 0
    created_at: _datetime = Field(default_factory=_datetime.utcnow)

    class Config:
        arbitrary_types_allowed = True

    def to_dict(self) -> dict:
        return self.model_dump(exclude_unset=True)

    @classmethod
    def from_doc(cls, doc: dict) -> StatisticsModel:
        if doc is None:
            return None
        doc.pop("_id", None)
        return cls(**doc)
