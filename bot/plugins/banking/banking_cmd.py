from __future__ import annotations

from pyrogram import Client, filters
from pyrogram.types import CallbackQuery, Message

from bot.core import loc
from bot.keyboards.inline import InlineKeyboards
from bot.utils.helpers import format_number


def register(app: Client):
    @app.on_message(filters.command("bankinfo") | filters.command("bank"))
    async def bankinfo_command(client: Client, message: Message):
        user = message.from_user
        lang = "en"
        if message._services:
            bank_svc = message._services.get("bank")
            if bank_svc:
                info = await bank_svc.get_balance(user.id)
                text = (
                    f"🏦 **Bank Info**\n\n"
                    f"💰 Balance: {format_number(info['balance'])}\n"
                    f"📈 Interest Rate: {info['interest_rate']*100}%\n"
                )
                if info["loan_amount"] > 0:
                    text += f"📄 Loan: {format_number(info['loan_amount'])} (Due: {info['loan_due']})\n"
                await message.reply_text(text)
                return
        await message.reply_text(loc.t("error.general", lang))

    @app.on_message(filters.command("loan"))
    async def loan_command(client: Client, message: Message):
        args = message.text.split()
        if len(args) < 2:
            await message.reply_text("Usage: /loan <amount>")
            return
        try:
            amount = int(args[1])
        except ValueError:
            await message.reply_text("Invalid amount.")
            return
        if message._services:
            bank_svc = message._services.get("bank")
            if bank_svc:
                result = await bank_svc.take_loan(message.from_user.id, amount)
                if result["success"]:
                    await message.reply_text(loc.t("bank.loan_taken", "en", amount=format_number(amount), date=str(result["due"])))
                else:
                    await message.reply_text(loc.t("bank.loan_exists", "en"))

    @app.on_message(filters.command("repay"))
    async def repay_command(client: Client, message: Message):
        args = message.text.split()
        if len(args) < 2:
            await message.reply_text("Usage: /repay <amount>")
            return
        try:
            amount = int(args[1])
        except ValueError:
            await message.reply_text("Invalid amount.")
            return
        if message._services:
            bank_svc = message._services.get("bank")
            eco_svc = message._services.get("economy")
            if bank_svc and eco_svc:
                result = await bank_svc.repay_loan(message.from_user.id, amount)
                if result["success"]:
                    await eco_svc.remove_coins(message.from_user.id, result["repaid"], "Loan repayment")
                    await message.reply_text(loc.t("bank.loan_repay", "en", amount=format_number(result["repaid"])))
                else:
                    await message.reply_text(loc.t("bank.loan_failed", "en"))

    @app.on_callback_query(filters.regex("^bank_info$"))
    async def bank_info_callback(client: Client, callback_query: CallbackQuery):
        user = callback_query.from_user
        lang = "en"
        if callback_query._services:
            bank_svc = callback_query._services.get("bank")
            if bank_svc:
                info = await bank_svc.get_balance(user.id)
                text = (
                    f"🏦 **Bank Info**\n\n"
                    f"💰 Balance: {format_number(info['balance'])}\n"
                    f"📈 Interest Rate: {info['interest_rate']*100}%\n"
                )
                if info["loan_amount"] > 0:
                    text += f"📄 Loan: {format_number(info['loan_amount'])}\n"
                try:
                    await callback_query.message.edit_text(text, reply_markup=InlineKeyboards.back_button("economy", lang))
                except Exception:
                    await callback_query.message.reply_text(text, reply_markup=InlineKeyboards.back_button("economy", lang))
        await callback_query.answer()

    @app.on_callback_query(filters.regex("^loans$"))
    async def loans_callback(client: Client, callback_query: CallbackQuery):
        lang = "en"
        text = "📄 **Loans**\n\nUse /loan <amount> to take a loan\nUse /repay <amount> to repay"
        try:
            await callback_query.message.edit_text(text, reply_markup=InlineKeyboards.back_button("economy", lang))
        except Exception:
            await callback_query.message.reply_text(text, reply_markup=InlineKeyboards.back_button("economy", lang))
        await callback_query.answer()

    @app.on_callback_query(filters.regex("^transactions$"))
    async def transactions_callback(client: Client, callback_query: CallbackQuery):
        user = callback_query.from_user
        lang = "en"
        if callback_query._services:
            eco_svc = callback_query._services.get("economy")
            if eco_svc:
                txs = await eco_svc.get_transactions(user.id, 10)
                text = "📜 **Recent Transactions**\n\n"
                if txs:
                    for tx in txs:
                        icon = "💰" if tx.transaction_type == "credit" else "💸" if tx.transaction_type == "debit" else "📋"
                        text += f"{icon} {tx.description}: {format_number(tx.amount)} coins\n"
                else:
                    text += "No transactions yet."
                try:
                    await callback_query.message.edit_text(text, reply_markup=InlineKeyboards.back_button("economy", lang))
                except Exception:
                    await callback_query.message.reply_text(text, reply_markup=InlineKeyboards.back_button("economy", lang))
        await callback_query.answer()
