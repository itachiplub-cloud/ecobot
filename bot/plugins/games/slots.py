from __future__ import annotations

import random
from pyrogram import Client, filters
from pyrogram.types import CallbackQuery

from bot.core import loc
from bot.keyboards.inline import InlineKeyboards
from bot.utils.helpers import format_number

SLOTS = ["🍒", "🍋", "🍊", "🍇", "🍉", "💎", "7️⃣"]
WEIGHTS = [25, 20, 20, 15, 10, 5, 5]


def register(app: Client):
    @app.on_message(filters.command("slots"))
    async def slots_command(client: Client, message):
        args = message.text.split()
        if len(args) < 2:
            await message.reply_text("Usage: /slots <amount>")
            return
        try:
            amount = int(args[1])
        except ValueError:
            await message.reply_text("Invalid amount.")
            return
        await _play_slots(message, amount)

    @app.on_callback_query(filters.regex("^slots$"))
    async def slots_callback(client: Client, callback_query: CallbackQuery):
        lang = "en"
        text = f"{loc.t('games.slots_title', lang)}\n\nUsage: /slots <amount>"
        await callback_query.message.edit_text(text, reply_markup=InlineKeyboards.back_button("games_menu", lang))
        await callback_query.answer()


async def _play_slots(message, amount: int):
    lang = "en"
    user = message.from_user
    if message._services:
        eco_svc = message._services.get("economy")
        user_svc = message._services.get("user")
        ach_svc = message._services.get("achievement")
        if eco_svc:
            result = await eco_svc.remove_coins(user.id, amount, "Slots bet")
            if not result["success"]:
                await message.reply_text(loc.t("error.insufficient_funds", lang))
                return
            s1 = random.choices(SLOTS, WEIGHTS, k=1)[0]
            s2 = random.choices(SLOTS, WEIGHTS, k=1)[0]
            s3 = random.choices(SLOTS, WEIGHTS, k=1)[0]
            display = f"[ {s1} | {s2} | {s3} ]"
            if s1 == s2 == s3:
                multiplier = 10 if s1 == "💎" else 7 if s1 == "7️⃣" else 5
                winnings = amount * multiplier
                await eco_svc.add_coins(user.id, winnings, "Slots jackpot")
                if user_svc:
                    await user_svc.increment_field(user.id, "games_played")
                if ach_svc:
                    await ach_svc.check_achievement(user.id, "games_10")
                await message.reply_text(f"{display}\n\n🎉 JACKPOT! Won {format_number(winnings)} coins!")
            elif s1 == s2 or s2 == s3 or s1 == s3:
                winnings = amount * 2
                await eco_svc.add_coins(user.id, winnings, "Slots win")
                if user_svc:
                    await user_svc.increment_field(user.id, "games_played")
                if ach_svc:
                    await ach_svc.check_achievement(user.id, "games_10")
                await message.reply_text(f"{display}\n\n🎉 Won {format_number(winnings)} coins!")
            else:
                if user_svc:
                    await user_svc.increment_field(user.id, "games_played")
                if ach_svc:
                    await ach_svc.check_achievement(user.id, "games_10")
                await message.reply_text(f"{display}\n\n😔 Lost {format_number(amount)} coins.")
