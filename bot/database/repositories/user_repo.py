from __future__ import annotations

from datetime import datetime
from typing import Optional

from motor.motor_asyncio import AsyncIOMotorDatabase

from bot.database.models.user import UserModel


class UserRepository:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.collection = db.users

    async def get_user(self, user_id: int) -> Optional[UserModel]:
        doc = await self.collection.find_one({"user_id": user_id})
        return UserModel.from_doc(doc)

    async def create_user(self, user: UserModel) -> UserModel:
        await self.collection.insert_one(user.to_dict())
        return user

    async def get_or_create(self, user_id: int, **kwargs) -> UserModel:
        user = await self.get_user(user_id)
        if user is None:
            user = UserModel(user_id=user_id, **kwargs)
            await self.create_user(user)
        return user

    async def update_user(self, user_id: int, **update_data) -> None:
        update_data["last_active"] = datetime.utcnow()
        await self.collection.update_one(
            {"user_id": user_id},
            {"$set": update_data},
        )

    async def update_stats(self, user_id: int, stats: dict) -> None:
        set_ops = {}
        for k, v in stats.items():
            set_ops[f"stats.{k}"] = v
        set_ops["last_active"] = datetime.utcnow()
        await self.collection.update_one(
            {"user_id": user_id},
            {"$set": set_ops},
        )

    async def add_xp(self, user_id: int, xp: int) -> dict:
        user = await self.get_user(user_id)
        if not user:
            return {"leveled_up": False}
        user.xp += xp
        leveled_up = False
        while user.xp >= user.xp_needed:
            user.xp -= user.xp_needed
            user.level += 1
            user.xp_needed = int(user.xp_needed * 1.5)
            leveled_up = True
        await self.collection.update_one(
            {"user_id": user_id},
            {"$set": {
                "xp": user.xp,
                "level": user.level,
                "xp_needed": user.xp_needed,
                "last_active": datetime.utcnow(),
            }},
        )
        return {"leveled_up": leveled_up, "new_level": user.level}

    async def get_top_users(self, field: str, limit: int = 10) -> list[UserModel]:
        cursor = self.collection.find({}).sort(field, -1).limit(limit)
        docs = await cursor.to_list(length=limit)
        return [UserModel.from_doc(d) for d in docs]

    async def count_users(self) -> int:
        return await self.collection.count_documents({})

    async def increment_field(self, user_id: int, field: str, amount: int = 1) -> None:
        await self.collection.update_one(
            {"user_id": user_id},
            {"$inc": {field: amount}, "$set": {"last_active": datetime.utcnow()}},
        )

    async def ban_user(self, user_id: int, reason: str = "") -> None:
        await self.collection.update_one(
            {"user_id": user_id},
            {"$set": {"is_banned": True, "ban_reason": reason}},
        )

    async def unban_user(self, user_id: int) -> None:
        await self.collection.update_one(
            {"user_id": user_id},
            {"$set": {"is_banned": False, "ban_reason": None}},
        )

    async def search_users(self, query: str, limit: int = 20) -> list[UserModel]:
        regex = {"$regex": query, "$options": "i"}
        cursor = self.collection.find({
            "$or": [{"username": regex}, {"first_name": regex}]
        }).limit(limit)
        docs = await cursor.to_list(length=limit)
        return [UserModel.from_doc(d) for d in docs]

    async def delete_user(self, user_id: int) -> None:
        await self.collection.delete_one({"user_id": user_id})
