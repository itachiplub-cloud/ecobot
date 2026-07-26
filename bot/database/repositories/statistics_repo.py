from __future__ import annotations

from datetime import date, datetime

from motor.motor_asyncio import AsyncIOMotorDatabase

from bot.database.models.statistics import StatisticsModel


class StatisticsRepository:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.collection = db.statistics

    async def get_today(self) -> StatisticsModel:
        today = date.today()
        doc = await self.collection.find_one({"stat_date": today.isoformat()})
        if doc:
            return StatisticsModel.from_doc(doc)
        stats = StatisticsModel(stat_date=today)
        await self.collection.insert_one(stats.to_dict())
        return stats

    async def increment(self, field: str, amount: int = 1) -> None:
        today = date.today().isoformat()
        await self.collection.update_one(
            {"stat_date": today},
            {"$inc": {field: amount}},
            upsert=True,
        )

    async def get_range(self, start_date: date, end_date: date) -> list[StatisticsModel]:
        cursor = self.collection.find({
            "stat_date": {"$gte": start_date.isoformat(), "$lte": end_date.isoformat()},
        }).sort("stat_date", 1)
        docs = await cursor.to_list(length=None)
        return [StatisticsModel.from_doc(d) for d in docs]

    async def get_total(self, field: str) -> int:
        pipeline = [
            {"$group": {"_id": None, "total": {"$sum": f"${field}"}}},
        ]
        result = await self.collection.aggregate(pipeline).to_list(1)
        return result[0]["total"] if result else 0
