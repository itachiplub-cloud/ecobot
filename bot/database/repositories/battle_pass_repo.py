from __future__ import annotations

from datetime import datetime
from typing import Optional

from motor.motor_asyncio import AsyncIOMotorDatabase

from bot.database.models.battle_pass import BattlePassModel


class BattlePassRepository:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.collection = db.battle_pass

    async def get_battle_pass(self, user_id: int, season: int = 1) -> Optional[BattlePassModel]:
        doc = await self.collection.find_one({"user_id": user_id, "season": season})
        return BattlePassModel.from_doc(doc)

    async def get_or_create(self, user_id: int, season: int = 1) -> BattlePassModel:
        bp = await self.get_battle_pass(user_id, season)
        if bp is None:
            bp = BattlePassModel(user_id=user_id, season=season)
            await self.collection.insert_one(bp.to_dict())
        return bp

    async def add_xp(self, user_id: int, xp: int, season: int = 1) -> dict:
        bp = await self.get_or_create(user_id, season)
        bp.xp += xp
        bp.total_xp_earned += xp
        tiered_up = False
        while bp.xp >= bp.xp_needed and bp.tier < 100:
            bp.xp -= bp.xp_needed
            bp.tier += 1
            bp.xp_needed = int(bp.xp_needed * 1.2)
            tiered_up = True
        await self.collection.update_one(
            {"user_id": user_id, "season": season},
            {"$set": {
                "xp": bp.xp,
                "tier": bp.tier,
                "xp_needed": bp.xp_needed,
                "total_xp_earned": bp.total_xp_earned,
                "updated_at": datetime.utcnow(),
            }},
        )
        return {"tiered_up": tiered_up, "new_tier": bp.tier}

    async def claim_reward(self, user_id: int, tier: int, season: int = 1) -> bool:
        bp = await self.get_or_create(user_id, season)
        if tier in bp.claimed_rewards or tier not in bp.unlocked_tiers:
            return False
        await self.collection.update_one(
            {"user_id": user_id, "season": season},
            {"$push": {"claimed_rewards": tier}},
        )
        return True

    async def unlock_tier(self, user_id: int, tier: int, season: int = 1) -> bool:
        bp = await self.get_or_create(user_id, season)
        if tier not in bp.unlocked_tiers:
            await self.collection.update_one(
                {"user_id": user_id, "season": season},
                {"$push": {"unlocked_tiers": tier}},
            )
            return True
        return False

    async def upgrade_premium(self, user_id: int, season: int = 1) -> bool:
        result = await self.collection.update_one(
            {"user_id": user_id, "season": season},
            {"$set": {"premium": True}},
        )
        return result.modified_count > 0

    async def get_top_players(self, season: int = 1, limit: int = 10) -> list[BattlePassModel]:
        cursor = self.collection.find({"season": season}).sort("tier", -1).limit(limit)
        docs = await cursor.to_list(length=limit)
        return [BattlePassModel.from_doc(d) for d in docs]
