from __future__ import annotations

import random
import string
from datetime import datetime, timezone
from typing import Optional

from motor.motor_asyncio import AsyncIOMotorDatabase

from bot.database.models.investment import InvestmentModel


class InvestmentRepository:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.collection = db.investments

    async def create_investment(self, investment: InvestmentModel) -> InvestmentModel:
        await self.collection.insert_one(investment.to_dict())
        return investment

    async def get_investment(self, user_id: int, investment_id: str) -> Optional[InvestmentModel]:
        doc = await self.collection.find_one({"user_id": user_id, "investment_id": investment_id})
        return InvestmentModel.from_doc(doc)

    async def get_user_investments(self, user_id: int, status: str = "active") -> list[InvestmentModel]:
        cursor = self.collection.find({"user_id": user_id, "status": status})
        docs = await cursor.to_list(length=None)
        return [InvestmentModel.from_doc(d) for d in docs]

    async def complete_investment(self, user_id: int, investment_id: str, returns: int) -> Optional[InvestmentModel]:
        inv = await self.get_investment(user_id, investment_id)
        if not inv:
            return None
        await self.collection.update_one(
            {"user_id": user_id, "investment_id": investment_id},
            {"$set": {"status": "completed", "returns": returns, "completed_at": datetime.now(timezone.utc)}},
        )
        inv.status = "completed"
        inv.returns = returns
        return inv

    async def cancel_investment(self, user_id: int, investment_id: str) -> bool:
        result = await self.collection.update_one(
            {"user_id": user_id, "investment_id": investment_id, "status": "active"},
            {"$set": {"status": "cancelled", "completed_at": datetime.now(timezone.utc)}},
        )
        return result.modified_count > 0

    async def get_all_active(self) -> list[InvestmentModel]:
        cursor = self.collection.find({"status": "active"})
        docs = await cursor.to_list(length=None)
        return [InvestmentModel.from_doc(d) for d in docs]

    async def get_total_invested(self, user_id: int) -> int:
        pipeline = [
            {"$match": {"user_id": user_id, "status": "active"}},
            {"$group": {"_id": None, "total": {"$sum": "$amount"}}},
        ]
        result = await self.collection.aggregate(pipeline).to_list(1)
        return result[0]["total"] if result else 0

    def generate_investment_id(self) -> str:
        return "INV-" + "".join(random.choices(string.ascii_uppercase + string.digits, k=8))
