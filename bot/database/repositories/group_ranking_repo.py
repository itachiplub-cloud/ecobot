from __future__ import annotations

from datetime import datetime
from typing import Optional

from motor.motor_asyncio import AsyncIOMotorDatabase

from bot.database.models.group_ranking import GroupRankingModel


class GroupRankingRepository:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.collection = db.group_rankings

    async def get_or_create(self, user_id: int, group_id: int) -> GroupRankingModel:
        doc = await self.collection.find_one({"user_id": user_id, "group_id": group_id})
        if doc:
            return GroupRankingModel.from_doc(doc)
        ranking = GroupRankingModel(user_id=user_id, group_id=group_id)
        await self.collection.insert_one(ranking.to_dict())
        return ranking

    async def update_activity(self, user_id: int, group_id: int, xp: int = 0, coins: int = 0, messages: int = 0, games: int = 0) -> GroupRankingModel:
        await self.collection.update_one(
            {"user_id": user_id, "group_id": group_id},
            {
                "$inc": {
                    "xp_earned": xp,
                    "coins_earned": coins,
                    "messages_sent": messages,
                    "games_played": games,
                },
                "$set": {"last_active": datetime.utcnow()},
            },
            upsert=True,
        )
        return await self.get_or_create(user_id, group_id)

    async def get_group_top(self, group_id: int, category: str = "xp_earned", limit: int = 10) -> list[GroupRankingModel]:
        valid_sorts = {"xp_earned", "coins_earned", "messages_sent", "games_played", "level"}
        if category not in valid_sorts:
            category = "xp_earned"
        cursor = self.collection.find({"group_id": group_id}).sort(category, -1).limit(limit)
        docs = await cursor.to_list(length=limit)
        return [GroupRankingModel.from_doc(d) for d in docs]

    async def get_user_rank(self, user_id: int, group_id: int, category: str = "xp_earned") -> Optional[int]:
        doc = await self.collection.find_one({"user_id": user_id, "group_id": group_id})
        if not doc:
            return None
        rank = await self.collection.count_documents({
            "group_id": group_id,
            category: {"$gt": doc.get(category, 0)},
        })
        return rank + 1

    async def get_user_stats(self, user_id: int, group_id: int) -> Optional[GroupRankingModel]:
        doc = await self.collection.find_one({"user_id": user_id, "group_id": group_id})
        return GroupRankingModel.from_doc(doc)

    async def get_all_groups(self) -> list[int]:
        pipeline = [
            {"$group": {"_id": "$group_id"}},
            {"$sort": {"_id": 1}},
        ]
        cursor = self.collection.aggregate(pipeline)
        docs = await cursor.to_list(length=None)
        return [d["_id"] for d in docs if d["_id"]]

    async def get_group_member_count(self, group_id: int) -> int:
        return await self.collection.count_documents({"group_id": group_id})

    async def update_level(self, user_id: int, group_id: int, level: int) -> None:
        await self.collection.update_one(
            {"user_id": user_id, "group_id": group_id},
            {"$set": {"level": level, "last_active": datetime.utcnow()}},
            upsert=True,
        )

    async def reset_group(self, group_id: int) -> None:
        await self.collection.delete_many({"group_id": group_id})

    async def get_global_top(self, category: str = "xp_earned", limit: int = 10) -> list[GroupRankingModel]:
        valid_sorts = {"xp_earned", "coins_earned", "messages_sent", "games_played"}
        if category not in valid_sorts:
            category = "xp_earned"
        pipeline = [
            {"$group": {
                "_id": "$user_id",
                "xp_earned": {"$sum": "$xp_earned"},
                "coins_earned": {"$sum": "$coins_earned"},
                "messages_sent": {"$sum": "$messages_sent"},
                "games_played": {"$sum": "$games_played"},
            }},
            {"$sort": {category: -1}},
            {"$limit": limit},
        ]
        cursor = self.collection.aggregate(pipeline)
        docs = await cursor.to_list(length=limit)
        return [GroupRankingModel(
            user_id=d["_id"], group_id=0,
            xp_earned=d.get("xp_earned", 0),
            coins_earned=d.get("coins_earned", 0),
            messages_sent=d.get("messages_sent", 0),
            games_played=d.get("games_played", 0),
        ) for d in docs]
