from __future__ import annotations

from datetime import datetime
from typing import Any, Optional

from pydantic import BaseModel, Field


class BotSettingsModel(BaseModel):
    key: str
    value: Any = None
    description: str = ""
    updated_by: Optional[int] = None
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        arbitrary_types_allowed = True

    def to_dict(self) -> dict:
        return self.model_dump(exclude_unset=True)

    @classmethod
    def from_doc(cls, doc: dict) -> BotSettingsModel:
        if doc is None:
            return None
        doc.pop("_id", None)
        return cls(**doc)
