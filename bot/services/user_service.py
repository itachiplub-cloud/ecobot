from __future__ import annotations

from motor.motor_asyncio import AsyncIOMotorDatabase

from bot.database.repositories.user_repo import UserRepository
from bot.database.models.user import UserModel


class UserService:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.user_repo = UserRepository(db)

    async def get_user(self, user_id: int) -> UserModel:
        return await self.user_repo.get_user(user_id)

    async def get_or_create(self, user_id: int, **kwargs) -> UserModel:
        return await self.user_repo.get_or_create(user_id, **kwargs)

    async def update_user(self, user_id: int, **data) -> None:
        await self.user_repo.update_user(user_id, **data)

    async def add_xp(self, user_id: int, xp: int) -> dict:
        return await self.user_repo.add_xp(user_id, xp)

    async def update_stats(self, user_id: int, stats: dict) -> None:
        await self.user_repo.update_stats(user_id, stats)

    async def increment_field(self, user_id: int, field: str, amount: int = 1) -> None:
        await self.user_repo.increment_field(user_id, field, amount)

    async def get_top_users(self, field: str, limit: int = 10) -> list:
        return await self.user_repo.get_top_users(field, limit)

    async def count_users(self) -> int:
        return await self.user_repo.count_users()

    async def ban_user(self, user_id: int, reason: str = "") -> None:
        await self.user_repo.ban_user(user_id, reason)

    async def unban_user(self, user_id: int) -> None:
        await self.user_repo.unban_user(user_id)

    async def search_users(self, query: str, limit: int = 20) -> list:
        return await self.user_repo.search_users(query, limit)

    async def is_owner(self, user_id: int) -> bool:
        from config import settings
        return user_id == settings.OWNER_ID

    async def is_banned(self, user_id: int) -> bool:
        user = await self.user_repo.get_user(user_id)
        return user.is_banned if user else False
