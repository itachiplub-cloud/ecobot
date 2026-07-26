from __future__ import annotations

from pyrogram import Client, filters
from pyrogram.types import Message, CallbackQuery

from bot.core import loc
from bot.keyboards.inline import InlineKeyboards
from bot.utils.helpers import format_number


def register(app: Client):

    @app.on_message(filters.command("banklb") | filters.command("bankleaderboard"))
    async def bank_leaderboard_command(client: Client, message: Message):
        services = getattr(message, '_services', None)
        if not services:
            return
        eco_svc = services.get("economy")
        if eco_svc:
            top_users = await eco_svc.get_richest(10)
            text = "🏦 **Bank Leaderboard** — Richest\n\n"
            medals = ["🥇", "🥈", "🥉"]
            for i, entry in enumerate(top_users):
                medal = medals[i] if i < 3 else f"#{i+1}"
                text += f"{medal} `{entry['user_id']}` — {format_number(entry.get('total', entry.get('wallet', 0)))} coins\n"
            if not top_users:
                text += "No data yet."
            kb = InlineKeyboards.bank_leaderboard()
            await message.reply_text(text, reply_markup=kb)

    @app.on_callback_query(filters.regex(r"^lb_bank_richest$"))
    async def lb_bank_richest_callback(client: Client, callback: CallbackQuery):
        services = getattr(callback, '_services', None) or getattr(callback.message, '_services', None)
        if not services:
            return
        eco_svc = services.get("economy")
        if eco_svc:
            top_users = await eco_svc.get_richest(10)
            text = "💰 **Richest Players**\n\n"
            medals = ["🥇", "🥈", "🥉"]
            for i, entry in enumerate(top_users):
                medal = medals[i] if i < 3 else f"#{i+1}"
                text += f"{medal} `{entry['user_id']}` — {format_number(entry.get('total', entry.get('wallet', 0)))} coins\n"
            if not top_users:
                text += "No data yet."
            await callback.message.edit_text(text, reply_markup=InlineKeyboards.bank_leaderboard())

    @app.on_callback_query(filters.regex(r"^lb_bank_savers$"))
    async def lb_bank_savers_callback(client: Client, callback: CallbackQuery):
        services = getattr(callback, '_services', None) or getattr(callback.message, '_services', None)
        if not services:
            return
        eco_svc = services.get("economy")
        if eco_svc:
            top_users = await eco_svc.get_top_savers(10)
            text = "🏦 **Top Savers**\n\n"
            medals = ["🥇", "🥈", "🥉"]
            for i, entry in enumerate(top_users):
                medal = medals[i] if i < 3 else f"#{i+1}"
                text += f"{medal} `{entry['user_id']}` — {format_number(entry.get('bank', 0))} coins\n"
            if not top_users:
                text += "No data yet."
            await callback.message.edit_text(text, reply_markup=InlineKeyboards.bank_leaderboard())

    @app.on_callback_query(filters.regex(r"^lb_bank_loans$"))
    async def lb_bank_loans_callback(client: Client, callback: CallbackQuery):
        await callback.answer("Loan leaderboard coming soon!", show_alert=True)

    @app.on_callback_query(filters.regex(r"^lb_bank_investments$"))
    async def lb_bank_investments_callback(client: Client, callback: CallbackQuery):
        await callback.answer("Investment leaderboard coming soon!", show_alert=True)
