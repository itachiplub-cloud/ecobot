from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class AdminModel(BaseModel):
    user_id: int
    role: str = "moderator"
    permissions: list = Field(default_factory=list)
    added_by: int = 0
    added_at: datetime = Field(default_factory=datetime.utcnow)
    is_active: bool = True

    class Config:
        arbitrary_types_allowed = True

    def to_dict(self) -> dict:
        return self.model_dump(exclude_unset=True)

    @classmethod
    def from_doc(cls, doc: dict) -> AdminModel:
        if doc is None:
            return None
        doc.pop("_id", None)
        return cls(**doc)
