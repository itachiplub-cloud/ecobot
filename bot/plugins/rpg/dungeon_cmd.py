from __future__ import annotations

import random
from pyrogram import Client, filters
from pyrogram.types import CallbackQuery, Message

from bot.core import loc
from bot.keyboards.inline import InlineKeyboards
from bot.utils.helpers import format_number


DUNGEONS = [
    {"name": "Goblin Cave", "min_level": 1, "xp": 50, "coins": 100, "fail_chance": 0.3},
    {"name": "Dark Forest", "min_level": 5, "xp": 150, "coins": 300, "fail_chance": 0.35},
    {"name": "Shadow Crypt", "min_level": 10, "xp": 300, "coins": 600, "fail_chance": 0.4},
    {"name": "Dragon Keep", "min_level": 20, "xp": 600, "coins": 1200, "fail_chance": 0.45},
    {"name": "Demon Realm", "min_level": 30, "xp": 1000, "coins": 2500, "fail_chance": 0.5},
]


def register(app: Client):
    @app.on_message(filters.command("dungeon"))
    async def dungeon_command(client: Client, message: Message):
        user = message.from_user
        lang = "en"
        if message._services:
            user_svc = message._services.get("user")
            eco_svc = message._services.get("economy")
            if user_svc and eco_svc:
                db_user = await user_svc.get_user(user.id)
                if not db_user:
                    await message.reply_text(loc.t("error.general", lang))
                    return
                available = [d for d in DUNGEONS if db_user.level >= d["min_level"]]
                if not available:
                    await message.reply_text("No dungeons available for your level.")
                    return
                dungeon = random.choice(available)
                if random.random() < dungeon["fail_chance"]:
                    await message.reply_text(loc.t("rpg.dungeon_fail", lang))
                else:
                    await eco_svc.add_coins(user.id, dungeon["coins"], f"Dungeon: {dungeon['name']}")
                    result = await user_svc.add_xp(user.id, dungeon["xp"])
                    text = loc.t("rpg.dungeon_clear", lang, coins=format_number(dungeon["coins"]), xp=dungeon["xp"])
                    if result["leveled_up"]:
                        text += f"\n🎉 {loc.t('rpg.level_up', lang, level=result['new_level'])}"
                    await message.reply_text(text)

    @app.on_callback_query(filters.regex("^dungeon$"))
    async def dungeon_callback(client: Client, callback_query: CallbackQuery):
        lang = "en"
        text = loc.t("rpg.dungeon_title", lang) + "\n\nUse /dungeon to enter."
        try:
            await callback_query.message.edit_text(text, reply_markup=InlineKeyboards.back_button("rpg_menu", lang))
        except Exception:
            await callback_query.message.reply_text(text, reply_markup=InlineKeyboards.back_button("rpg_menu", lang))
        await callback_query.answer()
