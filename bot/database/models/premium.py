from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class PremiumModel(BaseModel):
    user_id: int
    tier: int = 1
    expires_at: Optional[datetime] = None
    purchased_at: datetime = Field(default_factory=datetime.utcnow)
    auto_renew: bool = False
    features: list = Field(default_factory=list)

    class Config:
        arbitrary_types_allowed = True

    def to_dict(self) -> dict:
        return self.model_dump(exclude_unset=True)

    @classmethod
    def from_doc(cls, doc: dict) -> PremiumModel:
        if doc is None:
            return None
        doc.pop("_id", None)
        return cls(**doc)
