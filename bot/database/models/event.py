from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class EventModel(BaseModel):
    event_id: str
    event_type: str
    name: str
    description: str = ""
    rewards: dict = Field(default_factory=dict)
    modifiers: dict = Field(default_factory=dict)
    requirements: dict = Field(default_factory=dict)
    max_participants: int = -1
    participants: list = Field(default_factory=list)
    is_active: bool = True
    is_recurring: bool = False
    recurrence_pattern: Optional[str] = None
    start_at: Optional[datetime] = None
    end_at: Optional[datetime] = None
    created_by: Optional[int] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        arbitrary_types_allowed = True

    def to_dict(self) -> dict:
        return self.model_dump(exclude_unset=True)

    @classmethod
    def from_doc(cls, doc: dict) -> EventModel:
        if doc is None:
            return None
        doc.pop("_id", None)
        return cls(**doc)
