from __future__ import annotations

from typing import Optional

from motor.motor_asyncio import AsyncIOMotorDatabase

from bot.database.models.game_config import GameConfigModel


DEFAULT_GAME_CONFIGS = {
    "dart": {"cooldown_seconds": 60, "min_bet": 10, "max_bet": 10000, "multiplier": 3.0, "house_edge": 0.05, "win_chance": 0.33, "daily_limit": 100},
    "bowling": {"cooldown_seconds": 60, "min_bet": 10, "max_bet": 10000, "multiplier": 5.0, "house_edge": 0.08, "win_chance": 0.2, "daily_limit": 100},
    "basketball": {"cooldown_seconds": 60, "min_bet": 10, "max_bet": 10000, "multiplier": 4.0, "house_edge": 0.06, "win_chance": 0.25, "daily_limit": 100},
    "football": {"cooldown_seconds": 60, "min_bet": 10, "max_bet": 10000, "multiplier": 3.5, "house_edge": 0.05, "win_chance": 0.28, "daily_limit": 100},
    "dice_roll": {"cooldown_seconds": 60, "min_bet": 10, "max_bet": 50000, "multiplier": 2.0, "house_edge": 0.05, "win_chance": 0.5, "daily_limit": 200},
    "slots": {"cooldown_seconds": 90, "min_bet": 10, "max_bet": 50000, "multiplier": 5.0, "house_edge": 0.1, "win_chance": 0.15, "daily_limit": 150},
    "mines": {"cooldown_seconds": 120, "min_bet": 10, "max_bet": 50000, "multiplier": 3.0, "house_edge": 0.03, "win_chance": 0.4, "daily_limit": 100},
    "bet_roll": {"cooldown_seconds": 60, "min_bet": 10, "max_bet": 25000, "multiplier": 2.0, "house_edge": 0.05, "win_chance": 0.5, "daily_limit": 200},
    "high_low": {"cooldown_seconds": 60, "min_bet": 10, "max_bet": 25000, "multiplier": 2.0, "house_edge": 0.05, "win_chance": 0.5, "daily_limit": 200},
    "coinflip": {"cooldown_seconds": 60, "min_bet": 10, "max_bet": 50000, "multiplier": 2.0, "house_edge": 0.0, "win_chance": 0.5, "daily_limit": 200},
    "blackjack": {"cooldown_seconds": 60, "min_bet": 10, "max_bet": 50000, "multiplier": 2.0, "house_edge": 0.02, "win_chance": 0.48, "daily_limit": 100},
    "roulette": {"cooldown_seconds": 60, "min_bet": 10, "max_bet": 50000, "multiplier": 2.0, "house_edge": 0.027, "win_chance": 0.486, "daily_limit": 100},
    "crash": {"cooldown_seconds": 60, "min_bet": 10, "max_bet": 50000, "multiplier": 2.0, "house_edge": 0.05, "win_chance": 0.45, "daily_limit": 100},
    "wheel": {"cooldown_seconds": 90, "min_bet": 10, "max_bet": 25000, "multiplier": 3.0, "house_edge": 0.08, "win_chance": 0.3, "daily_limit": 100},
    "treasure_box": {"cooldown_seconds": 120, "min_bet": 10, "max_bet": 25000, "multiplier": 4.0, "house_edge": 0.1, "win_chance": 0.25, "daily_limit": 50},
    "lucky_card": {"cooldown_seconds": 60, "min_bet": 10, "max_bet": 25000, "multiplier": 2.5, "house_edge": 0.07, "win_chance": 0.4, "daily_limit": 100},
    "number_guess": {"cooldown_seconds": 60, "min_bet": 10, "max_bet": 10000, "multiplier": 6.0, "house_edge": 0.05, "win_chance": 0.167, "daily_limit": 100},
}


