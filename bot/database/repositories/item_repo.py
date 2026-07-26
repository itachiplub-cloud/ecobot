from __future__ import annotations

from typing import Optional

from motor.motor_asyncio import AsyncIOMotorDatabase

from bot.database.models.item import ItemModel


class ItemRepository:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.collection = db.items

    async def get_item(self, item_id: str) -> Optional[ItemModel]:
        doc = await self.collection.find_one({"item_id": item_id})
        return ItemModel.from_doc(doc)

    async def create_item(self, item: ItemModel) -> ItemModel:
        await self.collection.insert_one(item.to_dict())
        return item

    async def update_item(self, item_id: str, **update_data) -> None:
        await self.collection.update_one(
            {"item_id": item_id},
            {"$set": update_data},
        )

    async def get_by_category(self, category: str) -> list[ItemModel]:
        cursor = self.collection.find({"category": category, "is_active": True})
        docs = await cursor.to_list(length=None)
        return [ItemModel.from_doc(d) for d in docs]

    async def get_by_rarity(self, rarity: str) -> list[ItemModel]:
        cursor = self.collection.find({"rarity": rarity, "is_active": True})
        docs = await cursor.to_list(length=None)
        return [ItemModel.from_doc(d) for d in docs]

    async def get_buyable(self, min_level: int = 1) -> list[ItemModel]:
        cursor = self.collection.find({
            "buyable": True,
            "is_active": True,
            "level_required": {"$lte": min_level},
        })
        docs = await cursor.to_list(length=None)
        return [ItemModel.from_doc(d) for d in docs]

    async def search_items(self, query: str) -> list[ItemModel]:
        regex = {"$regex": query, "$options": "i"}
        cursor = self.collection.find({
            "$or": [{"name": regex}, {"description": regex}],
            "is_active": True,
        })
        docs = await cursor.to_list(length=None)
        return [ItemModel.from_doc(d) for d in docs]

    async def get_all(self) -> list[ItemModel]:
        cursor = self.collection.find({"is_active": True})
        docs = await cursor.to_list(length=None)
        return [ItemModel.from_doc(d) for d in docs]

    async def count_items(self) -> int:
        return await self.collection.count_documents({"is_active": True})

    async def delete_item(self, item_id: str) -> None:
        await self.collection.delete_one({"item_id": item_id})

    async def get_random_by_rarity(self, rarity: str, count: int = 1) -> list[ItemModel]:
        pipeline = [
            {"$match": {"rarity": rarity, "is_active": True, "drop_rate": {"$gt": 0}}},
            {"$sample": {"size": count}},
        ]
        cursor = self.collection.aggregate(pipeline)
        docs = await cursor.to_list(length=count)
        return [ItemModel.from_doc(d) for d in docs]

    async def seed_items(self, items: list[ItemModel]) -> None:
        for item in items:
            existing = await self.get_item(item.item_id)
            if not existing:
                await self.create_item(item)
