from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class StockMarketEventModel(BaseModel):
    event_id: str
    event_type: str
    ticker: Optional[str] = None
    title: str = ""
    description: str = ""
    price_modifier: float = 0.0
    multiplier: float = 1.0
    is_global: bool = False
    active: bool = True
    expires_at: Optional[datetime] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        arbitrary_types_allowed = True

    def to_dict(self) -> dict:
        return self.model_dump(exclude_unset=True)

    @classmethod
    def from_doc(cls, doc: dict) -> Optional["StockMarketEventModel"]:
        if doc is None:
            return None
        doc.pop("_id", None)
        return cls(**doc)
