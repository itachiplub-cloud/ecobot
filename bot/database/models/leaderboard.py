from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field


class LeaderboardModel(BaseModel):
    user_id: int
    category: str
    score: int = 0
    metadata: dict = Field(default_factory=dict)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        arbitrary_types_allowed = True

    def to_dict(self) -> dict:
        return self.model_dump(exclude_unset=True)

    @classmethod
    def from_doc(cls, doc: dict) -> LeaderboardModel:
        if doc is None:
            return None
        doc.pop("_id", None)
        return cls(**doc)
