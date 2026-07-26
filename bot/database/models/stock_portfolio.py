from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class StockPortfolioModel(BaseModel):
    user_id: int
    ticker: str
    shares: int = 0
    avg_buy_price: float = 0.0
    total_invested: int = 0
    stop_loss_pct: Optional[float] = None
    take_profit_pct: Optional[float] = None
    is_favorite: bool = False
    total_sold: int = 0
    lifetime_profit: int = 0
    lifetime_loss: int = 0
    first_bought: datetime = Field(default_factory=datetime.utcnow)
    last_updated: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        arbitrary_types_allowed = True

    def to_dict(self) -> dict:
        return self.model_dump(exclude_unset=True)

    @classmethod
    def from_doc(cls, doc: dict) -> Optional["StockPortfolioModel"]:
        if doc is None:
            return None
        doc.pop("_id", None)
        return cls(**doc)
