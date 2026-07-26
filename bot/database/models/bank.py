from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class BankModel(BaseModel):
    user_id: int
    balance: int = 0
    interest_rate: float = 0.02
    last_interest: Optional[datetime] = None
    total_interest_earned: int = 0
    loan_amount: int = 0
    loan_interest_rate: float = 0.05
    loan_taken_at: Optional[datetime] = None
    loan_due: Optional[datetime] = None
    investments: list = Field(default_factory=list)
    total_invested: int = 0
    investment_returns: int = 0
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        arbitrary_types_allowed = True

    def to_dict(self) -> dict:
        return self.model_dump(exclude_unset=True)

    @classmethod
    def from_doc(cls, doc: dict) -> BankModel:
        if doc is None:
            return None
        doc.pop("_id", None)
        return cls(**doc)
