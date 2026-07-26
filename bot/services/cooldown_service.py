from __future__ import annotations

from motor.motor_asyncio import AsyncIOMotorDatabase

from bot.database.repositories.cooldown_repo import CooldownRepository


class CooldownService:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.cooldown_repo = CooldownRepository(db)

    async def set_cooldown(self, user_id: int, action: str, seconds: int) -> None:
        await self.cooldown_repo.set_cooldown(user_id, action, seconds)

    async def is_on_cooldown(self, user_id: int, action: str) -> tuple[bool, int]:
        return await self.cooldown_repo.is_on_cooldown(user_id, action)

    async def clear_cooldown(self, user_id: int, action: str) -> None:
        await self.cooldown_repo.clear_cooldown(user_id, action)

    async def clear_all(self, user_id: int) -> None:
        await self.cooldown_repo.clear_all_cooldowns(user_id)

    async def cleanup(self) -> int:
        return await self.cooldown_repo.cleanup_expired()

    def format_time(self, seconds: int) -> str:
        hours = seconds // 3600
        minutes = (seconds % 3600) // 60
        secs = seconds % 60
        if hours > 0:
            return f"{hours}h {minutes}m {secs}s"
        if minutes > 0:
            return f"{minutes}m {secs}s"
        return f"{secs}s"
