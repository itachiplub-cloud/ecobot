from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class TransactionModel(BaseModel):
    user_id: int
    transaction_type: str
    amount: int
    balance_before: int = 0
    balance_after: int = 0
    description: str = ""
    target_user: Optional[int] = None
    item_id: Optional[str] = None
    quantity: int = 1
    metadata: dict = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        arbitrary_types_allowed = True

    def to_dict(self) -> dict:
        return self.model_dump(exclude_unset=True)

    @classmethod
    def from_doc(cls, doc: dict) -> TransactionModel:
        if doc is None:
            return None
        doc.pop("_id", None)
        return cls(**doc)
