from __future__ import annotations

import random
from pyrogram import Client, filters
from pyrogram.types import CallbackQuery, Message

from bot.core import loc
from bot.keyboards.inline import InlineKeyboards
from bot.utils.helpers import format_number

FISH_ITEMS = [
    {"name": "Old Boot", "value": 5, "chance": 0.3},
    {"name": "Seaweed", "value": 2, "chance": 0.25},
    {"name": "Small Fish", "value": 15, "chance": 0.2},
    {"name": "Big Fish", "value": 40, "chance": 0.1},
    {"name": "Goldfish", "value": 100, "chance": 0.08},
    {"name": "Treasure Chest", "value": 500, "chance": 0.05},
    {"name": "Legendary Swordfish", "value": 1000, "chance": 0.02},
]


def register(app: Client):
    @app.on_message(filters.command("fish") | filters.command("fishing"))
    async def fish_command(client: Client, message: Message):
        user = message.from_user
        lang = "en"
        if message._services:
            cd_svc = message._services.get("cooldown")
            eco_svc = message._services.get("economy")
            user_svc = message._services.get("user")
            ach_svc = message._services.get("achievement")
            if cd_svc:
                on_cd, remaining = await cd_svc.is_on_cooldown(user.id, "fish")
                if on_cd:
                    time_str = cd_svc.format_time(remaining)
                    await message.reply_text(loc.t("cooldown.active", lang, time=time_str))
                    return
            if eco_svc:
                roll = random.random()
                cumulative = 0
                caught = FISH_ITEMS[0]
                for fish in FISH_ITEMS:
                    cumulative += fish["chance"]
                    if roll <= cumulative:
                        caught = fish
                        break
                await eco_svc.add_coins(user.id, caught["value"], f"Fishing: {caught['name']}")
                if user_svc:
                    await user_svc.increment_field(user.id, "commands_used")
                if ach_svc:
                    await ach_svc.check_achievement(user.id, "fish_50")
                text = loc.t("rpg.fish_caught", lang, item=f"{caught['name']} ({format_number(caught['value'])} coins)")
                await message.reply_text(text)
                if cd_svc:
                    await cd_svc.set_cooldown(user.id, "fish", 60)
                return
        await message.reply_text(loc.t("error.general", lang))

    @app.on_callback_query(filters.regex("^fish$"))
    async def fish_callback(client: Client, callback_query: CallbackQuery):
        lang = "en"
        text = loc.t("rpg.fish_title", lang) + "\n\nUse /fish to fish."
        try:
            await callback_query.message.edit_text(text, reply_markup=InlineKeyboards.back_button("rpg_menu", lang))
        except Exception:
            await callback_query.message.reply_text(text, reply_markup=InlineKeyboards.back_button("rpg_menu", lang))
        await callback_query.answer()
