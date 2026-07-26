from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class DeletedUserModel(BaseModel):
    original_user_id: int
    username: Optional[str] = None
    first_name: Optional[str] = None
    backup_data: dict = Field(default_factory=dict)
    deleted_by: int = 0
    delete_reason: str = ""
    deleted_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        arbitrary_types_allowed = True

    def to_dict(self) -> dict:
        return self.model_dump(exclude_unset=True)

    @classmethod
    def from_doc(cls, doc: dict) -> DeletedUserModel:
        if doc is None:
            return None
        doc.pop("_id", None)
        return cls(**doc)
