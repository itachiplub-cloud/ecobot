from __future__ import annotations

from typing import Optional

from motor.motor_asyncio import AsyncIOMotorDatabase

from bot.database.models.stock_watchlist import StockWatchlistModel


class StockWatchlistRepository:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.collection = db.stock_watchlists

    async def get_watchlist(self, user_id: int) -> StockWatchlistModel:
        doc = await self.collection.find_one({"user_id": user_id})
        if doc:
            return StockWatchlistModel.from_doc(doc)
        wl = StockWatchlistModel(user_id=user_id)
        await self.collection.insert_one(wl.to_dict())
        return wl

    async def add_to_watchlist(self, user_id: int, ticker: str) -> bool:
        result = await self.collection.update_one(
            {"user_id": user_id},
            {"$addToSet": {"tickers": ticker.upper()}},
            upsert=True,
        )
        return result.modified_count > 0 or result.upserted_id is not None

    async def remove_from_watchlist(self, user_id: int, ticker: str) -> bool:
        result = await self.collection.update_one(
            {"user_id": user_id},
            {"$pull": {"tickers": ticker.upper()}},
        )
        return result.modified_count > 0

    async def is_on_watchlist(self, user_id: int, ticker: str) -> bool:
        doc = await self.collection.find_one({"user_id": user_id, "tickers": ticker.upper()})
        return doc is not None

    async def get_all_watchlists(self) -> list[StockWatchlistModel]:
        cursor = self.collection.find({})
        docs = await cursor.to_list(length=None)
        return [StockWatchlistModel.from_doc(d) for d in docs]
