from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field


class CooldownModel(BaseModel):
    user_id: int
    action: str
    expires_at: datetime
    created_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        arbitrary_types_allowed = True

    def to_dict(self) -> dict:
        return self.model_dump(exclude_unset=True)

    @classmethod
    def from_doc(cls, doc: dict) -> CooldownModel:
        if doc is None:
            return None
        doc.pop("_id", None)
        return cls(**doc)
