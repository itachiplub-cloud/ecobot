from __future__ import annotations

from datetime import datetime, timedelta
from typing import Optional

from motor.motor_asyncio import AsyncIOMotorDatabase

from bot.database.models.game_stats import GameStatsModel


class GameStatsRepository:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.collection = db.game_stats

    async def get_stats(self, user_id: int) -> Optional[GameStatsModel]:
        doc = await self.collection.find_one({"user_id": user_id})
        return GameStatsModel.from_doc(doc)

    async def get_or_create(self, user_id: int) -> GameStatsModel:
        stats = await self.get_stats(user_id)
        if stats is None:
            stats = GameStatsModel(user_id=user_id)
            await self.collection.insert_one(stats.to_dict())
        return stats

    async def record_game(self, user_id: int, game_type: str, won: bool, bet: int, payout: int) -> GameStatsModel:
        stats = await self.get_or_create(user_id)
        now = datetime.utcnow()
        if stats.daily_reset and (now - stats.daily_reset).days >= 1:
            stats.daily_games = 0
            stats.daily_reset = now
        if stats.weekly_reset and (now - stats.weekly_reset).days >= 7:
            stats.weekly_games = 0
            stats.weekly_reset = now
        if stats.monthly_reset and (now - stats.monthly_reset).days >= 30:
            stats.monthly_games = 0
            stats.monthly_reset = now
        if not stats.daily_reset:
            stats.daily_reset = now
        if not stats.weekly_reset:
            stats.weekly_reset = now
        if not stats.monthly_reset:
            stats.monthly_reset = now
        update_ops = {
            "$inc": {
                "games_played": 1,
                "lifetime_games": 1,
                "daily_games": 1,
                "weekly_games": 1,
                "monthly_games": 1,
            },
            "$set": {"last_game_date": now, "updated_at": now},
        }
        if won:
            update_ops["$inc"]["games_won"] = 1
            update_ops["$inc"]["total_coins_won"] = payout
            update_ops["$inc"]["current_win_streak"] = 1
            update_ops["$set"]["current_lose_streak"] = 0
            if payout > 0:
                update_ops["$max"] = {"highest_win": payout}
        else:
            update_ops["$inc"]["games_lost"] = 1
            update_ops["$inc"]["total_coins_lost"] = bet
            update_ops["$inc"]["current_lose_streak"] = 1
            update_ops["$set"]["current_win_streak"] = 0
        if bet > 0:
            update_ops["$max"] = {"highest_bet": bet}
        await self.collection.update_one(
            {"user_id": user_id},
            {"$set": {"daily_reset": stats.daily_reset, "weekly_reset": stats.weekly_reset, "monthly_reset": stats.monthly_reset}},
            upsert=True,
        )
        await self.collection.update_one({"user_id": user_id}, update_ops)
        return await self.get_stats(user_id)

    async def update_streaks(self, user_id: int) -> None:
        stats = await self.get_or_create(user_id)
        if stats.current_win_streak > stats.longest_win_streak:
            await self.collection.update_one(
                {"user_id": user_id},
                {"$set": {"longest_win_streak": stats.current_win_streak}},
            )
        if stats.current_lose_streak > stats.longest_lose_streak:
            await self.collection.update_one(
                {"user_id": user_id},
                {"$set": {"longest_lose_streak": stats.current_lose_streak}},
            )

    async def get_top_played(self, limit: int = 10) -> list[GameStatsModel]:
        cursor = self.collection.find({}).sort("games_played", -1).limit(limit)
        docs = await cursor.to_list(length=limit)
        return [GameStatsModel.from_doc(d) for d in docs]

    async def get_top_winners(self, limit: int = 10) -> list[GameStatsModel]:
        cursor = self.collection.find({}).sort("total_coins_won", -1).limit(limit)
        docs = await cursor.to_list(length=limit)
        return [GameStatsModel.from_doc(d) for d in docs]

    async def get_top_win_rate(self, limit: int = 10) -> list[GameStatsModel]:
        pipeline = [
            {"$match": {"games_played": {"$gte": 5}}},
            {"$addFields": {"win_rate": {"$divide": ["$games_won", "$games_played"]}}},
            {"$sort": {"win_rate": -1}},
            {"$limit": limit},
        ]
        cursor = self.collection.aggregate(pipeline)
        docs = await cursor.to_list(length=limit)
        return [GameStatsModel.from_doc(d) for d in docs]

    async def get_top_earners(self, limit: int = 10) -> list[GameStatsModel]:
        pipeline = [
            {"$addFields": {"net_profit": {"$subtract": ["$total_coins_won", "$total_coins_lost"]}}},
            {"$sort": {"net_profit": -1}},
            {"$limit": limit},
        ]
        cursor = self.collection.aggregate(pipeline)
        docs = await cursor.to_list(length=limit)
        return [GameStatsModel.from_doc(d) for d in docs]

    async def get_top_bettors(self, limit: int = 10) -> list[GameStatsModel]:
        pipeline = [
            {"$addFields": {"total_bet": {"$add": ["$total_coins_won", "$total_coins_lost"]}}},
            {"$sort": {"total_bet": -1}},
            {"$limit": limit},
        ]
        cursor = self.collection.aggregate(pipeline)
        docs = await cursor.to_list(length=limit)
        return [GameStatsModel.from_doc(d) for d in docs]

    async def reset_stats(self, user_id: int) -> None:
        await self.collection.delete_one({"user_id": user_id})

    async def reset_all_stats(self) -> None:
        await self.collection.delete_many({})
