from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class InventoryModel(BaseModel):
    user_id: int
    item_id: str
    quantity: int = 1
    equipped: bool = False
    slot: Optional[str] = None
    durability: int = 100
    upgraded: bool = False
    upgrade_level: int = 0
    purchased_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        arbitrary_types_allowed = True

    def to_dict(self) -> dict:
        return self.model_dump(exclude_unset=True)

    @classmethod
    def from_doc(cls, doc: dict) -> InventoryModel:
        if doc is None:
            return None
        doc.pop("_id", None)
        return cls(**doc)
