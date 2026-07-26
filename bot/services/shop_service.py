from __future__ import annotations

from motor.motor_asyncio import AsyncIOMotorDatabase

from bot.database.repositories.shop_repo import ShopRepository
from bot.database.repositories.item_repo import ItemRepository
from bot.database.repositories.inventory_repo import InventoryRepository
from bot.database.repositories.economy_repo import EconomyRepository


class ShopService:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.shop_repo = ShopRepository(db)
        self.item_repo = ItemRepository(db)
        self.inv_repo = InventoryRepository(db)
        self.econ_repo = EconomyRepository(db)

    async def get_shop_items(self, shop_type: str = "permanent"):
        return await self.shop_repo.get_shop_items(shop_type)

    async def buy_item(self, user_id: int, item_id: str, shop_type: str = "permanent", quantity: int = 1) -> dict:
        shop_item = await self.shop_repo.get_shop_item(item_id, shop_type)
        if not shop_item:
            return {"success": False, "reason": "item_not_found"}
        if shop_item.stock >= 0 and shop_item.stock < quantity:
            return {"success": False, "reason": "out_of_stock"}
        item = await self.item_repo.get_item(item_id)
        if not item:
            return {"success": False, "reason": "item_not_found"}
        price = shop_item.price_override if shop_item.price_override else item.price
        total = price * quantity
        if shop_item.discount > 0:
            total = int(total * (1 - shop_item.discount))
        eco = await self.econ_repo.get_economy(user_id)
        if not eco or eco.wallet < total:
            return {"success": False, "reason": "insufficient_funds", "needed": total, "have": eco.wallet if eco else 0}
        await self.econ_repo.remove_coins(user_id, total)
        await self.inv_repo.add_item(user_id, item_id, quantity)
        if shop_item.stock >= 0:
            await self.shop_repo.reduce_stock(item_id, shop_type)
        return {"success": True, "paid": total, "item": item.name, "quantity": quantity}

    async def sell_item(self, user_id: int, item_id: str, quantity: int = 1) -> dict:
        inv_item = await self.inv_repo.get_item(user_id, item_id)
        if not inv_item or inv_item.quantity < quantity:
            return {"success": False, "reason": "insufficient_items"}
        item = await self.item_repo.get_item(item_id)
        if not item or not item.sellable:
            return {"success": False, "reason": "cannot_sell"}
        total = item.sell_price * quantity
        await self.inv_repo.remove_item(user_id, item_id, quantity)
        await self.econ_repo.add_coins(user_id, total)
        return {"success": True, "earned": total, "item": item.name, "quantity": quantity}

    async def get_featured(self, shop_type: str = "permanent"):
        return await self.shop_repo.get_featured(shop_type)

    async def get_premium_shop(self):
        return await self.shop_repo.get_premium_shop()
