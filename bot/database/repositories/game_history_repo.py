from __future__ import annotations

from datetime import datetime
from typing import Optional

from motor.motor_asyncio import AsyncIOMotorDatabase

from bot.database.models.game_history import GameHistoryModel


class GameHistoryRepository:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.collection = db.game_history

    async def add_history(self, history: GameHistoryModel) -> GameHistoryModel:
        await self.collection.insert_one(history.to_dict())
        return history

    async def get_user_history(self, user_id: int, game_type: str = None, limit: int = 50) -> list[GameHistoryModel]:
        query = {"user_id": user_id}
        if game_type:
            query["game_type"] = game_type
        cursor = self.collection.find(query).sort("created_at", -1).limit(limit)
        docs = await cursor.to_list(length=limit)
        return [GameHistoryModel.from_doc(d) for d in docs]

    async def get_game_count(self, user_id: int, game_type: str = None, within_hours: int = None) -> int:
        query = {"user_id": user_id}
        if game_type:
            query["game_type"] = game_type
        if within_hours:
            from datetime import timedelta
            cutoff = datetime.utcnow() - timedelta(hours=within_hours)
            query["created_at"] = {"$gte": cutoff}
        return await self.collection.count_documents(query)

    async def get_recent_wins(self, user_id: int, limit: int = 10) -> list[GameHistoryModel]:
        cursor = self.collection.find({"user_id": user_id, "won": True}).sort("created_at", -1).limit(limit)
        docs = await cursor.to_list(length=limit)
        return [GameHistoryModel.from_doc(d) for d in docs]

    async def get_daily_volume(self, user_id: int) -> int:
        from datetime import timedelta
        today = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
        pipeline = [
            {"$match": {"user_id": user_id, "created_at": {"$gte": today}}},
            {"$group": {"_id": None, "total": {"$sum": "$bet_amount"}}},
        ]
        result = await self.collection.aggregate(pipeline).to_list(1)
        return result[0]["total"] if result else 0

    async def cleanup_old(self, days: int = 90) -> int:
        from datetime import timedelta
        cutoff = datetime.utcnow() - timedelta(days=days)
        result = await self.collection.delete_many({"created_at": {"$lt": cutoff}})
        return result.deleted_count
