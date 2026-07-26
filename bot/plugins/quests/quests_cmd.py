from __future__ import annotations

from pyrogram import Client, filters
from pyrogram.types import CallbackQuery, Message

from bot.core import loc
from bot.keyboards.inline import InlineKeyboards
from bot.utils.formatting import format_quest


def register(app: Client):
    @app.on_message(filters.command("quests") | filters.command("quest"))
    async def quests_command(client: Client, message: Message):
        user = message.from_user
        lang = "en"
        if message._services:
            quest_svc = message._services.get("quest")
            if quest_svc:
                quests = await quest_svc.get_user_quests(user.id)
                if quests:
                    text = loc.t("quest.title", lang) + "\n\n"
                    for q in quests[:5]:
                        text += format_quest(q, lang) + "\n\n"
                else:
                    text = loc.t("quest.no_quests", lang)
                await message.reply_text(text)
                return
        await message.reply_text(loc.t("error.general", lang))

    @app.on_callback_query(filters.regex("^quests$"))
    async def quests_callback(client: Client, callback_query: CallbackQuery):
        user = callback_query.from_user
        lang = "en"
        if callback_query._services:
            quest_svc = callback_query._services.get("quest")
            if quest_svc:
                quests = await quest_svc.get_user_quests(user.id)
                if quests:
                    text = loc.t("quest.title", lang) + "\n\n"
                    for q in quests[:5]:
                        text += format_quest(q, lang) + "\n\n"
                else:
                    text = loc.t("quest.no_quests", lang)
                try:
                    await callback_query.message.edit_text(text, reply_markup=InlineKeyboards.back_button("main_menu", lang))
                except Exception:
                    await callback_query.message.reply_text(text, reply_markup=InlineKeyboards.back_button("main_menu", lang))
        await callback_query.answer()
