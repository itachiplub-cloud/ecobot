from __future__ import annotations

from datetime import datetime
from typing import Optional

from motor.motor_asyncio import AsyncIOMotorDatabase

from bot.database.models.shop import ShopModel


class ShopRepository:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.collection = db.shop

    async def get_shop_item(self, item_id: str, shop_type: str = "permanent") -> Optional[ShopModel]:
        doc = await self.collection.find_one({"item_id": item_id, "shop_type": shop_type})
        return ShopModel.from_doc(doc)

    async def add_shop_item(self, shop: ShopModel) -> ShopModel:
        await self.collection.insert_one(shop.to_dict())
        return shop

    async def get_shop_items(self, shop_type: str = "permanent") -> list[ShopModel]:
        query = {"shop_type": shop_type}
        if shop_type != "permanent":
            query["expires_at"] = {"$gt": datetime.utcnow()}
        cursor = self.collection.find(query)
        docs = await cursor.to_list(length=None)
        return [ShopModel.from_doc(d) for d in docs]

    async def reduce_stock(self, item_id: str, shop_type: str = "permanent") -> bool:
        doc = await self.collection.find_one({"item_id": item_id, "shop_type": shop_type})
        if not doc:
            return False
        if doc["stock"] == -1:
            return True
        if doc["stock"] <= 0:
            return False
        await self.collection.update_one(
            {"item_id": item_id, "shop_type": shop_type},
            {"$inc": {"stock": -1}},
        )
        return True

    async def remove_shop_item(self, item_id: str, shop_type: str = "permanent") -> None:
        await self.collection.delete_one({"item_id": item_id, "shop_type": shop_type})

    async def clear_shop(self, shop_type: str = "permanent") -> None:
        await self.collection.delete_many({"shop_type": shop_type})

    async def get_featured(self, shop_type: str = "permanent") -> list[ShopModel]:
        cursor = self.collection.find({
            "shop_type": shop_type,
            "featured": True,
        })
        docs = await cursor.to_list(length=None)
        return [ShopModel.from_doc(d) for d in docs]

    async def get_daily_shop(self) -> list[ShopModel]:
        return await self.get_shop_items("daily")

    async def get_weekly_shop(self) -> list[ShopModel]:
        return await self.get_shop_items("weekly")

    async def get_premium_shop(self) -> list[ShopModel]:
        return await self.get_shop_items("premium")
