from __future__ import annotations

from datetime import datetime, timezone
from typing import Optional

from motor.motor_asyncio import AsyncIOMotorDatabase

from bot.database.models.transaction import TransactionModel


class TransactionRepository:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.collection = db.transactions

    async def add_transaction(self, tx: TransactionModel) -> TransactionModel:
        await self.collection.insert_one(tx.to_dict())
        return tx

    async def get_transactions(self, user_id: int, limit: int = 50) -> list[TransactionModel]:
        cursor = self.collection.find({"user_id": user_id}).sort("created_at", -1).limit(limit)
        docs = await cursor.to_list(length=limit)
        return [TransactionModel.from_doc(d) for d in docs]

    async def get_transaction_count(self, user_id: int) -> int:
        return await self.collection.count_documents({"user_id": user_id})

    async def get_total_volume(self, user_id: int) -> int:
        pipeline = [
            {"$match": {"user_id": user_id}},
            {"$group": {"_id": None, "total": {"$sum": "$amount"}}},
        ]
        result = await self.collection.aggregate(pipeline).to_list(1)
        return result[0]["total"] if result else 0

    async def check_duplicate(self, user_id: int, tx_type: str, amount: int, within_seconds: int = 5) -> bool:
        cutoff = datetime.now(timezone.utc)
        from datetime import timedelta
        cutoff -= timedelta(seconds=within_seconds)
        count = await self.collection.count_documents({
            "user_id": user_id,
            "transaction_type": tx_type,
            "amount": amount,
            "created_at": {"$gte": cutoff},
        })
        return count > 0

    async def get_date_range(self, user_id: int, start: datetime, end: datetime) -> list[TransactionModel]:
        cursor = self.collection.find({
            "user_id": user_id,
            "created_at": {"$gte": start, "$lte": end},
        }).sort("created_at", -1)
        docs = await cursor.to_list(length=None)
        return [TransactionModel.from_doc(d) for d in docs]
