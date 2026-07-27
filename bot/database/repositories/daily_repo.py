from __future__ import annotations

from datetime import datetime, timezone
from typing import Optional

from motor.motor_asyncio import AsyncIOMotorDatabase

from bot.database.models.daily import DailyRewardModel


class DailyRepository:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.collection = db.daily_rewards

    async def get_daily(self, user_id: int) -> Optional[DailyRewardModel]:
        doc = await self.collection.find_one({"user_id": user_id})
        return DailyRewardModel.from_doc(doc)

    async def get_or_create(self, user_id: int) -> DailyRewardModel:
        daily = await self.get_daily(user_id)
        if daily is None:
            daily = DailyRewardModel(user_id=user_id)
            await self.collection.insert_one(daily.to_dict())
        return daily

    async def claim_daily(self, user_id: int) -> dict:
        daily = await self.get_or_create(user_id)
        now = datetime.now(timezone.utc)
        if daily.last_daily:
            diff = (now - daily.last_daily).total_seconds()
            if diff < 82800:
                remaining = 82800 - diff
                hours = int(remaining // 3600)
                minutes = int((remaining % 3600) // 60)
                return {
                    "claimed": False,
                    "hours": hours,
                    "minutes": minutes,
                }
        daily.daily_streak += 1
        if daily.daily_streak > daily.best_streak:
            daily.best_streak = daily.daily_streak
        daily.last_daily = now
        daily.total_claimed += 1
        await self.collection.update_one(
            {"user_id": user_id},
            {"$set": {
                "daily_streak": daily.daily_streak,
                "weekly_streak": daily.weekly_streak,
                "monthly_streak": daily.monthly_streak,
                "last_daily": daily.last_daily,
                "total_claimed": daily.total_claimed,
                "best_streak": daily.best_streak,
            }},
        )
        return {"claimed": True, "streak": daily.daily_streak}

    async def claim_weekly(self, user_id: int) -> dict:
        daily = await self.get_or_create(user_id)
        now = datetime.now(timezone.utc)
        if daily.last_weekly:
            diff = (now - daily.last_weekly).total_seconds()
            if diff < 604800:
                remaining = 604800 - diff
                days = int(remaining // 86400)
                hours = int((remaining % 86400) // 3600)
                return {"claimed": False, "days": days, "hours": hours}
        daily.weekly_streak += 1
        daily.last_weekly = now
        await self.collection.update_one(
            {"user_id": user_id},
            {"$set": {"weekly_streak": daily.weekly_streak, "last_weekly": daily.last_weekly}},
        )
        return {"claimed": True, "streak": daily.weekly_streak}

    async def claim_monthly(self, user_id: int) -> dict:
        daily = await self.get_or_create(user_id)
        now = datetime.now(timezone.utc)
        if daily.last_monthly:
            diff = (now - daily.last_monthly).total_seconds()
            if diff < 2592000:
                remaining = 2592000 - diff
                days = int(remaining // 86400)
                return {"claimed": False, "days": days}
        daily.monthly_streak += 1
        daily.last_monthly = now
        await self.collection.update_one(
            {"user_id": user_id},
            {"$set": {"monthly_streak": daily.monthly_streak, "last_monthly": daily.last_monthly}},
        )
        return {"claimed": True, "streak": daily.monthly_streak}

    async def claim_yearly(self, user_id: int) -> dict:
        daily = await self.get_or_create(user_id)
        now = datetime.now(timezone.utc)
        if daily.last_yearly:
            diff = (now - daily.last_yearly).total_seconds()
            if diff < 31536000:
                remaining = 31536000 - diff
                days = int(remaining // 86400)
                return {"claimed": False, "days": days}
        daily.yearly_streak += 1
        daily.last_yearly = now
        await self.collection.update_one(
            {"user_id": user_id},
            {"$set": {"yearly_streak": daily.yearly_streak, "last_yearly": daily.last_yearly}},
        )
        return {"claimed": True, "streak": daily.yearly_streak}
