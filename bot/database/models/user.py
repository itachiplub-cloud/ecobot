from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class UserModel(BaseModel):
    user_id: int
    username: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    language: str = "en"
    level: int = 1
    xp: int = 0
    xp_needed: int = 100
    title: str = "Newcomer"
    bio: str = ""
    avatar_id: Optional[str] = None
    background_id: Optional[str] = "default"
    stats: dict = Field(default_factory=lambda: {
        "strength": 5,
        "defense": 5,
        "luck": 5,
        "speed": 5,
        "critical": 5,
    })
    total_earnings: int = 0
    total_spent: int = 0
    commands_used: int = 0
    games_played: int = 0
    crimes_committed: int = 0
    times_jailed: int = 0
    times_died: int = 0
    bosses_defeated: int = 0
    quests_completed: int = 0
    items_collected: int = 0
    guild_id: Optional[int] = None
    is_premium: bool = False
    premium_tier: int = 0
    is_banned: bool = False
    ban_reason: Optional[str] = None
    is_muted: bool = False
    settings: dict = Field(default_factory=lambda: {
        "notifications": True,
        "animations": True,
        "private_profile": False,
    })
    joined_at: datetime = Field(default_factory=datetime.utcnow)
    last_active: datetime = Field(default_factory=datetime.utcnow)
    last_daily: Optional[datetime] = None
    last_weekly: Optional[datetime] = None
    last_monthly: Optional[datetime] = None
    last_yearly: Optional[datetime] = None

    class Config:
        arbitrary_types_allowed = True

    def to_dict(self) -> dict:
        return self.model_dump(exclude_unset=True)

    @classmethod
    def from_doc(cls, doc: dict) -> UserModel:
        if doc is None:
            return None
        doc.pop("_id", None)
        return cls(**doc)
