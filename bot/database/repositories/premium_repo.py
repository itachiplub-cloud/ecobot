from __future__ import annotations

from datetime import datetime, timezone
from typing import Optional

from motor.motor_asyncio import AsyncIOMotorDatabase

from bot.database.models.premium import PremiumModel


class PremiumRepository:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.collection = db.premium

    async def get_premium(self, user_id: int) -> Optional[PremiumModel]:
        doc = await self.collection.find_one({"user_id": user_id})
        return PremiumModel.from_doc(doc)

    async def set_premium(self, user_id: int, tier: int = 1, expires_at: Optional[datetime] = None) -> PremiumModel:
        prem = PremiumModel(user_id=user_id, tier=tier, expires_at=expires_at)
        await self.collection.update_one(
            {"user_id": user_id},
            {"$set": prem.to_dict()},
            upsert=True,
        )
        return prem

    async def remove_premium(self, user_id: int) -> bool:
        result = await self.collection.delete_one({"user_id": user_id})
        return result.deleted_count > 0

    async def is_premium(self, user_id: int) -> bool:
        doc = await self.collection.find_one({"user_id": user_id})
        if not doc:
            return False
        prem = PremiumModel.from_doc(doc)
        if prem.expires_at and prem.expires_at < datetime.now(timezone.utc):
            await self.remove_premium(user_id)
            return False
        return True

    async def get_all_premium(self) -> list[PremiumModel]:
        cursor = self.collection.find({})
        docs = await cursor.to_list(length=None)
        return [PremiumModel.from_doc(d) for d in docs]

    async def cleanup_expired(self) -> int:
        result = await self.collection.delete_many({
            "expires_at": {"$lt": datetime.now(timezone.utc), "$ne": None},
        })
        return result.deleted_count
