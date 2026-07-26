from __future__ import annotations

from pyrogram import Client, filters
from pyrogram.types import CallbackQuery, Message

from bot.core import loc
from bot.keyboards.inline import InlineKeyboards
from bot.utils.helpers import progress_bar, format_number


def register(app: Client):
    @app.on_message(filters.command("battlepass") | filters.command("bp"))
    async def battlepass_command(client: Client, message: Message):
        user = message.from_user
        lang = "en"
        if message._services:
            bp_svc = message._services.get("battle_pass")
            if bp_svc:
                bp = await bp_svc.get_battle_pass(user.id)
                text = (
                    f"🎫 **Battle Pass** - Season {bp.season}\n\n"
                    f"⭐ Tier: {bp.tier}/100\n"
                    f"📊 XP: {progress_bar(bp.xp, bp.xp_needed)} {bp.xp}/{bp.xp_needed}\n"
                    f"👑 Premium: {'Yes' if bp.premium else 'No'}\n"
                    f"🎯 Total XP: {format_number(bp.total_xp_earned)}"
                )
                await message.reply_text(text)
                return
        await message.reply_text(loc.t("error.general", lang))

    @app.on_callback_query(filters.regex("^battlepass$"))
    async def battlepass_callback(client: Client, callback_query: CallbackQuery):
        user = callback_query.from_user
        lang = "en"
        if callback_query._services:
            bp_svc = callback_query._services.get("battle_pass")
            if bp_svc:
                bp = await bp_svc.get_battle_pass(user.id)
                text = (
                    f"🎫 **Battle Pass** - Season {bp.season}\n\n"
                    f"⭐ Tier: {bp.tier}/100\n"
                    f"📊 XP: {progress_bar(bp.xp, bp.xp_needed)} {bp.xp}/{bp.xp_needed}\n"
                    f"👑 Premium: {'Yes' if bp.premium else 'No'}\n"
                    f"🎯 Total XP: {format_number(bp.total_xp_earned)}"
                )
                try:
                    await callback_query.message.edit_text(text, reply_markup=InlineKeyboards.back_button("profile", lang))
                except Exception:
                    await callback_query.message.reply_text(text, reply_markup=InlineKeyboards.back_button("profile", lang))
        await callback_query.answer()
