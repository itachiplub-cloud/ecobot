from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class LogModel(BaseModel):
    level: str = "INFO"
    message: str = ""
    user_id: Optional[int] = None
    command: Optional[str] = None
    error: Optional[str] = None
    metadata: dict = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        arbitrary_types_allowed = True

    def to_dict(self) -> dict:
        return self.model_dump(exclude_unset=True)

    @classmethod
    def from_doc(cls, doc: dict) -> LogModel:
        if doc is None:
            return None
        doc.pop("_id", None)
        return cls(**doc)
