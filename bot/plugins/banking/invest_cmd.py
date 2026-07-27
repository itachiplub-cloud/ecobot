from __future__ import annotations

import random
from datetime import datetime, timedelta, timezone

from pyrogram import Client, filters
from pyrogram.types import Message

from bot.core import loc
from bot.database.repositories.investment_repo import InvestmentRepository
from bot.database.models.investment import InvestmentModel
from bot.utils.helpers import format_number

INVESTMENT_TYPES = {
    "savings": {"interest_rate": 0.5, "lock_days": 0, "risk_level": "low", "label": "🏦 Savings"},
    "fixed": {"interest_rate": 1.2, "lock_days": 7, "risk_level": "low", "label": "🔒 Fixed"},
    "growth": {"interest_rate": 2.5, "lock_days": 14, "risk_level": "medium", "label": "📊 Growth"},
    "premium": {"interest_rate": 3.0, "lock_days": 30, "risk_level": "high", "label": "👑 Premium"},
}


def register(app: Client):

    @app.on_message(filters.command("invest"))
    async def invest_command(client: Client, message: Message):
        services = getattr(message, '_services', None)
        if not services:
            return
        eco_svc = services.get("economy")
        args = message.text.split()

        if len(args) < 2:
            text = "📈 **Investments**\n\nSelect an investment type:\n\n"
            for key, val in INVESTMENT_TYPES.items():
                lock_str = f"{val['lock_days']} day lock" if val['lock_days'] > 0 else "No lock"
                text += f"{val['label']} ({val['interest_rate']}% daily) — {lock_str}, {val['risk_level']} risk\n"
            text += "\nUsage: /invest <type> <amount>"
            await message.reply_text(text)
            return

        inv_type = args[1].lower()
        if inv_type not in INVESTMENT_TYPES:
            await message.reply_text("❌ Invalid type. Use: savings, fixed, growth, premium")
            return

        try:
            amount = int(args[2])
        except (IndexError, ValueError):
            await message.reply_text("Usage: /invest <type> <amount>")
            return

        if amount <= 0:
            await message.reply_text("❌ Amount must be positive.")
            return

        balance = await eco_svc.get_balance(message.from_user.id)
        if balance["wallet"] < amount:
            await message.reply_text("❌ Not enough coins in wallet.")
            return

        config = INVESTMENT_TYPES[inv_type]
        investment_id = "INV-" + "".join(random.choices("ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789", k=8))
        matures_at = datetime.now(timezone.utc) + timedelta(days=config["lock_days"]) if config["lock_days"] > 0 else None

        inv_model = InvestmentModel(
            user_id=message.from_user.id,
            investment_id=investment_id,
            amount=amount,
            investment_type=inv_type,
            interest_rate=config["interest_rate"],
            risk_level=config["risk_level"],
            status="active",
            started_at=datetime.now(timezone.utc),
            matures_at=matures_at,
        )

        db = eco_svc.econ_repo.collection.database
        inv_repo = InvestmentRepository(db)
        await inv_repo.create_investment(inv_model)
        await eco_svc.remove_coins(message.from_user.id, amount, f"Investment: {inv_type}")

        lock_str = f" for {config['lock_days']} days" if config['lock_days'] > 0 else ""
        await message.reply_text(
            f"✅ Invested {format_number(amount)} coins in **{config['label']}**{lock_str}!\n"
            f"📈 Rate: {config['interest_rate']}% daily\n"
            f"🆔 ID: `{investment_id}`"
        )

    @app.on_message(filters.command("myinvestments"))
    async def myinvestments_command(client: Client, message: Message):
        services = getattr(message, '_services', None)
        if not services:
            return
        eco_svc = services.get("economy")
        db = eco_svc.econ_repo.collection.database
        inv_repo = InvestmentRepository(db)
        investments = await inv_repo.get_user_investments(message.from_user.id, "active")

        if not investments:
            await message.reply_text("❌ No active investments.\nUse /invest to start one.")
            return

        text = "📋 **Your Investments**\n\n"
        for inv in investments:
            config = INVESTMENT_TYPES.get(inv.investment_type, {})
            locked = inv.matures_at and inv.matures_at > datetime.now(timezone.utc)
            lock_str = f"🔒 Locked" if locked else "✅ Unlocked"
            days_left = ""
            if inv.matures_at and locked:
                delta = inv.matures_at - datetime.now(timezone.utc)
                days_left = f" ({delta.days}d {delta.seconds // 3600}h)"
            text += (
                f"🆔 `{inv.investment_id}`\n"
                f"  💰 {format_number(inv.amount)} coins\n"
                f"  📈 {config.get('interest_rate', 0)}% daily\n"
                f"  {lock_str}{days_left}\n\n"
            )
        await message.reply_text(text)

    @app.on_message(filters.command("withdrawinvestment"))
    async def withdraw_investment_command(client: Client, message: Message):
        services = getattr(message, '_services', None)
        if not services:
            return
        eco_svc = services.get("economy")
        args = message.text.split()
        if len(args) < 2:
            await message.reply_text("Usage: /withdrawinvestment <investment_id>")
            return

        investment_id = args[1]
        db = eco_svc.econ_repo.collection.database
        inv_repo = InvestmentRepository(db)
        inv = await inv_repo.get_investment(message.from_user.id, investment_id)

        if not inv:
            await message.reply_text("❌ Investment not found.")
            return

        if inv.matures_at and inv.matures_at > datetime.now(timezone.utc):
            delta = inv.matures_at - datetime.now(timezone.utc)
            await message.reply_text(f"❌ Still locked. Unlocks in {delta.days}d {delta.seconds // 3600}h.")
            return

        days_held = (datetime.now(timezone.utc) - inv.started_at).days
        interest = int(inv.amount * (inv.interest_rate / 100) * max(days_held, 1))
        total_return = inv.amount + interest

        if inv.risk_level == "high" and random.random() < 0.2:
            loss = int(inv.amount * 0.3)
            total_return = inv.amount - loss
            interest = -loss
        elif inv.risk_level == "medium" and random.random() < 0.1:
            loss = int(inv.amount * 0.15)
            total_return = inv.amount - loss
            interest = -loss

        await inv_repo.complete_investment(message.from_user.id, investment_id, total_return)
        await eco_svc.add_coins(message.from_user.id, total_return, f"Investment return: {inv.investment_type}")

        if interest >= 0:
            await message.reply_text(
                f"✅ Investment matured!\n"
                f"💰 Returned: {format_number(total_return)} coins\n"
                f"📈 Interest: +{format_number(interest)} coins"
            )
        else:
            await message.reply_text(
                f"⚠️ Investment ended with a loss.\n"
                f"💰 Returned: {format_number(total_return)} coins\n"
                f"💸 Loss: {format_number(abs(interest))} coins"
            )
