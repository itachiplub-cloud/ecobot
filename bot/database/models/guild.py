from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class GuildModel(BaseModel):
    guild_id: int
    name: str
    tag: str
    description: str = ""
    owner_id: int
    level: int = 1
    xp: int = 0
    xp_needed: int = 500
    treasury: int = 0
    bank: int = 0
    member_count: int = 1
    max_members: int = 50
    war_wins: int = 0
    war_losses: int = 0
    missions_completed: int = 0
    rank: int = 0
    banner: Optional[str] = None
    settings: dict = Field(default_factory=lambda: {
        "join_type": "open",
        "min_level": 1,
        "tax_rate": 0.05,
    })
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        arbitrary_types_allowed = True

    def to_dict(self) -> dict:
        return self.model_dump(exclude_unset=True)

    @classmethod
    def from_doc(cls, doc: dict) -> GuildModel:
        if doc is None:
            return None
        doc.pop("_id", None)
        return cls(**doc)


class GuildMemberModel(BaseModel):
    guild_id: int
    user_id: int
    role: str = "member"
    contribution: int = 0
    donations: int = 0
    xp_contributed: int = 0
    joined_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        arbitrary_types_allowed = True

    def to_dict(self) -> dict:
        return self.model_dump(exclude_unset=True)

    @classmethod
    def from_doc(cls, doc: dict) -> GuildMemberModel:
        if doc is None:
            return None
        doc.pop("_id", None)
        return cls(**doc)
