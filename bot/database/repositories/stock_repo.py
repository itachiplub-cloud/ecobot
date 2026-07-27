from __future__ import annotations

from datetime import datetime, timezone
from typing import Optional

from motor.motor_asyncio import AsyncIOMotorDatabase

from bot.database.models.stock import StockModel


class StockRepository:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.collection = db.stocks

    async def get_stock(self, ticker: str) -> Optional[StockModel]:
        doc = await self.collection.find_one({"ticker": ticker.upper()})
        return StockModel.from_doc(doc)

    async def create_stock(self, stock: StockModel) -> StockModel:
        await self.collection.insert_one(stock.to_dict())
        return stock

    async def update_stock(self, ticker: str, **data) -> None:
        data["updated_at"] = datetime.now(timezone.utc)
        await self.collection.update_one({"ticker": ticker.upper()}, {"$set": data})

    async def delete_stock(self, ticker: str) -> bool:
        result = await self.collection.delete_one({"ticker": ticker.upper()})
        return result.deleted_count > 0

    async def get_all_stocks(self, active_only: bool = True) -> list[StockModel]:
        query = {"is_active": True} if active_only else {}
        cursor = self.collection.find(query).sort("ticker", 1)
        docs = await cursor.to_list(length=None)
        return [StockModel.from_doc(d) for d in docs]

    async def get_top_gainers(self, limit: int = 10) -> list[StockModel]:
        pipeline = [
            {"$match": {"is_active": True, "opening_price": {"$gt": 0}}},
            {"$addFields": {
                "change_pct": {
                    "$multiply": [
                        {"$divide": [
                            {"$subtract": ["$current_price", "$opening_price"]},
                            "$opening_price"
                        ]},
                        100
                    ]
                }
            }},
            {"$sort": {"change_pct": -1}},
            {"$limit": limit},
        ]
        cursor = self.collection.aggregate(pipeline)
        docs = await cursor.to_list(length=limit)
        return [StockModel.from_doc(d) for d in docs]

    async def get_top_losers(self, limit: int = 10) -> list[StockModel]:
        pipeline = [
            {"$match": {"is_active": True, "opening_price": {"$gt": 0}}},
            {"$addFields": {
                "change_pct": {
                    "$multiply": [
                        {"$divide": [
                            {"$subtract": ["$current_price", "$opening_price"]},
                            "$opening_price"
                        ]},
                        100
                    ]
                }
            }},
            {"$sort": {"change_pct": 1}},
            {"$limit": limit},
        ]
        cursor = self.collection.aggregate(pipeline)
        docs = await cursor.to_list(length=limit)
        return [StockModel.from_doc(d) for d in docs]

    async def search_stocks(self, query: str, limit: int = 20) -> list[StockModel]:
        regex = {"$regex": query, "$options": "i"}
        cursor = self.collection.find({
            "is_active": True,
            "$or": [{"ticker": regex}, {"name": regex}, {"sector": regex}]
        }).limit(limit)
        docs = await cursor.to_list(length=limit)
        return [StockModel.from_doc(d) for d in docs]

    async def get_by_sector(self, sector: str, limit: int = 50) -> list[StockModel]:
        cursor = self.collection.find({"sector": sector, "is_active": True}).sort("market_cap", -1).limit(limit)
        docs = await cursor.to_list(length=limit)
        return [StockModel.from_doc(d) for d in docs]

    async def count_stocks(self) -> int:
        return await self.collection.count_documents({"is_active": True})

    async def reset_all_prices(self) -> None:
        await self.collection.update_many({}, {"$set": {
            "current_price": 100.0,
            "opening_price": 100.0,
            "previous_close": 100.0,
            "daily_volume": 0,
            "updated_at": datetime.now(timezone.utc),
        }})
