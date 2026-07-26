from __future__ import annotations

import random
from pyrogram import Client, filters
from pyrogram.types import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup

from bot.core import loc
from bot.keyboards.inline import InlineKeyboards
from bot.utils.helpers import format_number


def register(app: Client):
    @app.on_message(filters.command("roulette") | filters.command("rl"))
    async def roulette_command(client: Client, message):
        args = message.text.split()
        if len(args) < 3:
            await message.reply_text("Usage: /roulette <bet> <choice>\nChoices: red, black, green, or a number 0-36")
            return
        try:
            bet = int(args[1])
        except ValueError:
            await message.reply_text("Invalid bet.")
            return
        choice = args[2].lower()
        await _play_roulette(message, bet, choice)

    @app.on_callback_query(filters.regex("^roulette$"))
    async def roulette_menu(client: Client, callback_query: CallbackQuery):
        lang = "en"
        text = f"{loc.t('games.roulette_title', lang)}\n\nUsage: /roulette <bet> <choice>\nChoices: red, black, green, or a number 0-36"
        await callback_query.message.edit_text(text, reply_markup=InlineKeyboards.back_button("games_menu", lang))
        await callback_query.answer()


RED_NUMBERS = {1, 3, 5, 7, 9, 12, 14, 16, 18, 19, 21, 23, 25, 27, 30, 32, 34, 36}
BLACK_NUMBERS = {2, 4, 6, 8, 10, 11, 13, 15, 17, 20, 22, 24, 26, 28, 29, 31, 33, 35}


async def _play_roulette(message, bet: int, choice: str):
    lang = "en"
    user = message.from_user
    if message._services:
        eco_svc = message._services.get("economy")
        user_svc = message._services.get("user")
        ach_svc = message._services.get("achievement")
        if eco_svc:
            result = await eco_svc.remove_coins(user.id, bet, "Roulette bet")
            if not result["success"]:
                await message.reply_text(loc.t("error.insufficient_funds", lang))
                return
            number = random.randint(0, 36)
            if number == 0:
                color = "green"
            elif number in RED_NUMBERS:
                color = "red"
            else:
                color = "black"
            won = False
            multiplier = 0
            if choice.isdigit() and int(choice) == number:
                won = True
                multiplier = 36
            elif choice == color:
                won = True
                multiplier = 2 if color != "green" else 14
            if won:
                winnings = bet * multiplier
                await eco_svc.add_coins(user.id, winnings, "Roulette win")
                if user_svc:
                    await user_svc.increment_field(user.id, "games_played")
                if ach_svc:
                    await ach_svc.check_achievement(user.id, "games_10")
                await message.reply_text(f"🎡 **Roulette**\n\nResult: {number} ({color})\n\n🎉 Won {format_number(winnings)} coins!")
            else:
                if user_svc:
                    await user_svc.increment_field(user.id, "games_played")
                if ach_svc:
                    await ach_svc.check_achievement(user.id, "games_10")
                await message.reply_text(f"🎡 **Roulette**\n\nResult: {number} ({color})\n\n😔 Lost {format_number(bet)} coins.")
