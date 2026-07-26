from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class AchievementModel(BaseModel):
    user_id: int
    achievement_id: str
    progress: int = 0
    max_progress: int = 1
    completed: bool = False
    claimed: bool = False
    completed_at: Optional[datetime] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        arbitrary_types_allowed = True

    def to_dict(self) -> dict:
        return self.model_dump(exclude_unset=True)

    @classmethod
    def from_doc(cls, doc: dict) -> AchievementModel:
        if doc is None:
            return None
        doc.pop("_id", None)
        return cls(**doc)
