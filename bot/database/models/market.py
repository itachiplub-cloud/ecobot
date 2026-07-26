from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class MarketModel(BaseModel):
    listing_id: str
    seller_id: int
    item_id: str
    quantity: int = 1
    price: int = 0
    description: str = ""
    featured: bool = False
    sold: bool = False
    buyer_id: Optional[int] = None
    expires_at: Optional[datetime] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        arbitrary_types_allowed = True

    def to_dict(self) -> dict:
        return self.model_dump(exclude_unset=True)

    @classmethod
    def from_doc(cls, doc: dict) -> MarketModel:
        if doc is None:
            return None
        doc.pop("_id", None)
        return cls(**doc)


class AuctionModel(BaseModel):
    auction_id: str
    seller_id: int
    item_id: str
    quantity: int = 1
    starting_bid: int = 0
    current_bid: int = 0
    current_bidder: Optional[int] = None
    bid_count: int = 0
    buyout_price: Optional[int] = None
    ended: bool = False
    winner_id: Optional[int] = None
    expires_at: Optional[datetime] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        arbitrary_types_allowed = True

    def to_dict(self) -> dict:
        return self.model_dump(exclude_unset=True)

    @classmethod
    def from_doc(cls, doc: dict) -> AuctionModel:
        if doc is None:
            return None
        doc.pop("_id", None)
        return cls(**doc)
