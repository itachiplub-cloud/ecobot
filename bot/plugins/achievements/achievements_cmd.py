from __future__ import annotations

from pyrogram import Client, filters
from pyrogram.types import CallbackQuery, Message

from bot.core import loc
from bot.keyboards.inline import InlineKeyboards
from bot.utils.helpers import progress_bar


def register(app: Client):
    @app.on_message(filters.command("achievements") | filters.command("ach"))
    async def achievements_command(client: Client, message: Message):
        user = message.from_user
        lang = "en"
        if message._services:
            ach_svc = message._services.get("achievement")
            if ach_svc:
                achievements = await ach_svc.get_user_achievements(user.id)
                all_achs = await ach_svc.get_all_achievements()
                completed = await ach_svc.get_completed_count(user.id)
                text = loc.t("achievement.title", lang) + f" ({completed}/{len(all_achs)})\n\n"
                for ach_id, ach_info in all_achs.items():
                    user_ach = next((a for a in achievements if a.achievement_id == ach_id), None)
                    if user_ach and user_ach.completed:
                        text += f"✅ {ach_info['name']}: {ach_info['description']}\n"
                    elif user_ach:
                        prog = progress_bar(user_ach.progress, user_ach.max_progress)
                        text += f"⏳ {ach_info['name']}: {prog} ({user_ach.progress}/{user_ach.max_progress})\n"
                    else:
                        text += f"🔒 {ach_info['name']}\n"
                await message.reply_text(text)
                return
        await message.reply_text(loc.t("error.general", lang))

    @app.on_callback_query(filters.regex("^achievements$"))
    async def achievements_callback(client: Client, callback_query: CallbackQuery):
        user = callback_query.from_user
        lang = "en"
        if callback_query._services:
            ach_svc = callback_query._services.get("achievement")
            if ach_svc:
                achievements = await ach_svc.get_user_achievements(user.id)
                all_achs = await ach_svc.get_all_achievements()
                completed = await ach_svc.get_completed_count(user.id)
                text = loc.t("achievement.title", lang) + f" ({completed}/{len(all_achs)})\n\n"
                for ach_id, ach_info in list(all_achs.items())[:15]:
                    user_ach = next((a for a in achievements if a.achievement_id == ach_id), None)
                    if user_ach and user_ach.completed:
                        text += f"✅ {ach_info['name']}\n"
                    elif user_ach:
                        prog = progress_bar(user_ach.progress, user_ach.max_progress)
                        text += f"⏳ {ach_info['name']}: {prog}\n"
                    else:
                        text += f"🔒 {ach_info['name']}\n"
                try:
                    await callback_query.message.edit_text(text, reply_markup=InlineKeyboards.back_button("profile", lang))
                except Exception:
                    await callback_query.message.reply_text(text, reply_markup=InlineKeyboards.back_button("profile", lang))
        await callback_query.answer()
