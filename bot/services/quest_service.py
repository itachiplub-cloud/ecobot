from __future__ import annotations

import random
from motor.motor_asyncio import AsyncIOMotorDatabase

from bot.database.repositories.quest_repo import QuestRepository
from bot.database.models.quest import QuestModel


class QuestService:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.quest_repo = QuestRepository(db)

    async def get_user_quests(self, user_id: int, quest_type: str = None):
        return await self.quest_repo.get_user_quests(user_id, quest_type)

    async def assign_quest(self, user_id: int, quest_type: str = "daily") -> QuestModel:
        quests = self._get_quest_templates(quest_type)
        template = random.choice(quests)
        quest = QuestModel(
            user_id=user_id,
            quest_id=template["id"],
            quest_type=quest_type,
            title=template["title"],
            description=template["description"],
            objectives=template["objectives"],
            reward_xp=template["reward_xp"],
            reward_coins=template["reward_coins"],
        )
        return await self.quest_repo.add_quest(quest)

    async def update_progress(self, user_id: int, quest_id: str, objective: str, amount: int = 1) -> dict:
        return await self.quest_repo.update_quest_progress(user_id, quest_id, objective, amount)

    async def claim_reward(self, user_id: int, quest_id: str) -> dict:
        quest = await self.quest_repo.get_quest(user_id, quest_id)
        if not quest:
            return {"success": False, "reason": "quest_not_found"}
        if not quest.completed:
            return {"success": False, "reason": "not_completed"}
        if quest.claimed:
            return {"success": False, "reason": "already_claimed"}
        await self.quest_repo.claim_quest(user_id, quest_id)
        return {
            "success": True,
            "reward_xp": quest.reward_xp,
            "reward_coins": quest.reward_coins,
            "reward_items": quest.reward_items,
        }

    async def cleanup_expired(self) -> int:
        return await self.quest_repo.cleanup_expired()

    async def assign_daily_quests(self, user_id: int, count: int = 3) -> list:
        quests = []
        for _ in range(count):
            q = await self.assign_quest(user_id, "daily")
            quests.append(q)
        return quests

    async def assign_weekly_quests(self, user_id: int, count: int = 5) -> list:
        quests = []
        for _ in range(count):
            q = await self.assign_quest(user_id, "weekly")
            quests.append(q)
        return quests

    async def count_active(self, user_id: int) -> int:
        return await self.quest_repo.count_active(user_id)

    def _get_quest_templates(self, quest_type: str) -> list[dict]:
        templates = {
            "daily": [
                {"id": "d_work_3", "title": "Hard Worker", "description": "Work 3 times", "objectives": [{"id": "work", "target": 3}], "reward_xp": 50, "reward_coins": 200},
                {"id": "d_earn_500", "title": "Money Maker", "description": "Earn 500 coins", "objectives": [{"id": "earn", "target": 500}], "reward_xp": 30, "reward_coins": 150},
                {"id": "d_play_2", "title": "Game Night", "description": "Play 2 games", "objectives": [{"id": "play_game", "target": 2}], "reward_xp": 40, "reward_coins": 100},
                {"id": "d_crime_1", "title": "Quick Heist", "description": "Commit 1 crime", "objectives": [{"id": "crime", "target": 1}], "reward_xp": 35, "reward_coins": 120},
                {"id": "d_fish_5", "title": "Gone Fishing", "description": "Fish 5 times", "objectives": [{"id": "fish", "target": 5}], "reward_xp": 45, "reward_coins": 180},
                {"id": "d_mine_5", "title": "Miner", "description": "Mine 5 times", "objectives": [{"id": "mine", "target": 5}], "reward_xp": 45, "reward_coins": 180},
                {"id": "d_daily", "title": "Daily Devotee", "description": "Claim your daily reward", "objectives": [{"id": "daily_claim", "target": 1}], "reward_xp": 20, "reward_coins": 100},
            ],
            "weekly": [
                {"id": "w_earn_5000", "title": "Tycoon", "description": "Earn 5000 coins this week", "objectives": [{"id": "earn", "target": 5000}], "reward_xp": 200, "reward_coins": 1000},
                {"id": "w_boss_3", "title": "Boss Slayer", "description": "Defeat 3 bosses", "objectives": [{"id": "boss_defeat", "target": 3}], "reward_xp": 300, "reward_coins": 1500},
                {"id": "w_work_20", "title": "Workaholic", "description": "Work 20 times", "objectives": [{"id": "work", "target": 20}], "reward_xp": 250, "reward_coins": 1200},
                {"id": "w_pet_feed_7", "title": "Pet Lover", "description": "Feed your pet 7 times", "objectives": [{"id": "pet_feed", "target": 7}], "reward_xp": 150, "reward_coins": 800},
                {"id": "w_play_10", "title": "Gamer", "description": "Play 10 games", "objectives": [{"id": "play_game", "target": 10}], "reward_xp": 200, "reward_coins": 1000},
            ],
            "monthly": [
                {"id": "m_earn_50000", "title": "Millionaire Dream", "description": "Earn 50000 coins this month", "objectives": [{"id": "earn", "target": 50000}], "reward_xp": 1000, "reward_coins": 5000},
                {"id": "m_dungeon_5", "title": "Dungeon Explorer", "description": "Complete 5 dungeons", "objectives": [{"id": "dungeon_clear", "target": 5}], "reward_xp": 800, "reward_coins": 4000},
                {"id": "m_level_10", "title": "Level Up", "description": "Gain 10 levels", "objectives": [{"id": "level_up", "target": 10}], "reward_xp": 500, "reward_coins": 3000},
            ],
        }
        return templates.get(quest_type, templates["daily"])
