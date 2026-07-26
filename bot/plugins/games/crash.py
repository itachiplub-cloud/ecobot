from __future__ import annotations

import random
from pyrogram import Client, filters
from pyrogram.types import CallbackQuery

from bot.core import loc
from bot.keyboards.inline import InlineKeyboards
from bot.utils.helpers import format_number


def register(app: Client):
    @app.on_message(filters.command("crash"))
    async def crash_command(client: Client, message):
        args = message.text.split()
        if len(args) < 2:
            await message.reply_text("Usage: /crash <amount>\nCash out before it crashes!")
            return
        try:
            amount = int(args[1])
        except ValueError:
            await message.reply_text("Invalid amount.")
            return
        crash_point = random.uniform(1.0, 10.0)
        multiplier = round(crash_point, 2)
        user = message.from_user
        if message._services:
            eco_svc = message._services.get("economy")
            if eco_svc:
                result = await eco_svc.remove_coins(user.id, amount, "Crash bet")
                if not result["success"]:
                    await message.reply_text(loc.t("error.insufficient_funds", "en"))
                    return
                winnings = int(amount * multiplier)
                await eco_svc.add_coins(user.id, winnings, "Crash win")
                text = f"📈 **Crash**\n\nCrashed at {multiplier}x!\n💰 Won {format_number(winnings)} coins!"
                await message.reply_text(text)

    @app.on_callback_query(filters.regex("^crash$"))
    async def crash_menu(client: Client, callback_query: CallbackQuery):
        lang = "en"
        text = f"{loc.t('games.crash_title', lang)}\n\nUsage: /crash <amount>\nCash out before it crashes!"
        await callback_query.message.edit_text(text, reply_markup=InlineKeyboards.back_button("games_menu", lang))
        await callback_query.answer()
