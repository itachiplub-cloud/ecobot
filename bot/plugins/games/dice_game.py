from __future__ import annotations

import random
from pyrogram import Client, filters
from pyrogram.types import CallbackQuery

from bot.core import loc
from bot.keyboards.inline import InlineKeyboards
from bot.utils.helpers import format_number


def register(app: Client):
    @app.on_message(filters.command("dice"))
    async def dice_command(client: Client, message):
        args = message.text.split()
        if len(args) < 2:
            await message.reply_text("Usage: /dice <amount>\nYou win if you roll 4, 5, or 6.")
            return
        try:
            amount = int(args[1])
        except ValueError:
            await message.reply_text("Invalid amount.")
            return
        await _play_dice(message, amount)

    @app.on_callback_query(filters.regex("^dice_game$"))
    async def dice_menu(client: Client, callback_query: CallbackQuery):
        lang = "en"
        text = f"{loc.t('games.dice_title', lang)}\n\nUsage: /dice <amount>\nYou win if you roll 4, 5, or 6."
        await callback_query.message.edit_text(text, reply_markup=InlineKeyboards.back_button("games_menu", lang))
        await callback_query.answer()


async def _play_dice(message, bet: int):
    lang = "en"
    user = message.from_user
    if message._services:
        eco_svc = message._services.get("economy")
        user_svc = message._services.get("user")
        ach_svc = message._services.get("achievement")
        if eco_svc:
            result = await eco_svc.remove_coins(user.id, bet, "Dice bet")
            if not result["success"]:
                await message.reply_text(loc.t("error.insufficient_funds", lang))
                return
            roll = random.randint(1, 6)
            if roll >= 4:
                winnings = bet * roll
                await eco_svc.add_coins(user.id, winnings, "Dice win")
                if user_svc:
                    await user_svc.increment_field(user.id, "games_played")
                if ach_svc:
                    await ach_svc.check_achievement(user.id, "games_10")
                await message.reply_text(f"🎲 **Dice**\n\nRolled: {roll}\n\n🎉 Won {format_number(winnings)} coins!")
            else:
                if user_svc:
                    await user_svc.increment_field(user.id, "games_played")
                if ach_svc:
                    await ach_svc.check_achievement(user.id, "games_10")
                await message.reply_text(f"🎲 **Dice**\n\nRolled: {roll}\n\n😔 Lost {format_number(bet)} coins.")
