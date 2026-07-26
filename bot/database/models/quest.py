from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class QuestModel(BaseModel):
    user_id: int
    quest_id: str
    quest_type: str
    title: str
    description: str = ""
    objectives: list = Field(default_factory=list)
    progress: dict = Field(default_factory=dict)
    reward_xp: int = 0
    reward_coins: int = 0
    reward_items: list = Field(default_factory=list)
    completed: bool = False
    claimed: bool = False
    expires_at: Optional[datetime] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        arbitrary_types_allowed = True

    def to_dict(self) -> dict:
        return self.model_dump(exclude_unset=True)

    @classmethod
    def from_doc(cls, doc: dict) -> QuestModel:
        if doc is None:
            return None
        doc.pop("_id", None)
        return cls(**doc)
