from __future__ import annotations

from pyrogram import Client, filters
from pyrogram.types import CallbackQuery, Message, InlineKeyboardButton, InlineKeyboardMarkup

from bot.core import loc
from bot.keyboards.inline import InlineKeyboards
from bot.utils.helpers import format_number


def register(app: Client):
    @app.on_message(filters.command("leaderboard") | filters.command("lb"))
    async def leaderboard_command(client: Client, message: Message):
        lang = "en"
        text = loc.t("leaderboard.title", lang)
        kb = InlineKeyboardMarkup([
            [InlineKeyboardButton(loc.t("leaderboard.richest", lang), callback_data="lb_richest")],
            [InlineKeyboardButton(loc.t("leaderboard.highest_level", lang), callback_data="lb_level")],
            [InlineKeyboardButton(loc.t("leaderboard.most_xp", lang), callback_data="lb_xp")],
            [InlineKeyboardButton(loc.t("btn.back", lang), callback_data="main_menu")],
        ])
        await message.reply_text(text, reply_markup=kb)

    @app.on_callback_query(filters.regex("^leaderboard$"))
    async def leaderboard_callback(client: Client, callback_query: CallbackQuery):
        lang = "en"
        text = loc.t("leaderboard.title", lang)
        kb = InlineKeyboardMarkup([
            [InlineKeyboardButton(loc.t("leaderboard.richest", lang), callback_data="lb_richest")],
            [InlineKeyboardButton(loc.t("leaderboard.highest_level", lang), callback_data="lb_level")],
            [InlineKeyboardButton(loc.t("leaderboard.most_xp", lang), callback_data="lb_xp")],
            [InlineKeyboardButton(loc.t("btn.back", lang), callback_data="main_menu")],
        ])
        try:
            await callback_query.message.edit_text(text, reply_markup=kb)
        except Exception:
            await callback_query.message.reply_text(text, reply_markup=kb)
        await callback_query.answer()

    @app.on_callback_query(filters.regex("^lb_richest$"))
    async def lb_richest_callback(client: Client, callback_query: CallbackQuery):
        lang = "en"
        if callback_query._services:
            eco_svc = callback_query._services.get("economy")
            if eco_svc:
                richest = await eco_svc.get_richest(10)
                text = f"💰 **{loc.t('leaderboard.richest', lang)}**\n\n"
                medals = ["🥇", "🥈", "🥉"]
                for i, eco in enumerate(richest):
                    medal = medals[i] if i < 3 else f"#{i + 1}"
                    text += f"{medal} `{eco.user_id}` - 💰 {format_number(eco.wallet)}\n"
                try:
                    await callback_query.message.edit_text(text, reply_markup=InlineKeyboards.back_button("leaderboard", lang))
                except Exception:
                    await callback_query.message.reply_text(text, reply_markup=InlineKeyboards.back_button("leaderboard", lang))
        await callback_query.answer()

    @app.on_callback_query(filters.regex("^lb_level$"))
    async def lb_level_callback(client: Client, callback_query: CallbackQuery):
        lang = "en"
        if callback_query._services:
            user_svc = callback_query._services.get("user")
            if user_svc:
                top = await user_svc.get_top_users("level", 10)
                text = f"⭐ **{loc.t('leaderboard.highest_level', lang)}**\n\n"
                medals = ["🥇", "🥈", "🥉"]
                for i, u in enumerate(top):
                    medal = medals[i] if i < 3 else f"#{i + 1}"
                    text += f"{medal} `{u.user_id}` - Level {u.level}\n"
                try:
                    await callback_query.message.edit_text(text, reply_markup=InlineKeyboards.back_button("leaderboard", lang))
                except Exception:
                    await callback_query.message.reply_text(text, reply_markup=InlineKeyboards.back_button("leaderboard", lang))
        await callback_query.answer()

    @app.on_callback_query(filters.regex("^lb_xp$"))
    async def lb_xp_callback(client: Client, callback_query: CallbackQuery):
        lang = "en"
        if callback_query._services:
            user_svc = callback_query._services.get("user")
            if user_svc:
                top = await user_svc.get_top_users("xp", 10)
                text = f"📊 **{loc.t('leaderboard.most_xp', lang)}**\n\n"
                medals = ["🥇", "🥈", "🥉"]
                for i, u in enumerate(top):
                    medal = medals[i] if i < 3 else f"#{i + 1}"
                    text += f"{medal} `{u.user_id}` - {u.xp} XP\n"
                try:
                    await callback_query.message.edit_text(text, reply_markup=InlineKeyboards.back_button("leaderboard", lang))
                except Exception:
                    await callback_query.message.reply_text(text, reply_markup=InlineKeyboards.back_button("leaderboard", lang))
        await callback_query.answer()
