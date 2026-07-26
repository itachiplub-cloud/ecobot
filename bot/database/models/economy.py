from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class EconomyModel(BaseModel):
    user_id: int
    wallet: int = 0
    bank: int = 0
    total_earned: int = 0
    total_spent: int = 0
    total_deposited: int = 0
    total_withdrawn: int = 0
    loans_taken: int = 0
    loans_repaid: int = 0
    current_loan: int = 0
    loan_interest: float = 0.0
    investment_amount: int = 0
    investment_returns: int = 0
    tax_paid: int = 0
    gifts_sent: int = 0
    gifts_received: int = 0
    heists_won: int = 0
    heists_lost: int = 0
    work_income: int = 0
    crime_income: int = 0
    game_income: int = 0
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        arbitrary_types_allowed = True

    def to_dict(self) -> dict:
        return self.model_dump(exclude_unset=True)

    @classmethod
    def from_doc(cls, doc: dict) -> EconomyModel:
        if doc is None:
            return None
        doc.pop("_id", None)
        return cls(**doc)
