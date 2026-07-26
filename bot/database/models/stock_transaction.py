from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class StockTransactionModel(BaseModel):
    user_id: int
    ticker: str
    action: str = "buy"
    shares: int = 0
    price_per_share: float = 0.0
    total_amount: int = 0
    tax: int = 0
    profit: int = 0
    created_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        arbitrary_types_allowed = True

    def to_dict(self) -> dict:
        return self.model_dump(exclude_unset=True)

    @classmethod
    def from_doc(cls, doc: dict) -> Optional["StockTransactionModel"]:
        if doc is None:
            return None
        doc.pop("_id", None)
        return cls(**doc)
