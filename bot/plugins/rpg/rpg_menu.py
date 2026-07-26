from __future__ import annotations

import random
from pyrogram import Client, filters
from pyrogram.types import CallbackQuery, Message

from bot.core import loc
from bot.keyboards.inline import InlineKeyboards
from bot.utils.helpers import format_number


def register(app: Client):
    @app.on_message(filters.command("rpg"))
    async def rpg_command(client: Client, message: Message):
        lang = "en"
        text = loc.t("rpg.title", lang)
        await message.reply_text(text, reply_markup=InlineKeyboards.rpg_menu(lang))

    @app.on_callback_query(filters.regex("^rpg_menu$"))
    async def rpg_menu_callback(client: Client, callback_query: CallbackQuery):
        lang = "en"
        text = loc.t("rpg.title", lang)
        try:
            await callback_query.message.edit_text(text, reply_markup=InlineKeyboards.rpg_menu(lang))
        except Exception:
            await callback_query.message.reply_text(text, reply_markup=InlineKeyboards.rpg_menu(lang))
        await callback_query.answer()
