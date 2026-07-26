from __future__ import annotations

from motor.motor_asyncio import AsyncIOMotorDatabase

from bot.database.repositories.daily_repo import DailyRepository
from config import settings


class DailyService:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.daily_repo = DailyRepository(db)

    async def claim_daily(self, user_id: int) -> dict:
        result = await self.daily_repo.claim_daily(user_id)
        if result["claimed"]:
            streak = result["streak"]
            base = settings.DAILY_REWARD
            bonus = min(streak, 30) * 10
            total = base + bonus
            result["amount"] = total
            result["streak_bonus"] = bonus
        return result

    async def claim_weekly(self, user_id: int) -> dict:
        result = await self.daily_repo.claim_weekly(user_id)
        if result["claimed"]:
            streak = result["streak"]
            base = settings.DAILY_REWARD * 5
            bonus = min(streak, 10) * 100
            total = base + bonus
            result["amount"] = total
            result["streak_bonus"] = bonus
        return result

    async def claim_monthly(self, user_id: int) -> dict:
        result = await self.daily_repo.claim_monthly(user_id)
        if result["claimed"]:
            streak = result["streak"]
            base = settings.DAILY_REWARD * 20
            bonus = min(streak, 12) * 500
            total = base + bonus
            result["amount"] = total
            result["streak_bonus"] = bonus
        return result

    async def claim_yearly(self, user_id: int) -> dict:
        result = await self.daily_repo.claim_yearly(user_id)
        if result["claimed"]:
            streak = result["streak"]
            base = settings.DAILY_REWARD * 100
            bonus = min(streak, 5) * 5000
            total = base + bonus
            result["amount"] = total
            result["streak_bonus"] = bonus
        return result

    async def get_streaks(self, user_id: int) -> dict:
        daily = await self.daily_repo.get_daily(user_id)
        if not daily:
            return {"daily": 0, "weekly": 0, "monthly": 0, "yearly": 0}
        return {
            "daily": daily.daily_streak,
            "weekly": daily.weekly_streak,
            "monthly": daily.monthly_streak,
            "yearly": daily.yearly_streak,
            "best": daily.best_streak,
        }
