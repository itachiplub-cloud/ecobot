from __future__ import annotations

from pyrogram import Client, filters
from pyrogram.types import CallbackQuery

from bot.core import loc
from bot.keyboards.inline import InlineKeyboards
from bot.utils.formatting import format_balance


def register(app: Client):
    @app.on_message(filters.command("balance") | filters.command("bal"))
    async def balance_command(client: Client, message):
        user = message.from_user
        lang = "en"
        if message._services:
            eco_svc = message._services.get("economy")
            if eco_svc:
                bal = await eco_svc.get_balance(user.id)
                text = f"{loc.t('economy.balance_title', lang)}\n\n{format_balance(bal['wallet'], bal['bank'], lang)}"
            else:
                text = loc.t("error.general", lang)
        else:
            text = loc.t("error.general", lang)
        kb = InlineKeyboards.economy_menu(lang)
        await message.reply_text(text, reply_markup=kb)

    @app.on_callback_query(filters.regex("^balance$"))
    async def balance_callback(client: Client, callback_query: CallbackQuery):
        user = callback_query.from_user
        lang = "en"
        if callback_query._services:
            eco_svc = callback_query._services.get("economy")
            if eco_svc:
                bal = await eco_svc.get_balance(user.id)
                text = f"{loc.t('economy.balance_title', lang)}\n\n{format_balance(bal['wallet'], bal['bank'], lang)}"
            else:
                text = loc.t("error.general", lang)
        else:
            text = loc.t("error.general", lang)
        kb = InlineKeyboards.economy_menu(lang)
        try:
            await callback_query.message.edit_text(text, reply_markup=kb)
        except Exception:
            await callback_query.message.reply_text(text, reply_markup=kb)
        await callback_query.answer()

    @app.on_callback_query(filters.regex("^economy$"))
    async def economy_menu_callback(client: Client, callback_query: CallbackQuery):
        lang = "en"
        user = callback_query.from_user
        eco_svc = callback_query._services.get("economy") if callback_query._services else None
        balance_text = ""
        if eco_svc:
            bal = await eco_svc.get_balance(user.id)
            balance_text = format_balance(bal['wallet'], bal['bank'], lang)
        text = f"💰 **Economy Menu**\n\n{balance_text}"
        kb = InlineKeyboards.economy_menu(lang)
        try:
            await callback_query.message.edit_text(text, reply_markup=kb)
        except Exception:
            await callback_query.message.reply_text(text, reply_markup=kb)
        await callback_query.answer()
