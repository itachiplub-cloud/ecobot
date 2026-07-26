from __future__ import annotations

from datetime import datetime
from typing import Optional

from motor.motor_asyncio import AsyncIOMotorDatabase

from bot.database.models.inventory import InventoryModel


class InventoryRepository:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.collection = db.inventory

    async def add_item(self, user_id: int, item_id: str, quantity: int = 1, **kwargs) -> InventoryModel:
        existing = await self.collection.find_one({"user_id": user_id, "item_id": item_id})
        if existing:
            await self.collection.update_one(
                {"user_id": user_id, "item_id": item_id},
                {"$inc": {"quantity": quantity}},
            )
            item = await self.collection.find_one({"user_id": user_id, "item_id": item_id})
            return InventoryModel.from_doc(item)
        inv = InventoryModel(user_id=user_id, item_id=item_id, quantity=quantity, **kwargs)
        await self.collection.insert_one(inv.to_dict())
        return inv

    async def remove_item(self, user_id: int, item_id: str, quantity: int = 1) -> bool:
        existing = await self.collection.find_one({"user_id": user_id, "item_id": item_id})
        if not existing or existing["quantity"] < quantity:
            return False
        if existing["quantity"] == quantity:
            await self.collection.delete_one({"user_id": user_id, "item_id": item_id})
        else:
            await self.collection.update_one(
                {"user_id": user_id, "item_id": item_id},
                {"$inc": {"quantity": -quantity}},
            )
        return True

    async def get_item(self, user_id: int, item_id: str) -> Optional[InventoryModel]:
        doc = await self.collection.find_one({"user_id": user_id, "item_id": item_id})
        return InventoryModel.from_doc(doc)

    async def get_user_items(self, user_id: int) -> list[InventoryModel]:
        cursor = self.collection.find({"user_id": user_id})
        docs = await cursor.to_list(length=None)
        return [InventoryModel.from_doc(d) for d in docs]

    async def get_user_item_count(self, user_id: int, item_id: str) -> int:
        doc = await self.collection.find_one({"user_id": user_id, "item_id": item_id})
        return doc["quantity"] if doc else 0

    async def equip_item(self, user_id: int, item_id: str, slot: str) -> bool:
        result = await self.collection.update_one(
            {"user_id": user_id, "item_id": item_id},
            {"$set": {"equipped": True, "slot": slot}},
        )
        return result.modified_count > 0

    async def unequip_item(self, user_id: int, item_id: str) -> bool:
        result = await self.collection.update_one(
            {"user_id": user_id, "item_id": item_id},
            {"$set": {"equipped": False, "slot": None}},
        )
        return result.modified_count > 0

    async def get_equipped(self, user_id: int) -> list[InventoryModel]:
        cursor = self.collection.find({"user_id": user_id, "equipped": True})
        docs = await cursor.to_list(length=None)
        return [InventoryModel.from_doc(d) for d in docs]

    async def clear_inventory(self, user_id: int) -> None:
        await self.collection.delete_many({"user_id": user_id})

    async def has_item(self, user_id: int, item_id: str, quantity: int = 1) -> bool:
        doc = await self.collection.find_one({"user_id": user_id, "item_id": item_id})
        return doc is not None and doc["quantity"] >= quantity

    async def count_items(self, user_id: int) -> int:
        pipeline = [
            {"$match": {"user_id": user_id}},
            {"$group": {"_id": None, "total": {"$sum": "$quantity"}}},
        ]
        result = await self.collection.aggregate(pipeline).to_list(1)
        return result[0]["total"] if result else 0
