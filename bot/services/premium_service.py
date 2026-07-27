from __future__ import annotations

from datetime import datetime, timedelta, timezone
from motor.motor_asyncio import AsyncIOMotorDatabase

from bot.database.repositories.premium_repo import PremiumRepository


class PremiumService:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.prem_repo = PremiumRepository(db)

    async def is_premium(self, user_id: int) -> bool:
        return await self.prem_repo.is_premium(user_id)

    async def set_premium(self, user_id: int, tier: int = 1, days: int = 30):
        expires = datetime.now(timezone.utc) + timedelta(days=days)
        return await self.prem_repo.set_premium(user_id, tier, expires)

    async def remove_premium(self, user_id: int) -> bool:
        return await self.prem_repo.remove_premium(user_id)

    async def get_premium(self, user_id: int):
        return await self.prem_repo.get_premium(user_id)

    async def get_all_premium(self):
        return await self.prem_repo.get_all_premium()

    async def cleanup(self) -> int:
        return await self.prem_repo.cleanup_expired()
