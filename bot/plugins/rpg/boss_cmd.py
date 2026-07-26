from __future__ import annotations

import random
from pyrogram import Client, filters
from pyrogram.types import CallbackQuery, Message

from bot.core import loc
from bot.keyboards.inline import InlineKeyboards
from bot.utils.helpers import format_number, calc_damage


BOSSES = [
    {"name": "Goblin King", "hp": 100, "atk": 10, "def": 5, "xp": 100, "coins": 200, "min_level": 1},
    {"name": "Troll Warlord", "hp": 250, "atk": 25, "def": 15, "xp": 300, "coins": 500, "min_level": 5},
    {"name": "Vampire Lord", "hp": 500, "atk": 40, "def": 25, "xp": 600, "coins": 1000, "min_level": 10},
    {"name": "Dragon", "hp": 1000, "atk": 80, "def": 50, "xp": 1200, "coins": 2500, "min_level": 20},
    {"name": "Demon King", "hp": 2000, "atk": 150, "def": 100, "xp": 3000, "coins": 5000, "min_level": 30},
]


def register(app: Client):
    @app.on_message(filters.command("boss"))
    async def boss_command(client: Client, message: Message):
        user = message.from_user
        lang = "en"
        if message._services:
            user_svc = message._services.get("user")
            eco_svc = message._services.get("economy")
            ach_svc = message._services.get("achievement")
            if user_svc and eco_svc:
                db_user = await user_svc.get_user(user.id)
                if not db_user:
                    await message.reply_text(loc.t("error.general", lang))
                    return
                available = [b for b in BOSSES if db_user.level >= b["min_level"]]
                if not available:
                    await message.reply_text("No bosses available for your level.")
                    return
                boss = random.choice(available)
                player_atk = db_user.stats.get("strength", 5)
                player_def = db_user.stats.get("defense", 5)
                player_hp = 100 + db_user.level * 10
                boss_hp = boss["hp"]
                turn = 0
                while player_hp > 0 and boss_hp > 0 and turn < 50:
                    dmg = calc_damage(player_atk, boss["def"], db_user.stats.get("luck", 5))
                    boss_hp -= dmg
                    if boss_hp > 0:
                        boss_dmg = calc_damage(boss["atk"], player_def)
                        player_hp -= boss_dmg
                    turn += 1
                if boss_hp <= 0:
                    await eco_svc.add_coins(user.id, boss["coins"], f"Boss: {boss['name']}")
                    result = await user_svc.add_xp(user.id, boss["xp"])
                    await user_svc.increment_field(user.id, "bosses_defeated")
                    if ach_svc:
                        await ach_svc.check_achievement(user.id, "boss_10")
                    text = loc.t("rpg.boss_win", lang, boss=boss["name"], coins=format_number(boss["coins"]), xp=boss["xp"])
                    if result["leveled_up"]:
                        text += f"\n🎉 {loc.t('rpg.level_up', lang, level=result['new_level'])}"
                    await message.reply_text(text)
                else:
                    await message.reply_text(loc.t("rpg.boss_lose", lang, boss=boss["name"]))

    @app.on_callback_query(filters.regex("^boss$"))
    async def boss_callback(client: Client, callback_query: CallbackQuery):
        lang = "en"
        text = loc.t("rpg.boss_title", lang) + "\n\nUse /boss to challenge a boss."
        try:
            await callback_query.message.edit_text(text, reply_markup=InlineKeyboards.back_button("rpg_menu", lang))
        except Exception:
            await callback_query.message.reply_text(text, reply_markup=InlineKeyboards.back_button("rpg_menu", lang))
        await callback_query.answer()
