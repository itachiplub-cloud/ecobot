from __future__ import annotations

import random
from pyrogram import Client, filters
from pyrogram.types import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup

from bot.core import loc
from bot.keyboards.inline import InlineKeyboards
from bot.utils.helpers import format_number


def register(app: Client):
    @app.on_message(filters.command("coinflip") | filters.command("cf"))
    async def coinflip_command(client: Client, message):
        args = message.text.split()
        if len(args) < 2:
            await message.reply_text("Usage: /coinflip <amount>")
            return
        try:
            amount = int(args[1])
        except ValueError:
            await message.reply_text("Invalid amount.")
            return
        kb = InlineKeyboardMarkup([
            [
                InlineKeyboardButton("Heads", callback_data=f"cf_heads_{amount}"),
                InlineKeyboardButton("Tails", callback_data=f"cf_tails_{amount}"),
            ],
        ])
        await message.reply_text(loc.t("games.coinflip_prompt", "en"), reply_markup=kb)

    @app.on_callback_query(filters.regex(r"^cf_(heads|tails)_(\d+)$"))
    async def coinflip_callback(client: Client, callback_query: CallbackQuery):
        user = callback_query.from_user
        lang = "en"
        parts = callback_query.data.split("_")
        choice = parts[1]
        amount = int(parts[2])
        if callback_query._services:
            eco_svc = callback_query._services.get("economy")
            user_svc = callback_query._services.get("user")
            ach_svc = callback_query._services.get("achievement")
            if eco_svc:
                result = await eco_svc.remove_coins(user.id, amount, "Coinflip bet")
                if not result["success"]:
                    await callback_query.answer(loc.t("error.insufficient_funds", lang), show_alert=True)
                    return
                coin_result = random.choice(["heads", "tails"])
                if choice == coin_result:
                    winnings = amount * 2
                    await eco_svc.add_coins(user.id, winnings, "Coinflip win")
                    if user_svc:
                        await user_svc.increment_field(user.id, "games_played")
                    if ach_svc:
                        await ach_svc.check_achievement(user.id, "games_10")
                    await callback_query.answer(loc.t("games.coinflip_won", lang, result=coin_result.capitalize(), amount=format_number(winnings)), show_alert=True)
                else:
                    if user_svc:
                        await user_svc.increment_field(user.id, "games_played")
                    if ach_svc:
                        await ach_svc.check_achievement(user.id, "games_10")
                    await callback_query.answer(loc.t("games.coinflip_lost", lang, result=coin_result.capitalize(), amount=format_number(amount)), show_alert=True)
        else:
            await callback_query.answer()

    @app.on_callback_query(filters.regex("^coinflip$"))
    async def coinflip_menu(client: Client, callback_query: CallbackQuery):
        lang = "en"
        text = f"{loc.t('games.coinflip_title', lang)}\n\nUsage: /coinflip <amount>\n\nChoose Heads or Tails!"
        await callback_query.message.edit_text(text, reply_markup=InlineKeyboards.back_button("games_menu", lang))
        await callback_query.answer()
