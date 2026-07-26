from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class StockModel(BaseModel):
    ticker: str
    name: str
    sector: str = "general"
    current_price: float = 100.0
    opening_price: float = 100.0
    previous_close: float = 100.0
    market_cap: float = 1_000_000.0
    popularity: float = 50.0
    volatility: str = "medium"
    is_active: bool = True
    total_shares: int = 1_000_000
    available_shares: int = 1_000_000
    daily_volume: int = 0
    daily_high: float = 0.0
    daily_low: float = 999999.0
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        arbitrary_types_allowed = True

    def to_dict(self) -> dict:
        return self.model_dump(exclude_unset=True)

    @classmethod
    def from_doc(cls, doc: dict) -> Optional["StockModel"]:
        if doc is None:
            return None
        doc.pop("_id", None)
        return cls(**doc)
