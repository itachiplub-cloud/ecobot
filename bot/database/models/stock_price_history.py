from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class StockPriceHistoryModel(BaseModel):
    ticker: str
    price: float
    volume: int = 0
    high: float = 0.0
    low: float = 0.0
    recorded_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        arbitrary_types_allowed = True

    def to_dict(self) -> dict:
        return self.model_dump(exclude_unset=True)

    @classmethod
    def from_doc(cls, doc: dict) -> Optional["StockPriceHistoryModel"]:
        if doc is None:
            return None
        doc.pop("_id", None)
        return cls(**doc)
