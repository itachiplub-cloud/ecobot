from __future__ import annotations

from datetime import datetime, timezone

from motor.motor_asyncio import AsyncIOMotorDatabase

from bot.database.models.cooldown import CooldownModel


class CooldownRepository:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.collection = db.cooldowns

    async def set_cooldown(self, user_id: int, action: str, seconds: int) -> None:
        from datetime import timedelta
        expires = datetime.now(timezone.utc) + timedelta(seconds=seconds)
        await self.collection.update_one(
            {"user_id": user_id, "action": action},
            {"$set": {"expires_at": expires, "created_at": datetime.now(timezone.utc)}},
            upsert=True,
        )

    async def get_cooldown(self, user_id: int, action: str) -> CooldownModel | None:
        doc = await self.collection.find_one({"user_id": user_id, "action": action})
        if not doc:
            return None
        return CooldownModel.from_doc(doc)

    async def is_on_cooldown(self, user_id: int, action: str) -> tuple[bool, int]:
        doc = await self.collection.find_one({"user_id": user_id, "action": action})
        if not doc:
            return False, 0
        remaining = (doc["expires_at"] - datetime.now(timezone.utc)).total_seconds()
        if remaining <= 0:
            await self.collection.delete_one({"user_id": user_id, "action": action})
            return False, 0
        return True, int(remaining)

    async def clear_cooldown(self, user_id: int, action: str) -> None:
        await self.collection.delete_one({"user_id": user_id, "action": action})

    async def clear_all_cooldowns(self, user_id: int) -> None:
        await self.collection.delete_many({"user_id": user_id})

    async def cleanup_expired(self) -> int:
        result = await self.collection.delete_many({"expires_at": {"$lt": datetime.now(timezone.utc)}})
        return result.deleted_count
