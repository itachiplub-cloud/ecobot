from __future__ import annotations

from motor.motor_asyncio import AsyncIOMotorDatabase

from bot.database.repositories.bank_repo import BankRepository
from bot.database.repositories.economy_repo import EconomyRepository


class BankService:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.bank_repo = BankRepository(db)
        self.econ_repo = EconomyRepository(db)

    async def get_balance(self, user_id: int) -> dict:
        bank = await self.bank_repo.get_or_create(user_id)
        return {
            "balance": bank.balance,
            "interest_rate": bank.interest_rate,
            "loan_amount": bank.loan_amount,
            "loan_due": bank.loan_due,
        }

    async def deposit(self, user_id: int, amount: int) -> dict:
        eco = await self.econ_repo.get_economy(user_id)
        if not eco or eco.wallet < amount:
            return {"success": False, "reason": "insufficient_funds"}
        await self.econ_repo.withdraw_from_wallet(user_id, amount) if hasattr(self.econ_repo, 'withdraw_from_wallet') else None
        eco.wallet -= amount
        from bot.database import get_db
        db = get_db()
        await db.economy.update_one({"user_id": user_id}, {"$set": {"wallet": eco.wallet}})
        await self.bank_repo.deposit(user_id, amount)
        return {"success": True, "balance": eco.wallet + amount, "bank_balance": eco.bank + amount}

    async def withdraw(self, user_id: int, amount: int) -> dict:
        bank = await self.bank_repo.get_bank(user_id)
        if not bank or bank.balance < amount:
            return {"success": False, "reason": "insufficient_funds"}
        await self.bank_repo.withdraw(user_id, amount)
        await self.econ_repo.add_coins(user_id, amount)
        return {"success": True, "bank_balance": bank.balance - amount}

    async def apply_interest(self, user_id: int) -> int:
        return await self.bank_repo.apply_interest(user_id)

    async def take_loan(self, user_id: int, amount: int, days: int = 30) -> dict:
        bank = await self.bank_repo.take_loan(user_id, amount, days)
        if not bank:
            return {"success": False, "reason": "existing_loan"}
        await self.econ_repo.add_coins(user_id, amount)
        return {"success": True, "loan": amount, "due": bank.loan_due}

    async def repay_loan(self, user_id: int, amount: int) -> dict:
        eco = await self.econ_repo.get_economy(user_id)
        if not eco or eco.wallet < amount:
            return {"success": False, "reason": "insufficient_funds"}
        bank = await self.bank_repo.get_bank(user_id)
        if not bank or bank.loan_amount <= 0:
            return {"success": False, "reason": "no_loan"}
        repay_amount = min(amount, bank.loan_amount)
        await self.econ_repo.remove_coins(user_id, repay_amount)
        await self.bank_repo.repay_loan(user_id, repay_amount)
        return {"success": True, "repaid": repay_amount, "remaining": bank.loan_amount - repay_amount}
