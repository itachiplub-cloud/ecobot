from __future__ import annotations

from motor.motor_asyncio import AsyncIOMotorDatabase

from bot.database.repositories.inventory_repo import InventoryRepository
from bot.database.repositories.item_repo import ItemRepository


class InventoryService:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.inv_repo = InventoryRepository(db)
        self.item_repo = ItemRepository(db)

    async def add_item(self, user_id: int, item_id: str, quantity: int = 1, **kwargs):
        return await self.inv_repo.add_item(user_id, item_id, quantity, **kwargs)

    async def remove_item(self, user_id: int, item_id: str, quantity: int = 1) -> bool:
        return await self.inv_repo.remove_item(user_id, item_id, quantity)

    async def get_item(self, user_id: int, item_id: str):
        return await self.inv_repo.get_item(user_id, item_id)

    async def get_user_items(self, user_id: int):
        return await self.inv_repo.get_user_items(user_id)

    async def has_item(self, user_id: int, item_id: str, quantity: int = 1) -> bool:
        return await self.inv_repo.has_item(user_id, item_id, quantity)

    async def get_item_count(self, user_id: int, item_id: str) -> int:
        return await self.inv_repo.get_user_item_count(user_id, item_id)

    async def equip_item(self, user_id: int, item_id: str, slot: str) -> bool:
        return await self.inv_repo.equip_item(user_id, item_id, slot)

    async def unequip_item(self, user_id: int, item_id: str) -> bool:
        return await self.inv_repo.unequip_item(user_id, item_id)

    async def get_equipped(self, user_id: int):
        return await self.inv_repo.get_equipped(user_id)

    async def get_total_items(self, user_id: int) -> int:
        return await self.inv_repo.count_items(user_id)

    async def get_item_info(self, item_id: str):
        return await self.item_repo.get_item(item_id)

    async def get_items_by_category(self, category: str):
        return await self.item_repo.get_by_category(category)

    async def search_items(self, query: str):
        return await self.item_repo.search_items(query)

    async def clear_inventory(self, user_id: int) -> None:
        await self.inv_repo.clear_inventory(user_id)

    async def calc_equipment_stats(self, user_id: int) -> dict:
        equipped = await self.get_equipped(user_id)
        stats = {"attack": 0, "defense": 0, "speed": 0, "luck": 0, "critical": 0}
        for inv_item in equipped:
            item = await self.get_item_info(inv_item.item_id)
            if item and item.stats:
                for k in stats:
                    stats[k] += item.stats.get(k, 0)
        return stats
