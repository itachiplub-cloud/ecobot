from __future__ import annotations

from datetime import datetime, timezone
from typing import Optional

from motor.motor_asyncio import AsyncIOMotorDatabase

from bot.database.models.log import LogModel


class LogRepository:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.collection = db.logs

    async def add_log(self, log: LogModel) -> LogModel:
        await self.collection.insert_one(log.to_dict())
        return log

    async def get_logs(self, level: Optional[str] = None, limit: int = 100) -> list[LogModel]:
        query = {}
        if level:
            query["level"] = level
        cursor = self.collection.find(query).sort("created_at", -1).limit(limit)
        docs = await cursor.to_list(length=limit)
        return [LogModel.from_doc(d) for d in docs]

    async def get_user_logs(self, user_id: int, limit: int = 50) -> list[LogModel]:
        cursor = self.collection.find({"user_id": user_id}).sort("created_at", -1).limit(limit)
        docs = await cursor.to_list(length=limit)
        return [LogModel.from_doc(d) for d in docs]

    async def cleanup_old(self, days: int = 30) -> int:
        from datetime import timedelta
        cutoff = datetime.now(timezone.utc) - timedelta(days=days)
        result = await self.collection.delete_many({"created_at": {"$lt": cutoff}})
        return result.deleted_count

    async def count_errors(self, since_hours: int = 24) -> int:
        from datetime import timedelta
        cutoff = datetime.now(timezone.utc) - timedelta(hours=since_hours)
        return await self.collection.count_documents({
            "level": "ERROR",
            "created_at": {"$gte": cutoff},
        })
