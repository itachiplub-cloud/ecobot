from __future__ import annotations

from motor.motor_asyncio import AsyncIOMotorDatabase

from bot.database.repositories.group_ranking_repo import GroupRankingRepository


class GroupRankingService:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.repo = GroupRankingRepository(db)

    async def track_message(self, user_id: int, group_id: int) -> None:
        await self.repo.update_activity(user_id, group_id, xp=5, messages=1)

    async def track_game(self, user_id: int, group_id: int, coins: int = 0) -> None:
        await self.repo.update_activity(user_id, group_id, xp=10, coins=coins, games=1)

    async def track_work(self, user_id: int, group_id: int, coins: int = 0) -> None:
        await self.repo.update_activity(user_id, group_id, xp=8, coins=coins)

    async def get_group_top(self, group_id: int, category: str = "xp_earned", limit: int = 10):
        return await self.repo.get_group_top(group_id, category, limit)

    async def get_user_rank(self, user_id: int, group_id: int, category: str = "xp_earned"):
        return await self.repo.get_user_rank(user_id, group_id, category)

    async def get_user_stats(self, user_id: int, group_id: int):
        return await self.repo.get_user_stats(user_id, group_id)

    async def get_global_top(self, category: str = "xp_earned", limit: int = 10):
        return await self.repo.get_global_top(category, limit)

    async def get_all_groups(self) -> list[int]:
        return await self.repo.get_all_groups()

    async def get_group_member_count(self, group_id: int) -> int:
        return await self.repo.get_group_member_count(group_id)

    async def reset_group(self, group_id: int) -> None:
        await self.repo.reset_group(group_id)
