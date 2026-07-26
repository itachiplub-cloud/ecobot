from __future__ import annotations

from pyrogram import Client, filters
from pyrogram.types import CallbackQuery

from bot.core import loc
from bot.keyboards.inline import InlineKeyboards


def register(app: Client):
    @app.on_message(filters.command("settings"))
    async def settings_command(client: Client, message):
        lang = "en"
        text = loc.t("btn.settings", lang)
        kb = InlineKeyboards.settings_menu(lang)
        await message.reply_text(text, reply_markup=kb)

    @app.on_callback_query(filters.regex("^settings$"))
    async def settings_callback(client: Client, callback_query: CallbackQuery):
        lang = "en"
        text = loc.t("btn.settings", lang)
        kb = InlineKeyboards.settings_menu(lang)
        try:
            await callback_query.message.edit_text(text, reply_markup=kb)
        except Exception:
            await callback_query.message.reply_text(text, reply_markup=kb)
        await callback_query.answer()

    @app.on_callback_query(filters.regex("^toggle_notifications$"))
    async def toggle_notifications(client: Client, callback_query: CallbackQuery):
        user = callback_query.from_user
        if callback_query._services:
            user_svc = callback_query._services.get("user")
            if user_svc:
                db_user = await user_svc.get_user(user.id)
                if db_user:
                    new_val = not db_user.settings.get("notifications", True)
                    await user_svc.update_user(user.id, settings={"notifications": new_val, **db_user.settings})
                    status = "ON" if new_val else "OFF"
                    await callback_query.answer(f"Notifications: {status}", show_alert=True)
                    return
        await callback_query.answer()

    @app.on_callback_query(filters.regex("^toggle_private$"))
    async def toggle_private(client: Client, callback_query: CallbackQuery):
        user = callback_query.from_user
        if callback_query._services:
            user_svc = callback_query._services.get("user")
            if user_svc:
                db_user = await user_svc.get_user(user.id)
                if db_user:
                    new_val = not db_user.settings.get("private_profile", False)
                    await user_svc.update_user(user.id, settings={"private_profile": new_val, **db_user.settings})
                    status = "ON" if new_val else "OFF"
                    await callback_query.answer(f"Private Profile: {status}", show_alert=True)
                    return
        await callback_query.answer()