class GameConfigRepository:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.collection = db.game_configs

    async def get_config(self, game_type: str) -> Optional[GameConfigModel]:
        doc = await self.collection.find_one({"game_type": game_type})
        return GameConfigModel.from_doc(doc)

    async def get_or_create(self, game_type: str) -> GameConfigModel:
        config = await self.get_config(game_type)
        if config is None:
            defaults = DEFAULT_GAME_CONFIGS.get(game_type, {})
            config = GameConfigModel(game_type=game_type, **defaults)
            await self.collection.insert_one(config.to_dict())
        return config

    async def set_cooldown(self, game_type: str, seconds: int, updated_by: int = 0) -> None:
        await self.collection.update_one(
            {"game_type": game_type},
            {"$set": {"cooldown_seconds": seconds, "updated_by": updated_by}},
            upsert=True,
        )

    async def set_difficulty(self, game_type: str, difficulty: str, updated_by: int = 0) -> None:
        difficulty_settings = {
            "easy": {"win_chance": 0.6, "multiplier": 1.5, "house_edge": 0.02},
            "normal": {"win_chance": 0.5, "multiplier": 2.0, "house_edge": 0.05},
            "hard": {"win_chance": 0.35, "multiplier": 3.0, "house_edge": 0.1},
            "impossible": {"win_chance": 0.1, "multiplier": 10.0, "house_edge": 0.2},
        }
        settings = difficulty_settings.get(difficulty, difficulty_settings["normal"])
        await self.collection.update_one(
            {"game_type": game_type},
            {"$set": {**settings, "difficulty": difficulty, "updated_by": updated_by}},
            upsert=True,
        )

    async def set_multiplier(self, game_type: str, multiplier: float, updated_by: int = 0) -> None:
        await self.collection.update_one(
            {"game_type": game_type},
            {"$set": {"multiplier": multiplier, "updated_by": updated_by}},
            upsert=True,
        )

    async def set_house_edge(self, game_type: str, edge: float, updated_by: int = 0) -> None:
        await self.collection.update_one(
            {"game_type": game_type},
            {"$set": {"house_edge": edge, "updated_by": updated_by}},
            upsert=True,
        )

    async def set_reward(self, game_type: str, xp: int = 0, coins: int = 0, bonus: int = 0, updated_by: int = 0) -> None:
        await self.collection.update_one(
            {"game_type": game_type},
            {"$set": {"xp_reward": xp, "coins_reward": coins, "bonus_reward": bonus, "updated_by": updated_by}},
            upsert=True,
        )

    async def set_daily_limit(self, game_type: str, limit: int, updated_by: int = 0) -> None:
        await self.collection.update_one(
            {"game_type": game_type},
            {"$set": {"daily_limit": limit, "updated_by": updated_by}},
            upsert=True,
        )

    async def set_bet_limit(self, game_type: str, min_bet: int = None, max_bet: int = None, updated_by: int = 0) -> None:
        update = {"updated_by": updated_by}
        if min_bet is not None:
            update["min_bet"] = min_bet
        if max_bet is not None:
            update["max_bet"] = max_bet
        await self.collection.update_one(
            {"game_type": game_type},
            {"$set": update},
            upsert=True,
        )

    async def set_enabled(self, game_type: str, enabled: bool, updated_by: int = 0) -> None:
        await self.collection.update_one(
            {"game_type": game_type},
            {"$set": {"is_enabled": enabled, "updated_by": updated_by}},
            upsert=True,
        )

    async def get_all_configs(self) -> list[GameConfigModel]:
        cursor = self.collection.find({})
        docs = await cursor.to_list(length=None)
        return [GameConfigModel.from_doc(d) for d in docs]

    async def seed_defaults(self) -> None:
        for game_type, defaults in DEFAULT_GAME_CONFIGS.items():
            existing = await self.get_config(game_type)
            if not existing:
                config = GameConfigModel(game_type=game_type, **defaults)
                await self.collection.insert_one(config.to_dict())
