from __future__ import annotations

from datetime import datetime, timedelta, timezone

from motor.motor_asyncio import AsyncIOMotorDatabase

from bot.database.repositories.investment_repo import InvestmentRepository
from bot.database.repositories.economy_repo import EconomyRepository
from bot.database.models.investment import InvestmentModel


INVESTMENT_TYPES = {
    "savings": {"rate": 0.02, "risk": "none", "min_amount": 100, "lock_days": 7},
    "fixed": {"rate": 0.05, "risk": "low", "min_amount": 500, "lock_days": 30},
    "growth": {"rate": 0.10, "risk": "medium", "min_amount": 1000, "lock_days": 60},
    "premium": {"rate": 0.15, "risk": "high", "min_amount": 5000, "lock_days": 90},
}


class EnhancedBankService:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.invest_repo = InvestmentRepository(db)
        self.econ_repo = EconomyRepository(db)
        self.db = db

    async def get_bank_info(self, user_id: int) -> dict:
        bank_doc = await self.db.banks.find_one({"user_id": user_id})
        balance = bank_doc.get("balance", 0) if bank_doc else 0
        interest_rate = bank_doc.get("interest_rate", 0.02) if bank_doc else 0.02
        investments = await self.invest_repo.get_user_investments(user_id)
        total_invested = sum(i.amount for i in investments)
        total_returns = sum(i.returns for i in investments)
        return {
            "balance": balance,
            "interest_rate": interest_rate,
            "investments": investments,
            "total_invested": total_invested,
            "total_returns": total_returns,
        }

    async def invest(self, user_id: int, amount: int, investment_type: str = "fixed") -> dict:
        inv_config = INVESTMENT_TYPES.get(investment_type, INVESTMENT_TYPES["fixed"])
        if amount < inv_config["min_amount"]:
            return {"success": False, "reason": "min_amount", "min": inv_config["min_amount"]}
        eco = await self.econ_repo.get_economy(user_id)
        if not eco or eco.wallet < amount:
            return {"success": False, "reason": "insufficient_funds"}
        await self.econ_repo.remove_coins(user_id, amount)
        inv = InvestmentModel(
            investment_id=self.invest_repo.generate_investment_id(),
            user_id=user_id,
            amount=amount,
            investment_type=investment_type,
            interest_rate=inv_config["rate"],
            risk_level=inv_config["risk"],
            matures_at=datetime.now(timezone.utc) + timedelta(days=inv_config["lock_days"]),
        )
        await self.invest_repo.create_investment(inv)
        return {"success": True, "investment_id": inv.investment_id, "rate": inv_config["rate"], "matures": inv.matures_at}

    async def collect_investment(self, user_id: int, investment_id: str) -> dict:
        inv = await self.invest_repo.get_investment(user_id, investment_id)
        if not inv:
            return {"success": False, "reason": "not_found"}
        if inv.matures_at and inv.matures_at > datetime.now(timezone.utc):
            return {"success": False, "reason": "not_matured", "matures": inv.matures_at}
        returns = int(inv.amount * (1 + inv.interest_rate))
        await self.invest_repo.complete_investment(user_id, investment_id, returns)
        await self.econ_repo.add_coins(user_id, returns, f"Investment return: {inv.investment_type}")
        return {"success": True, "returns": returns, "profit": returns - inv.amount}

    async def get_investment_types(self) -> dict:
        return INVESTMENT_TYPES

    async def get_all_active_investments(self):
        return await self.invest_repo.get_all_active()

    async def get_total_invested(self, user_id: int) -> int:
        return await self.invest_repo.get_total_invested(user_id)
