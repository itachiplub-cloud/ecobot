from __future__ import annotations

from motor.motor_asyncio import AsyncIOMotorDatabase

from bot.database.repositories.battle_pass_repo import BattlePassRepository


class BattlePassService:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.bp_repo = BattlePassRepository(db)

    async def get_battle_pass(self, user_id: int, season: int = 1):
        return await self.bp_repo.get_or_create(user_id, season)

    async def add_xp(self, user_id: int, xp: int, season: int = 1) -> dict:
        return await self.bp_repo.add_xp(user_id, xp, season)

    async def claim_reward(self, user_id: int, tier: int, season: int = 1) -> bool:
        return await self.bp_repo.claim_reward(user_id, tier, season)

    async def upgrade_premium(self, user_id: int, season: int = 1) -> bool:
        return await self.bp_repo.upgrade_premium(user_id, season)

    async def get_top_players(self, season: int = 1, limit: int = 10):
        return await self.bp_repo.get_top_players(season, limit)
