from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class ShopModel(BaseModel):
    item_id: str
    shop_type: str = "permanent"
    stock: int = -1
    price_override: Optional[int] = None
    discount: float = 0.0
    featured: bool = False
    npc_name: Optional[str] = None
    min_level: int = 1
    rotation_day: Optional[int] = None
    expires_at: Optional[datetime] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        arbitrary_types_allowed = True

    def to_dict(self) -> dict:
        return self.model_dump(exclude_unset=True)

    @classmethod
    def from_doc(cls, doc: dict) -> ShopModel:
        if doc is None:
            return None
        doc.pop("_id", None)
        return cls(**doc)
