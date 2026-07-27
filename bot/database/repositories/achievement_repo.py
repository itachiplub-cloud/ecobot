from __future__ import annotations

from datetime import datetime, timezone
from typing import Optional

from motor.motor_asyncio import AsyncIOMotorDatabase

from bot.database.models.achievement import AchievementModel


class AchievementRepository:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.collection = db.achievements

    async def get_achievement(self, user_id: int, achievement_id: str) -> Optional[AchievementModel]:
        doc = await self.collection.find_one({"user_id": user_id, "achievement_id": achievement_id})
        return AchievementModel.from_doc(doc)

    async def unlock_achievement(self, user_id: int, achievement_id: str, max_progress: int = 1) -> bool:
        existing = await self.get_achievement(user_id, achievement_id)
        if existing and existing.completed:
            return False
        if existing:
            await self.collection.update_one(
                {"user_id": user_id, "achievement_id": achievement_id},
                {"$set": {"progress": max_progress, "completed": True, "completed_at": datetime.now(timezone.utc)}},
            )
        else:
            ach = AchievementModel(
                user_id=user_id,
                achievement_id=achievement_id,
                progress=max_progress,
                max_progress=max_progress,
                completed=True,
                completed_at=datetime.now(timezone.utc),
            )
            await self.collection.insert_one(ach.to_dict())
        return True

    async def update_progress(self, user_id: int, achievement_id: str, progress: int) -> dict:
        existing = await self.get_achievement(user_id, achievement_id)
        if existing and existing.completed:
            return {"completed": False, "newly_unlocked": False}
        if existing:
            new_progress = min(existing.progress + progress, existing.max_progress)
            newly_unlocked = new_progress >= existing.max_progress
            set_data = {"progress": new_progress}
            if newly_unlocked:
                set_data["completed"] = True
                set_data["completed_at"] = datetime.now(timezone.utc)
            await self.collection.update_one(
                {"user_id": user_id, "achievement_id": achievement_id},
                {"$set": set_data},
            )
            return {"completed": newly_unlocked, "newly_unlocked": newly_unlocked}
        return {"completed": False, "newly_unlocked": False}

    async def claim_reward(self, user_id: int, achievement_id: str) -> bool:
        result = await self.collection.update_one(
            {"user_id": user_id, "achievement_id": achievement_id, "completed": True, "claimed": False},
            {"$set": {"claimed": True}},
        )
        return result.modified_count > 0

    async def get_user_achievements(self, user_id: int) -> list[AchievementModel]:
        cursor = self.collection.find({"user_id": user_id})
        docs = await cursor.to_list(length=None)
        return [AchievementModel.from_doc(d) for d in docs]

    async def get_completed_count(self, user_id: int) -> int:
        return await self.collection.count_documents({"user_id": user_id, "completed": True})

    async def is_unlocked(self, user_id: int, achievement_id: str) -> bool:
        doc = await self.collection.find_one({
            "user_id": user_id,
            "achievement_id": achievement_id,
            "completed": True,
        })
        return doc is not None
