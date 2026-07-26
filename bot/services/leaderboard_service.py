from __future__ import annotations

from motor.motor_asyncio import AsyncIOMotorDatabase

from bot.database.repositories.leaderboard_repo import LeaderboardRepository


class LeaderboardService:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.lb_repo = LeaderboardRepository(db)

    async def update_score(self, user_id: int, category: str, score: int) -> None:
        await self.lb_repo.update_score(user_id, category, score)

    async def increment_score(self, user_id: int, category: str, amount: int) -> None:
        await self.lb_repo.increment_score(user_id, category, amount)

    async def get_top(self, category: str, limit: int = 10):
        return await self.lb_repo.get_top(category, limit)

    async def get_rank(self, user_id: int, category: str) -> int | None:
        return await self.lb_repo.get_rank(user_id, category)

    async def get_score(self, user_id: int, category: str) -> int:
        return await self.lb_repo.get_score(user_id, category)

    async def get_categories(self) -> list[str]:
        return await self.lb_repo.get_categories()
