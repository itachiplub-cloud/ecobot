from __future__ import annotations

from motor.motor_asyncio import AsyncIOMotorDatabase

from bot.database.repositories.economy_repo import EconomyRepository
from bot.database.repositories.transaction_repo import TransactionRepository
from bot.database.models.transaction import TransactionModel
from config import settings


class EconomyService:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.econ_repo = EconomyRepository(db)
        self.tx_repo = TransactionRepository(db)

    async def get_balance(self, user_id: int) -> dict:
        eco = await self.econ_repo.get_or_create(user_id, settings.DEFAULT_BALANCE)
        return {"wallet": eco.wallet, "bank": eco.bank, "total": eco.wallet + eco.bank}

    async def add_coins(self, user_id: int, amount: int, description: str = "") -> dict:
        if await self.tx_repo.check_duplicate(user_id, "credit", amount):
            return {"success": False, "reason": "duplicate"}
        eco = await self.econ_repo.add_coins(user_id, amount)
        tx = TransactionModel(
            user_id=user_id,
            transaction_type="credit",
            amount=amount,
            balance_before=eco.wallet - amount,
            balance_after=eco.wallet,
            description=description,
        )
        await self.tx_repo.add_transaction(tx)
        return {"success": True, "wallet": eco.wallet}

    async def remove_coins(self, user_id: int, amount: int, description: str = "") -> dict:
        eco = await self.econ_repo.get_economy(user_id)
        if not eco or eco.wallet < amount:
            return {"success": False, "reason": "insufficient_funds"}
        eco = await self.econ_repo.remove_coins(user_id, amount)
        tx = TransactionModel(
            user_id=user_id,
            transaction_type="debit",
            amount=amount,
            balance_before=eco.wallet + amount,
            balance_after=eco.wallet,
            description=description,
        )
        await self.tx_repo.add_transaction(tx)
        return {"success": True, "wallet": eco.wallet}

    async def transfer(self, sender_id: int, receiver_id: int, amount: int) -> dict:
        if await self.tx_repo.check_duplicate(sender_id, "transfer_out", amount):
            return {"success": False, "reason": "duplicate"}
        sender, receiver = await self.econ_repo.transfer(sender_id, receiver_id, amount)
        if not sender:
            return {"success": False, "reason": "insufficient_funds"}
        await self.tx_repo.add_transaction(TransactionModel(
            user_id=sender_id, transaction_type="transfer_out", amount=amount,
            balance_after=sender.wallet, target_user=receiver_id, description="Transfer sent",
        ))
        await self.tx_repo.add_transaction(TransactionModel(
            user_id=receiver_id, transaction_type="transfer_in", amount=amount,
            balance_after=receiver.wallet, target_user=sender_id, description="Transfer received",
        ))
        return {"success": True, "sender_wallet": sender.wallet, "receiver_wallet": receiver.wallet}

    async def deposit(self, user_id: int, amount: int) -> dict:
        eco = await self.econ_repo.deposit(user_id, amount)
        if not eco:
            return {"success": False, "reason": "insufficient_funds"}
        await self.tx_repo.add_transaction(TransactionModel(
            user_id=user_id, transaction_type="deposit", amount=amount,
            balance_after=eco.bank, description="Bank deposit",
        ))
        return {"success": True, "wallet": eco.wallet, "bank": eco.bank}

    async def withdraw(self, user_id: int, amount: int) -> dict:
        eco = await self.econ_repo.withdraw(user_id, amount)
        if not eco:
            return {"success": False, "reason": "insufficient_funds"}
        await self.tx_repo.add_transaction(TransactionModel(
            user_id=user_id, transaction_type="withdraw", amount=amount,
            balance_after=eco.wallet, description="Bank withdrawal",
        ))
        return {"success": True, "wallet": eco.wallet, "bank": eco.bank}

    async def pay_tax(self, user_id: int, amount: int) -> dict:
        tax = int(amount * settings.TAX_RATE)
        if tax <= 0:
            return {"success": True, "tax": 0}
        result = await self.remove_coins(user_id, tax, "Government tax")
        return {"success": result["success"], "tax": tax}

    async def get_richest(self, limit: int = 10) -> list:
        return await self.econ_repo.get_richest(limit)

    async def get_top_savers(self, limit: int = 10) -> list:
        return await self.econ_repo.get_top_savers(limit)

    async def get_total_coins(self) -> int:
        return await self.econ_repo.get_total_coins()

    async def global_add(self, amount: int) -> None:
        await self.econ_repo.global_add(amount)

    async def reset_all(self) -> None:
        await self.econ_repo.reset_all()

    async def set_balance(self, user_id: int, wallet: int = 0, bank: int = 0) -> None:
        await self.econ_repo.set_balance(user_id, wallet, bank)

    async def get_transactions(self, user_id: int, limit: int = 20) -> list:
        return await self.tx_repo.get_transactions(user_id, limit)

    async def calc_with_tax(self, amount: int) -> int:
        return int(amount * (1 - settings.TAX_RATE))
