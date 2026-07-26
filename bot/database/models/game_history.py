from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class GameHistoryModel(BaseModel):
    user_id: int
    game_type: str
    bet_amount: int
    result: str
    won: bool
    payout: int = 0
    multiplier: float = 1.0
    metadata: dict = Field(default_factory=dict)
    chat_id: Optional[int] = None
    chat_type: str = "private"
    created_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        arbitrary_types_allowed = True

    def to_dict(self) -> dict:
        return self.model_dump(exclude_unset=True)

    @classmethod
    def from_doc(cls, doc: dict) -> GameHistoryModel:
        if doc is None:
            return None
        doc.pop("_id", None)
        return cls(**doc)
