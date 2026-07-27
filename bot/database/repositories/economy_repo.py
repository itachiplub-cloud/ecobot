from __future__ import annotations

from datetime import datetime, timezone
from typing import Optional

from motor.motor_asyncio import AsyncIOMotorDatabase

from bot.database.models.economy import EconomyModel


class EconomyRepository:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.collection = db.economy

    async def get_economy(self, user_id: int) -> Optional[EconomyModel]:
        doc = await self.collection.find_one({"user_id": user_id})
        return EconomyModel.from_doc(doc)

    async def create_economy(self, economy: EconomyModel) -> EconomyModel:
        await self.collection.insert_one(economy.to_dict())
        return economy

    async def get_or_create(self, user_id: int, default_wallet: int = 0) -> EconomyModel:
        eco = await self.get_economy(user_id)
        if eco is None:
            eco = EconomyModel(user_id=user_id, wallet=default_wallet)
            await self.create_economy(eco)
        return eco

    async def add_coins(self, user_id: int, amount: int, source: str = "") -> EconomyModel:
        eco = await self.get_or_create(user_id)
        eco.wallet += amount
        if amount > 0:
            eco.total_earned += abs(amount)
        else:
            eco.total_spent += abs(amount)
        await self.collection.update_one(
            {"user_id": user_id},
            {"$set": {
                "wallet": eco.wallet,
                "total_earned": eco.total_earned,
                "total_spent": eco.total_spent,
                "updated_at": datetime.now(timezone.utc),
            }},
        )
        return eco

    async def remove_coins(self, user_id: int, amount: int) -> Optional[EconomyModel]:
        eco = await self.get_economy(user_id)
        if eco is None or eco.wallet < amount:
            return None
        eco.wallet -= amount
        eco.total_spent += amount
        await self.collection.update_one(
            {"user_id": user_id},
            {"$set": {
                "wallet": eco.wallet,
                "total_spent": eco.total_spent,
                "updated_at": datetime.now(timezone.utc),
            }},
        )
        return eco

    async def transfer(self, sender_id: int, receiver_id: int, amount: int) -> tuple[Optional[EconomyModel], Optional[EconomyModel]]:
        sender = await self.get_economy(sender_id)
        receiver = await self.get_or_create(receiver_id)
        if sender is None or sender.wallet < amount:
            return None, None
        sender.wallet -= amount
        sender.total_spent += amount
        receiver.wallet += amount
        receiver.total_earned += amount
        await self.collection.update_one(
            {"user_id": sender_id},
            {"$set": {"wallet": sender.wallet, "total_spent": sender.total_spent, "updated_at": datetime.now(timezone.utc)}},
        )
        await self.collection.update_one(
            {"user_id": receiver_id},
            {"$set": {"wallet": receiver.wallet, "total_earned": receiver.total_earned, "updated_at": datetime.now(timezone.utc)}},
        )
        return sender, receiver

    async def deposit(self, user_id: int, amount: int) -> Optional[EconomyModel]:
        eco = await self.get_economy(user_id)
        if eco is None or eco.wallet < amount:
            return None
        eco.wallet -= amount
        eco.bank += amount
        eco.total_deposited += amount
        await self.collection.update_one(
            {"user_id": user_id},
            {"$set": {
                "wallet": eco.wallet,
                "bank": eco.bank,
                "total_deposited": eco.total_deposited,
                "updated_at": datetime.now(timezone.utc),
            }},
        )
        return eco

    async def withdraw(self, user_id: int, amount: int) -> Optional[EconomyModel]:
        eco = await self.get_economy(user_id)
        if eco is None or eco.bank < amount:
            return None
        eco.bank -= amount
        eco.wallet += amount
        eco.total_withdrawn += amount
        await self.collection.update_one(
            {"user_id": user_id},
            {"$set": {
                "wallet": eco.wallet,
                "bank": eco.bank,
                "total_withdrawn": eco.total_withdrawn,
                "updated_at": datetime.now(timezone.utc),
            }},
        )
        return eco

    async def get_richest(self, limit: int = 10) -> list[EconomyModel]:
        cursor = self.collection.find({}).sort("wallet", -1).limit(limit)
        docs = await cursor.to_list(length=limit)
        return [EconomyModel.from_doc(d) for d in docs]

    async def get_top_savers(self, limit: int = 10) -> list[EconomyModel]:
        cursor = self.collection.find({}).sort("bank", -1).limit(limit)
        docs = await cursor.to_list(length=limit)
        return [EconomyModel.from_doc(d) for d in docs]

    async def get_total_coins(self) -> int:
        pipeline = [
            {"$group": {"_id": None, "total": {"$sum": "$wallet"}}},
        ]
        result = await self.collection.aggregate(pipeline).to_list(1)
        return result[0]["total"] if result else 0

    async def set_balance(self, user_id: int, wallet: int = 0, bank: int = 0) -> None:
        await self.collection.update_one(
            {"user_id": user_id},
            {"$set": {"wallet": wallet, "bank": bank, "updated_at": datetime.now(timezone.utc)}},
        )

    async def reset_all(self) -> None:
        await self.collection.update_many(
            {},
            {"$set": {"wallet": 0, "bank": 0, "updated_at": datetime.now(timezone.utc)}},
        )

    async def global_add(self, amount: int) -> None:
        await self.collection.update_many(
            {},
            {"$inc": {"wallet": amount}},
        )
