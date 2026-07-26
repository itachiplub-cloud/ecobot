from __future__ import annotations

from typing import Optional

from motor.motor_asyncio import AsyncIOMotorDatabase

from bot.database.models.admin import AdminModel


class AdminRepository:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.collection = db.admins

    async def add_admin(self, admin: AdminModel) -> AdminModel:
        await self.collection.insert_one(admin.to_dict())
        return admin

    async def get_admin(self, user_id: int) -> Optional[AdminModel]:
        doc = await self.collection.find_one({"user_id": user_id})
        return AdminModel.from_doc(doc)

    async def remove_admin(self, user_id: int) -> bool:
        result = await self.collection.delete_one({"user_id": user_id})
        return result.deleted_count > 0

    async def is_admin(self, user_id: int) -> bool:
        doc = await self.collection.find_one({"user_id": user_id, "is_active": True})
        return doc is not None

    async def get_all_admins(self) -> list[AdminModel]:
        cursor = self.collection.find({"is_active": True})
        docs = await cursor.to_list(length=None)
        return [AdminModel.from_doc(d) for d in docs]

    async def update_admin(self, user_id: int, **update_data) -> None:
        await self.collection.update_one(
            {"user_id": user_id},
            {"$set": update_data},
        )

    async def set_sudo(self, user_id: int, added_by: int) -> AdminModel:
        admin = AdminModel(user_id=user_id, role="sudo", added_by=added_by)
        await self.collection.update_one(
            {"user_id": user_id},
            {"$set": admin.to_dict()},
            upsert=True,
        )
        return admin
