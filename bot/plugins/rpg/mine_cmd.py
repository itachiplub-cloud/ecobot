from __future__ import annotations

import random
from pyrogram import Client, filters
from pyrogram.types import CallbackQuery, Message

from bot.core import loc
from bot.keyboards.inline import InlineKeyboards
from bot.utils.helpers import format_number

MINE_ITEMS = [
    {"name": "Stone", "value": 5, "chance": 0.3},
    {"name": "Iron Ore", "value": 20, "chance": 0.25},
    {"name": "Copper Ore", "value": 15, "chance": 0.2},
    {"name": "Gold Ore", "value": 60, "chance": 0.1},
    {"name": "Diamond", "value": 200, "chance": 0.08},
    {"name": "Emerald", "value": 300, "chance": 0.05},
    {"name": "Mythril", "value": 1000, "chance": 0.02},
]


def register(app: Client):
    @app.on_message(filters.command("mine") | filters.command("mining"))
    async def mine_command(client: Client, message: Message):
        user = message.from_user
        lang = "en"
        if message._services:
            cd_svc = message._services.get("cooldown")
            eco_svc = message._services.get("economy")
            user_svc = message._services.get("user")
            ach_svc = message._services.get("achievement")
            if cd_svc:
                on_cd, remaining = await cd_svc.is_on_cooldown(user.id, "mine")
                if on_cd:
                    time_str = cd_svc.format_time(remaining)
                    await message.reply_text(loc.t("cooldown.active", lang, time=time_str))
                    return
            if eco_svc:
                roll = random.random()
                cumulative = 0
                found = MINE_ITEMS[0]
                for item in MINE_ITEMS:
                    cumulative += item["chance"]
                    if roll <= cumulative:
                        found = item
                        break
                await eco_svc.add_coins(user.id, found["value"], f"Mining: {found['name']}")
                if user_svc:
                    await user_svc.increment_field(user.id, "commands_used")
                if ach_svc:
                    await ach_svc.check_achievement(user.id, "mine_50")
                text = loc.t("rpg.mine_found", lang, item=f"{found['name']} ({format_number(found['value'])} coins)")
                await message.reply_text(text)
                if cd_svc:
                    await cd_svc.set_cooldown(user.id, "mine", 60)
                return
        await message.reply_text(loc.t("error.general", lang))

    @app.on_callback_query(filters.regex("^mine$"))
    async def mine_callback(client: Client, callback_query: CallbackQuery):
        lang = "en"
        text = loc.t("rpg.mine_title", lang) + "\n\nUse /mine to mine."
        try:
            await callback_query.message.edit_text(text, reply_markup=InlineKeyboards.back_button("rpg_menu", lang))
        except Exception:
            await callback_query.message.reply_text(text, reply_markup=InlineKeyboards.back_button("rpg_menu", lang))
        await callback_query.answer()
