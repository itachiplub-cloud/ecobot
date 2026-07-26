from __future__ import annotations

from motor.motor_asyncio import AsyncIOMotorDatabase

from bot.database.repositories.statistics_repo import StatisticsRepository


class StatisticsService:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.stats_repo = StatisticsRepository(db)

    async def increment(self, field: str, amount: int = 1) -> None:
        await self.stats_repo.increment(field, amount)

    async def get_today(self):
        return await self.stats_repo.get_today()

    async def get_range(self, start_date, end_date):
        return await self.stats_repo.get_range(start_date, end_date)

    async def get_total(self, field: str) -> int:
        return await self.stats_repo.get_total(field)
