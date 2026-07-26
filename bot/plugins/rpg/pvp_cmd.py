from __future__ import annotations

import random
from pyrogram import Client, filters
from pyrogram.types import CallbackQuery, Message

from bot.core import loc
from bot.keyboards.inline import InlineKeyboards
from bot.utils.helpers import calc_damage


def register(app: Client):
    @app.on_message(filters.command("pvp"))
    async def pvp_command(client: Client, message: Message):
        if not message.reply_to_message:
            await message.reply_text("Reply to a user with /pvp to challenge them.")
            return
        attacker = message.from_user
        defender = message.reply_to_message.from_user
        if defender.id == attacker.id:
            await message.reply_text("You can't fight yourself!")
            return
        if message._services:
            user_svc = message._services.get("user")
            eco_svc = message._services.get("economy")
            ach_svc = message._services.get("achievement")
            if user_svc:
                att_user = await user_svc.get_user(attacker.id)
                def_user = await user_svc.get_user(defender.id)
                if not att_user or not def_user:
                    await message.reply_text(loc.t("error.general", "en"))
                    return
                att_atk = att_user.stats.get("strength", 5)
                att_def = att_user.stats.get("defense", 5)
                att_luck = att_user.stats.get("luck", 5)
                def_atk = def_user.stats.get("strength", 5)
                def_def = def_user.stats.get("defense", 5)
                att_hp = 100 + att_user.level * 10
                def_hp = 100 + def_user.level * 10
                turn = 0
                while att_hp > 0 and def_hp > 0 and turn < 30:
                    dmg = calc_damage(att_atk, def_def, att_luck)
                    def_hp -= dmg
                    if def_hp > 0:
                        dmg2 = calc_damage(def_atk, att_def)
                        att_hp -= dmg2
                    turn += 1
                if def_hp <= 0:
                    await user_svc.increment_field(attacker.id, "commands_used")
                    if ach_svc:
                        await ach_svc.check_achievement(attacker.id, "pvp_10")
                    await message.reply_text(loc.t("rpg.pvp_win", "en", opponent=defender.first_name))
                elif att_hp <= 0:
                    await message.reply_text(loc.t("rpg.pvp_lose", "en", opponent=defender.first_name))
                else:
                    await message.reply_text(loc.t("rpg.pvp_draw", "en"))

    @app.on_callback_query(filters.regex("^pvp$"))
    async def pvp_callback(client: Client, callback_query: CallbackQuery):
        lang = "en"
        text = "⚔️ **PvP**\n\nReply to a user with /pvp to challenge them."
        try:
            await callback_query.message.edit_text(text, reply_markup=InlineKeyboards.back_button("rpg_menu", lang))
        except Exception:
            await callback_query.message.reply_text(text, reply_markup=InlineKeyboards.back_button("rpg_menu", lang))
        await callback_query.answer()
