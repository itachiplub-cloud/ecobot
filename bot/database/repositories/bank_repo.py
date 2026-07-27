from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Optional

from motor.motor_asyncio import AsyncIOMotorDatabase

from bot.database.models.bank import BankModel


class BankRepository:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.collection = db.banks

    async def get_bank(self, user_id: int) -> Optional[BankModel]:
        doc = await self.collection.find_one({"user_id": user_id})
        return BankModel.from_doc(doc)

    async def get_or_create(self, user_id: int) -> BankModel:
        bank = await self.get_bank(user_id)
        if bank is None:
            bank = BankModel(user_id=user_id)
            await self.collection.insert_one(bank.to_dict())
        return bank

    async def deposit(self, user_id: int, amount: int) -> Optional[BankModel]:
        bank = await self.get_or_create(user_id)
        bank.balance += amount
        await self.collection.update_one(
            {"user_id": user_id},
            {"$set": {"balance": bank.balance, "updated_at": datetime.now(timezone.utc)}},
        )
        return bank

    async def withdraw(self, user_id: int, amount: int) -> Optional[BankModel]:
        bank = await self.get_bank(user_id)
        if not bank or bank.balance < amount:
            return None
        bank.balance -= amount
        await self.collection.update_one(
            {"user_id": user_id},
            {"$set": {"balance": bank.balance, "updated_at": datetime.now(timezone.utc)}},
        )
        return bank

    async def apply_interest(self, user_id: int) -> int:
        bank = await self.get_bank(user_id)
        if not bank or bank.balance <= 0:
            return 0
        interest = int(bank.balance * bank.interest_rate)
        if interest > 0:
            bank.balance += interest
            bank.total_interest_earned += interest
            await self.collection.update_one(
                {"user_id": user_id},
                {"$set": {
                    "balance": bank.balance,
                    "total_interest_earned": bank.total_interest_earned,
                    "last_interest": datetime.now(timezone.utc),
                }},
            )
        return interest

    async def take_loan(self, user_id: int, amount: int, days: int = 30) -> Optional[BankModel]:
        bank = await self.get_or_create(user_id)
        if bank.loan_amount > 0:
            return None
        bank.loan_amount = amount
        bank.loan_taken_at = datetime.now(timezone.utc)
        bank.loan_due = datetime.now(timezone.utc) + timedelta(days=days)
        await self.collection.update_one(
            {"user_id": user_id},
            {"$set": {
                "loan_amount": bank.loan_amount,
                "loan_taken_at": bank.loan_taken_at,
                "loan_due": bank.loan_due,
            }},
        )
        return bank

    async def repay_loan(self, user_id: int, amount: int) -> Optional[BankModel]:
        bank = await self.get_bank(user_id)
        if not bank or bank.loan_amount <= 0:
            return None
        bank.loan_amount -= amount
        if bank.loan_amount <= 0:
            bank.loan_amount = 0
            bank.loan_taken_at = None
            bank.loan_due = None
        await self.collection.update_one(
            {"user_id": user_id},
            {"$set": {
                "loan_amount": bank.loan_amount,
                "loan_taken_at": bank.loan_taken_at,
                "loan_due": bank.loan_due,
            }},
        )
        return bank

    async def add_investment(self, user_id: int, investment: dict) -> bool:
        result = await self.collection.update_one(
            {"user_id": user_id},
            {"$push": {"investments": investment}, "$inc": {"total_invested": investment.get("amount", 0)}},
        )
        return result.modified_count > 0

    async def get_balance(self, user_id: int) -> int:
        bank = await self.get_bank(user_id)
        return bank.balance if bank else 0
