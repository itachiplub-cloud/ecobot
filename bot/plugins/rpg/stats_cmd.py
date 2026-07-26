from __future__ import annotations

from pyrogram import Client, filters
from pyrogram.types import CallbackQuery, Message

from bot.core import loc
from bot.keyboards.inline import InlineKeyboards
from bot.utils.helpers import format_number, progress_bar
from bot.utils.formatting import format_user_profile


def register(app: Client):
    @app.on_message(filters.command("stats"))
    async def stats_command(client: Client, message: Message):
        user = message.from_user
        lang = "en"
        if message._services:
            user_svc = message._services.get("user")
            eco_svc = message._services.get("economy")
            if user_svc:
                db_user = await user_svc.get_user(user.id)
                if db_user:
                    text = format_user_profile(db_user, await eco_svc.get_balance(user.id) if eco_svc else None, lang)
                    await message.reply_text(text)
                    return
        await message.reply_text(loc.t("error.general", lang))

    @app.on_callback_query(filters.regex("^rpg_stats$"))
    async def rpg_stats_callback(client: Client, callback_query: CallbackQuery):
        user = callback_query.from_user
        lang = "en"
        if callback_query._services:
            user_svc = callback_query._services.get("user")
            eco_svc = callback_query._services.get("economy")
            if user_svc:
                db_user = await user_svc.get_user(user.id)
                if db_user:
                    text = format_user_profile(db_user, await eco_svc.get_balance(user.id) if eco_svc else None, lang)
                    try:
                        await callback_query.message.edit_text(text, reply_markup=InlineKeyboards.back_button("rpg_menu", lang))
                    except Exception:
                        await callback_query.message.reply_text(text, reply_markup=InlineKeyboards.back_button("rpg_menu", lang))
                    await callback_query.answer()
                    return
        await callback_query.answer()
