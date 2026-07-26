from __future__ import annotations

from pyrogram import Client, filters
from pyrogram.types import CallbackQuery

from bot.core import loc
from bot.keyboards.inline import InlineKeyboards
from bot.utils.formatting import format_user_profile


def register(app: Client):
    @app.on_message(filters.command("profile"))
    async def profile_command(client: Client, message):
        user = message.from_user
        lang = "en"
        if message._services:
            user_svc = message._services.get("user")
            eco_svc = message._services.get("economy")
            if user_svc:
                db_user = await user_svc.get_or_create(user.id)
                economy = await eco_svc.get_balance(user.id) if eco_svc else None
                text = format_user_profile(db_user, economy, lang)
            else:
                text = loc.t("profile.no_user", lang)
        else:
            text = loc.t("error.general", lang)
        kb = InlineKeyboards.profile_menu(lang)
        await message.reply_text(text, reply_markup=kb)

    @app.on_callback_query(filters.regex("^profile$"))
    async def profile_callback(client: Client, callback_query: CallbackQuery):
        user = callback_query.from_user
        lang = "en"
        if callback_query._services:
            user_svc = callback_query._services.get("user")
            eco_svc = callback_query._services.get("economy")
            if user_svc:
                db_user = await user_svc.get_or_create(user.id)
                economy = await eco_svc.get_balance(user.id) if eco_svc else None
                text = format_user_profile(db_user, economy, lang)
            else:
                text = loc.t("profile.no_user", lang)
        else:
            text = loc.t("error.general", lang)
        kb = InlineKeyboards.profile_menu(lang)
        try:
            await callback_query.message.edit_text(text, reply_markup=kb)
        except Exception:
            await callback_query.message.reply_text(text, reply_markup=kb)
        await callback_query.answer()
