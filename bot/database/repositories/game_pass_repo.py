from __future__ import annotations

from datetime import datetime, timezone
from typing import Optional

from motor.motor_asyncio import AsyncIOMotorDatabase

from bot.database.models.investment import GamePassModel


class GamePassRepository:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.collection = db.game_pass

    async def get_pass(self, user_id: int, season: int = 1) -> Optional[GamePassModel]:
        doc = await self.collection.find_one({"user_id": user_id, "season": season})
        return GamePassModel.from_doc(doc)

    async def get_or_create(self, user_id: int, season: int = 1) -> GamePassModel:
        gp = await self.get_pass(user_id, season)
        if gp is None:
            gp = GamePassModel(user_id=user_id, season=season)
            await self.collection.insert_one(gp.to_dict())
        return gp

    async def add_xp(self, user_id: int, xp: int, season: int = 1) -> dict:
        gp = await self.get_or_create(user_id, season)
        gp.xp += xp
        tiered_up = False
        while gp.xp >= gp.xp_needed and gp.tier < 100:
            gp.xp -= gp.xp_needed
            gp.tier += 1
            gp.xp_needed = int(gp.xp_needed * 1.15)
            tiered_up = True
            gp.unlocked_rewards.append(gp.tier)
        await self.collection.update_one(
            {"user_id": user_id, "season": season},
            {"$set": {
                "xp": gp.xp, "tier": gp.tier, "xp_needed": gp.xp_needed,
                "unlocked_rewards": gp.unlocked_rewards, "updated_at": datetime.now(timezone.utc),
            }},
        )
        return {"tiered_up": tiered_up, "new_tier": gp.tier}

    async def claim_reward(self, user_id: int, tier: int, season: int = 1) -> bool:
        gp = await self.get_or_create(user_id, season)
        if tier in gp.claimed_rewards or tier not in gp.unlocked_rewards:
            return False
        await self.collection.update_one(
            {"user_id": user_id, "season": season},
            {"$push": {"claimed_rewards": tier}},
        )
        return True

    async def upgrade_premium(self, user_id: int, season: int = 1) -> bool:
        result = await self.collection.update_one(
            {"user_id": user_id, "season": season},
            {"$set": {"premium": True}},
        )
        return result.modified_count > 0

    async def complete_daily_mission(self, user_id: int, mission_id: str, season: int = 1) -> bool:
        gp = await self.get_or_create(user_id, season)
        if mission_id in gp.daily_missions_completed:
            return False
        await self.collection.update_one(
            {"user_id": user_id, "season": season},
            {"$push": {"daily_missions_completed": mission_id}},
        )
        return True

    async def complete_weekly_mission(self, user_id: int, mission_id: str, season: int = 1) -> bool:
        gp = await self.get_or_create(user_id, season)
        if mission_id in gp.weekly_missions_completed:
            return False
        await self.collection.update_one(
            {"user_id": user_id, "season": season},
            {"$push": {"weekly_missions_completed": mission_id}},
        )
        return True

    async def reset_daily_missions(self, season: int = 1) -> int:
        result = await self.collection.update_many(
            {"season": season},
            {"$set": {"daily_missions_completed": []}},
        )
        return result.modified_count

    async def get_top_players(self, season: int = 1, limit: int = 10) -> list[GamePassModel]:
        cursor = self.collection.find({"season": season}).sort("tier", -1).limit(limit)
        docs = await cursor.to_list(length=limit)
        return [GamePassModel.from_doc(d) for d in docs]
