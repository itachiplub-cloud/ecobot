from __future__ import annotations

from datetime import datetime, timezone
from typing import Optional

from motor.motor_asyncio import AsyncIOMotorDatabase

from bot.database.models.stock_market_event import StockMarketEventModel


class StockMarketEventRepository:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.collection = db.stock_market_events

    async def create_event(self, event: StockMarketEventModel) -> StockMarketEventModel:
        await self.collection.insert_one(event.to_dict())
        return event

    async def get_active_events(self, ticker: str = None) -> list[StockMarketEventModel]:
        query = {"active": True}
        if ticker:
            query["$or"] = [{"ticker": ticker.upper()}, {"is_global": True}]
        else:
            query["is_global"] = True
        now = datetime.now(timezone.utc)
        query["$or"] = [{"expires_at": None}, {"expires_at": {"$gt": now}}]
        cursor = self.collection.find(query)
        docs = await cursor.to_list(length=None)
        return [StockMarketEventModel.from_doc(d) for d in docs]

    async def expire_events(self) -> int:
        result = await self.collection.update_many(
            {"active": True, "expires_at": {"$lte": datetime.now(timezone.utc)}},
            {"$set": {"active": False}},
        )
        return result.modified_count

    async def deactivate_event(self, event_id: str) -> bool:
        result = await self.collection.update_one(
            {"event_id": event_id},
            {"$set": {"active": False}},
        )
        return result.modified_count > 0
