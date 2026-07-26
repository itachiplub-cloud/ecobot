from __future__ import annotations

import random
from datetime import datetime
from motor.motor_asyncio import AsyncIOMotorDatabase

from bot.database.repositories.game_stats_repo import GameStatsRepository
from bot.database.repositories.game_history_repo import GameHistoryRepository
from bot.database.repositories.game_config_repo import GameConfigRepository, DEFAULT_GAME_CONFIGS
from bot.database.repositories.economy_repo import EconomyRepository
from bot.database.models.game_history import GameHistoryModel


class GameService:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.stats_repo = GameStatsRepository(db)
        self.history_repo = GameHistoryRepository(db)
        self.config_repo = GameConfigRepository(db)
        self.econ_repo = EconomyRepository(db)

    async def get_config(self, game_type: str) -> dict:
        config = await self.config_repo.get_or_create(game_type)
        return config

    async def play_game(self, user_id: int, game_type: str, bet: int, won: bool, payout: int, chat_id: int = None, chat_type: str = "private", **metadata) -> dict:
        config = await self.config_repo.get_or_create(game_type)
        if not config.is_enabled:
            return {"success": False, "reason": "game_disabled"}
        if bet < config.min_bet or bet > config.max_bet:
            return {"success": False, "reason": "invalid_bet", "min": config.min_bet, "max": config.max_bet}
        eco = await self.econ_repo.get_economy(user_id)
        if not eco or eco.wallet < bet:
            return {"success": False, "reason": "insufficient_funds"}
        daily_count = await self.history_repo.get_game_count(user_id, game_type, within_hours=24)
        if daily_count >= config.daily_limit:
            return {"success": False, "reason": "daily_limit", "limit": config.daily_limit}
        if won:
            await self.econ_repo.add_coins(user_id, payout, f"Game win: {game_type}")
        else:
            await self.econ_repo.remove_coins(user_id, bet)
        stats = await self.stats_repo.record_game(user_id, game_type, won, bet, payout)
        await self.stats_repo.update_streaks(user_id)
        history = GameHistoryModel(
            user_id=user_id, game_type=game_type, bet_amount=bet,
            result="win" if won else "lose", won=won, payout=payout if won else 0,
            multiplier=config.multiplier, chat_id=chat_id, chat_type=chat_type,
            metadata=metadata,
        )
        await self.history_repo.add_history(history)
        return {
            "success": True, "won": won, "payout": payout if won else 0,
            "wallet": eco.wallet - bet + (payout if won else 0),
            "stats": stats,
            "xp_reward": config.xp_reward if won else 0,
            "daily_remaining": config.daily_limit - daily_count - 1,
        }

    async def check_cooldown(self, user_id: int, game_type: str) -> tuple[bool, int]:
        config = await self.config_repo.get_or_create(game_type)
        from bot.database.repositories.cooldown_repo import CooldownRepository
        cd_repo = CooldownRepository(self.stats_repo.collection.database)
        on_cd, remaining = await cd_repo.is_on_cooldown(user_id, f"game_{game_type}")
        return on_cd, remaining

    async def set_cooldown(self, user_id: int, game_type: str) -> None:
        config = await self.config_repo.get_or_create(game_type)
        from bot.database.repositories.cooldown_repo import CooldownRepository
        cd_repo = CooldownRepository(self.stats_repo.collection.database)
        await cd_repo.set_cooldown(user_id, f"game_{game_type}", config.cooldown_seconds)

    async def get_stats(self, user_id: int):
        return await self.stats_repo.get_or_create(user_id)

    async def get_history(self, user_id: int, game_type: str = None, limit: int = 20):
        return await self.history_repo.get_user_history(user_id, game_type, limit)

    async def get_daily_volume(self, user_id: int) -> int:
        return await self.history_repo.get_daily_volume(user_id)

    async def set_cooldown_config(self, game_type: str, seconds: int, updated_by: int = 0) -> None:
        await self.config_repo.set_cooldown(game_type, seconds, updated_by)

    async def set_difficulty(self, game_type: str, difficulty: str, updated_by: int = 0) -> None:
        await self.config_repo.set_difficulty(game_type, difficulty, updated_by)

    async def set_multiplier(self, game_type: str, multiplier: float, updated_by: int = 0) -> None:
        await self.config_repo.set_multiplier(game_type, multiplier, updated_by)

    async def set_house_edge(self, game_type: str, edge: float, updated_by: int = 0) -> None:
        await self.config_repo.set_house_edge(game_type, edge, updated_by)

    async def set_reward(self, game_type: str, xp: int = 0, coins: int = 0, updated_by: int = 0) -> None:
        await self.config_repo.set_reward(game_type, xp, coins, updated_by=updated_by)

    async def set_daily_limit(self, game_type: str, limit: int, updated_by: int = 0) -> None:
        await self.config_repo.set_daily_limit(game_type, limit, updated_by)

    async def set_bet_limit(self, game_type: str, min_bet: int = None, max_bet: int = None, updated_by: int = 0) -> None:
        await self.config_repo.set_bet_limit(game_type, min_bet, max_bet, updated_by)

    async def set_enabled(self, game_type: str, enabled: bool, updated_by: int = 0) -> None:
        await self.config_repo.set_enabled(game_type, enabled, updated_by)

    async def reset_stats(self, user_id: int) -> None:
        await self.stats_repo.reset_stats(user_id)

    async def reset_all_stats(self) -> None:
        await self.stats_repo.reset_all_stats()

    def telegram_dice_result(self, emoji: str, value: int) -> dict:
        dart_scores = {1: 1, 2: 2, 3: 3, 4: 4, 5: 5, 6: 6}
        if emoji == "🎯":
            score = dart_scores.get(value, value)
            return {"score": score, "display": f"🎯 Scored {score}!"}
        elif emoji == "🎳":
            return {"score": value, "display": f"🎳 Pins knocked: {value}!"}
        elif emoji == "🏀":
            return {"score": value, "display": f"🏀 Scored {value}!"}
        elif emoji == "⚽":
            return {"score": value, "display": f"⚽ Scored {value}!"}
        elif emoji == "🎰":
            return {"score": value, "display": f"🎰 Slot result: {value}!"}
        elif emoji == "🎲":
            return {"score": value, "display": f"🎲 Rolled: {value}!"}
        return {"score": value, "display": f"{emoji} Result: {value}!"}

    async def seed_configs(self) -> None:
        await self.config_repo.seed_defaults()
