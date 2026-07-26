from __future__ import annotations

from datetime import datetime

from motor.motor_asyncio import AsyncIOMotorDatabase

from bot.database.models.stock_price_history import StockPriceHistoryModel


class StockPriceHistoryRepository:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.collection = db.stock_price_history

    async def record_price(self, history: StockPriceHistoryModel) -> None:
        await self.collection.insert_one(history.to_dict())

    async def get_price_history(self, ticker: str, limit: int = 50) -> list[StockPriceHistoryModel]:
        cursor = self.collection.find({"ticker": ticker.upper()}).sort("recorded_at", -1).limit(limit)
        docs = await cursor.to_list(length=limit)
        return [StockPriceHistoryModel.from_doc(d) for d in docs]

    async def get_latest_price(self, ticker: str) -> float:
        doc = await self.collection.find_one(
            {"ticker": ticker.upper()},
            sort=[("recorded_at", -1)],
        )
        return doc["price"] if doc else 0.0

    async def cleanup_old(self, days: int = 30) -> int:
        from datetime import timedelta
        cutoff = datetime.utcnow() - timedelta(days=days)
        result = await self.collection.delete_many({"recorded_at": {"$lt": cutoff}})
        return result.deleted_count
