from __future__ import annotations

from datetime import datetime, timezone
from typing import Optional

from motor.motor_asyncio import AsyncIOMotorDatabase

from bot.database.models.leaderboard import LeaderboardModel


class LeaderboardRepository:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.collection = db.leaderboards

    async def update_score(self, user_id: int, category: str, score: int) -> None:
        await self.collection.update_one(
            {"user_id": user_id, "category": category},
            {"$set": {"score": score, "updated_at": datetime.now(timezone.utc)}},
            upsert=True,
        )

    async def increment_score(self, user_id: int, category: str, amount: int) -> None:
        await self.collection.update_one(
            {"user_id": user_id, "category": category},
            {"$inc": {"score": amount}, "$set": {"updated_at": datetime.now(timezone.utc)}},
            upsert=True,
        )

    async def get_top(self, category: str, limit: int = 10) -> list[LeaderboardModel]:
        cursor = self.collection.find({"category": category}).sort("score", -1).limit(limit)
        docs = await cursor.to_list(length=limit)
        return [LeaderboardModel.from_doc(d) for d in docs]

    async def get_rank(self, user_id: int, category: str) -> Optional[int]:
        user_doc = await self.collection.find_one({"user_id": user_id, "category": category})
        if not user_doc:
            return None
        rank = await self.collection.count_documents({
            "category": category,
            "score": {"$gt": user_doc["score"]},
        })
        return rank + 1

    async def get_score(self, user_id: int, category: str) -> int:
        doc = await self.collection.find_one({"user_id": user_id, "category": category})
        return doc["score"] if doc else 0

    async def get_categories(self) -> list[str]:
        pipeline = [
            {"$group": {"_id": "$category"}},
            {"$sort": {"_id": 1}},
        ]
        cursor = self.collection.aggregate(pipeline)
        docs = await cursor.to_list(length=None)
        return [d["_id"] for d in docs]
