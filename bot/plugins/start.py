from __future__ import annotations

from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton

from config import settings
from bot.core import loc
from bot.keyboards.inline import InlineKeyboards
from bot.utils.helpers import format_number


def register(app: Client):
    @app.on_message(filters.command("start") & filters.private)
    async def start_private(client: Client, message: Message):
        user = message.from_user
        lang = "en"
        if message._services:
            user_svc = message._services.get("user")
            eco_svc = message._services.get("economy")
            if user_svc and user:
                await user_svc.get_or_create(user.id, username=user.username, first_name=user.first_name)
            balance = 0
            if eco_svc and user:
                bal = await eco_svc.get_balance(user.id)
                balance = bal.get("total", 0)
            if user_svc and user:
                db_user = await user_svc.get_user(user.id)
                level = db_user.level if db_user else 1
            else:
                level = 1
        else:
            balance = settings.DEFAULT_BALANCE
            level = 1
        text = loc.t("start.private", lang, user=user.first_name, balance=format_number(balance), level=level)
        kb = InlineKeyboards.main_menu(lang)
        await message.reply_text(text, reply_markup=kb)

    @app.on_message(filters.command("start") & filters.group)
    async def start_group(client: Client, message: Message):
        lang = "en"
        chat = message.chat
        member_count = 0
        try:
            member_count = await client.get_chat_members_count(chat.id)
        except Exception:
            pass
        owner = "Unknown"
        try:
            member = await client.get_chat_member(chat.id, message.from_user.id)
            owner = message.from_user.first_name
        except Exception:
            pass
        text = loc.t("start.group", lang, group_name=chat.title, owner=owner, player_count=member_count)
        kb = InlineKeyboardMarkup([
            [InlineKeyboardButton(loc.t("btn.help", lang), callback_data="help")],
            [InlineKeyboardButton(loc.t("btn.updates", lang), url="https://t.me/updates")],
        ])
        await message.reply_text(text, reply_markup=kb)

    @app.on_callback_query(filters.regex("^close$"))
    async def close_callback(client: Client, callback_query):
        try:
            await callback_query.message.delete()
        except Exception:
            pass
        await callback_query.answer()

    @app.on_callback_query(filters.regex("^noop$"))
    async def noop_callback(client: Client, callback_query):
        await callback_query.answer()
