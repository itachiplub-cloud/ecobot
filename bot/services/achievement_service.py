from __future__ import annotations

from motor.motor_asyncio import AsyncIOMotorDatabase

from bot.database.repositories.achievement_repo import AchievementRepository

ACHIEVEMENTS = {
    "first_work": {"name": "First Job", "description": "Complete your first work", "max": 1, "reward": 100},
    "work_100": {"name": "Workaholic", "description": "Work 100 times", "max": 100, "reward": 1000},
    "work_1000": {"name": "Legendary Worker", "description": "Work 1000 times", "max": 1000, "reward": 10000},
    "crime_10": {"name": "Petty Criminal", "description": "Commit 10 crimes", "max": 10, "reward": 500},
    "crime_100": {"name": "Crime Lord", "description": "Commit 100 crimes", "max": 100, "reward": 5000},
    "earn_10000": {"name": "Wealthy", "description": "Earn 10,000 coins total", "max": 10000, "reward": 500},
    "earn_100000": {"name": "Rich", "description": "Earn 100,000 coins total", "max": 100000, "reward": 2000},
    "earn_1000000": {"name": "Millionaire", "description": "Earn 1,000,000 coins total", "max": 1000000, "reward": 10000},
    "level_10": {"name": "Rising Star", "description": "Reach level 10", "max": 10, "reward": 500},
    "level_50": {"name": "Veteran", "description": "Reach level 50", "max": 50, "reward": 2500},
    "level_100": {"name": "Legend", "description": "Reach level 100", "max": 100, "reward": 10000},
    "boss_10": {"name": "Boss Hunter", "description": "Defeat 10 bosses", "max": 10, "reward": 2000},
    "boss_50": {"name": "Boss Slayer", "description": "Defeat 50 bosses", "max": 50, "reward": 10000},
    "games_10": {"name": "Gamer", "description": "Play 10 games", "max": 10, "reward": 300},
    "games_100": {"name": "Addicted", "description": "Play 100 games", "max": 100, "reward": 3000},
    "daily_7": {"name": "Daily Devotee", "description": "7-day daily streak", "max": 7, "reward": 500},
    "daily_30": {"name": "Monthly Master", "description": "30-day daily streak", "max": 30, "reward": 5000},
    "pet_1": {"name": "Pet Owner", "description": "Own your first pet", "max": 1, "reward": 200},
    "pet_10": {"name": "Zookeeper", "description": "Own 10 pets", "max": 10, "reward": 2000},
    "quest_10": {"name": "Quester", "description": "Complete 10 quests", "max": 10, "reward": 500},
    "quest_50": {"name": "Quest Master", "description": "Complete 50 quests", "max": 50, "reward": 5000},
    "guild_create": {"name": "Guild Leader", "description": "Create a guild", "max": 1, "reward": 1000},
    "fish_50": {"name": "Angler", "description": "Fish 50 times", "max": 50, "reward": 1000},
    "mine_50": {"name": "Miner", "description": "Mine 50 times", "max": 50, "reward": 1000},
    "heist_win": {"name": "Heist Master", "description": "Win a heist", "max": 1, "reward": 500},
    "pvp_10": {"name": "Warrior", "description": "Win 10 PvP battles", "max": 10, "reward": 2000},
    "market_trade": {"name": "Trader", "description": "Complete a market trade", "max": 1, "reward": 300},
}


class AchievementService:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.ach_repo = AchievementRepository(db)

    async def check_achievement(self, user_id: int, achievement_id: str, progress: int = 1) -> dict:
        ach = ACHIEVEMENTS.get(achievement_id)
        if not ach:
            return {"unlocked": False}
        result = await self.ach_repo.update_progress(user_id, achievement_id, progress)
        if result["newly_unlocked"]:
            return {"unlocked": True, "name": ach["name"], "description": ach["description"], "reward": ach["reward"]}
        return {"unlocked": False}

    async def get_user_achievements(self, user_id: int):
        return await self.ach_repo.get_user_achievements(user_id)

    async def get_completed_count(self, user_id: int) -> int:
        return await self.ach_repo.get_completed_count(user_id)

    async def get_achievement_info(self, achievement_id: str) -> dict:
        return ACHIEVEMENTS.get(achievement_id, {})

    async def get_all_achievements(self) -> dict:
        return ACHIEVEMENTS

    async def is_unlocked(self, user_id: int, achievement_id: str) -> bool:
        return await self.ach_repo.is_unlocked(user_id, achievement_id)

    async def claim_reward(self, user_id: int, achievement_id: str) -> dict:
        ach = ACHIEVEMENTS.get(achievement_id)
        if not ach:
            return {"success": False}
        result = await self.ach_repo.claim_reward(user_id, achievement_id)
        if result:
            return {"success": True, "reward": ach["reward"], "name": ach["name"]}
        return {"success": False, "reason": "not_claimable"}
