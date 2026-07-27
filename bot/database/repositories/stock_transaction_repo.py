from __future__ import annotations

from datetime import datetime, timezone
from typing import Optional

from motor.motor_asyncio import AsyncIOMotorDatabase

from bot.database.models.stock_transaction import StockTransactionModel


class StockTransactionRepository:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.collection = db.stock_transactions

    async def add_transaction(self, tx: StockTransactionModel) -> StockTransactionModel:
        await self.collection.insert_one(tx.to_dict())
        return tx

    async def get_user_transactions(self, user_id: int, ticker: str = None, limit: int = 20) -> list[StockTransactionModel]:
        query = {"user_id": user_id}
        if ticker:
            query["ticker"] = ticker.upper()
        cursor = self.collection.find(query).sort("created_at", -1).limit(limit)
        docs = await cursor.to_list(length=limit)
        return [StockTransactionModel.from_doc(d) for d in docs]

    async def get_user_trades(self, user_id: int) -> int:
        return await self.collection.count_documents({"user_id": user_id})

    async def check_recent_duplicate(self, user_id: int, ticker: str, action: str, amount: int) -> bool:
        recent = await self.collection.find_one({
            "user_id": user_id,
            "ticker": ticker.upper(),
            "action": action,
            "total_amount": amount,
            "created_at": {"$gte": datetime.now(timezone.utc).timestamp() - 5},
        })
        return recent is not None
