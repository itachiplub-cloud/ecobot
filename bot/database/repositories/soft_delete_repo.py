from __future__ import annotations

from datetime import datetime
from typing import Optional

from motor.motor_asyncio import AsyncIOMotorDatabase

from bot.database.models.deleted_user import DeletedUserModel
from bot.database.repositories.user_repo import UserRepository
from bot.database.repositories.economy_repo import EconomyRepository
from bot.database.repositories.inventory_repo import InventoryRepository


class SoftDeleteRepository:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.collection = db.deleted_users
        self.user_repo = UserRepository(db)
        self.econ_repo = EconomyRepository(db)
        self.inv_repo = InventoryRepository(db)

    async def backup_and_delete(self, user_id: int, deleted_by: int, reason: str = "") -> DeletedUserModel:
        user = await self.user_repo.get_user(user_id)
        eco = await self.econ_repo.get_economy(user_id)
        inv_items = await self.inv_repo.get_user_items(user_id)
        backup = {
            "user": user.to_dict() if user else {},
            "economy": eco.to_dict() if eco else {},
            "inventory": [i.to_dict() for i in inv_items],
        }
        deleted = DeletedUserModel(
            original_user_id=user_id,
            username=user.username if user else None,
            first_name=user.first_name if user else None,
            backup_data=backup,
            deleted_by=deleted_by,
            delete_reason=reason,
        )
        await self.collection.insert_one(deleted.to_dict())
        await self.user_repo.delete_user(user_id)
        return deleted

    async def restore_user(self, user_id: int) -> dict:
        doc = await self.collection.find_one({"original_user_id": user_id})
        if not doc:
            return {"success": False, "reason": "not_found"}
        deleted = DeletedUserModel.from_doc(doc)
        backup = deleted.backup_data
        if backup.get("user"):
            await self.user_repo.collection.insert_one(backup["user"])
        if backup.get("economy"):
            await self.econ_repo.collection.insert_one(backup["economy"])
        for inv in backup.get("inventory", []):
            await self.inv_repo.collection.insert_one(inv)
        await self.collection.delete_one({"original_user_id": user_id})
        return {"success": True, "user_id": user_id}

    async def purge_user(self, user_id: int) -> bool:
        result = await self.collection.delete_one({"original_user_id": user_id})
        return result.deleted_count > 0

    async def get_deleted_users(self, limit: int = 50) -> list[DeletedUserModel]:
        cursor = self.collection.find({}).sort("deleted_at", -1).limit(limit)
        docs = await cursor.to_list(length=limit)
        return [DeletedUserModel.from_doc(d) for d in docs]

    async def is_deleted(self, user_id: int) -> bool:
        count = await self.collection.count_documents({"original_user_id": user_id})
        return count > 0
