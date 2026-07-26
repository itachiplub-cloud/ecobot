from __future__ import annotations

import random
from pyrogram import Client, filters
from pyrogram.types import CallbackQuery

from bot.core import loc
from bot.keyboards.inline import InlineKeyboards
from bot.utils.helpers import format_number


def register(app: Client):
    @app.on_message(filters.command("mines"))
    async def mines_command(client: Client, message):
        args = message.text.split()
        if len(args) < 2:
            await message.reply_text("Usage: /mines <amount>\nSimple mines game: avoid the mine!")
            return
        try:
            amount = int(args[1])
        except ValueError:
            await message.reply_text("Invalid amount.")
            return
        grid_size = 9
        mines_count = 3
        mines_positions = random.sample(range(grid_size), mines_count)
        safe_tiles = [i for i in range(grid_size) if i not in mines_positions]
        revealed = random.choice(safe_tiles)
        multiplier = 1.5
        winnings = int(amount * multiplier)
        user = message.from_user
        if message._services:
            eco_svc = message._services.get("economy")
            if eco_svc:
                result = await eco_svc.remove_coins(user.id, amount, "Mines bet")
                if not result["success"]:
                    await message.reply_text(loc.t("error.insufficient_funds", "en"))
                    return
                await eco_svc.add_coins(user.id, winnings, "Mines win")
                text = f"💣 **Mines**\n\nRevealed: Safe! 💚\n💰 Won {format_number(winnings)} coins!"
                await message.reply_text(text)

    @app.on_callback_query(filters.regex("^mines$"))
    async def mines_menu(client: Client, callback_query: CallbackQuery):
        lang = "en"
        text = f"{loc.t('games.mines_title', lang)}\n\nUsage: /mines <amount>\nSimple mines game: avoid the mine!"
        await callback_query.message.edit_text(text, reply_markup=InlineKeyboards.back_button("games_menu", lang))
        await callback_query.answer()
