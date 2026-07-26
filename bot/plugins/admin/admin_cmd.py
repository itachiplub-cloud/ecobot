from __future__ import annotations

from pyrogram import Client, filters
from pyrogram.types import CallbackQuery, Message

from bot.core import loc
from bot.keyboards.inline import InlineKeyboards
from config import settings
from bot.utils.helpers import format_number


def register(app: Client):
    @app.on_message(filters.command("admin") & filters.user(settings.OWNER_ID))
    async def admin_command(client: Client, message: Message):
        lang = "en"
        await message.reply_text(loc.t("admin.title", lang), reply_markup=InlineKeyboards.admin_panel(lang))

    @app.on_callback_query(filters.regex("^admin_"))
    async def admin_callback(client: Client, callback_query: CallbackQuery):
        user = callback_query.from_user
        lang = "en"
        if user.id != settings.OWNER_ID:
            await callback_query.answer(loc.t("error.permission_denied", lang), show_alert=True)
            return
        data = callback_query.data
        if data == "admin_broadcast":
            await callback_query.message.edit_text(loc.t("admin.broadcast_prompt", lang), reply_markup=InlineKeyboards.back_button("admin", lang))
        elif data == "admin_economy":
            text = "💰 **Economy Control**\n\n/adminreset - Reset all balances\n/adminadd <user_id> <amount> - Add coins\n/adminset <user_id> <amount> - Set balance"
            await callback_query.message.edit_text(text, reply_markup=InlineKeyboards.back_button("admin", lang))
        elif data == "admin_users":
            text = "👥 **User Management**\n\n/adminban <user_id> - Ban user\n/adminunban <user_id> - Unban user"
            await callback_query.message.edit_text(text, reply_markup=InlineKeyboards.back_button("admin", lang))
        elif data == "admin_premium":
            text = "👑 **Premium Control**\n\n/adminpremium <user_id> <days> - Grant premium\n/adminremovepremium <user_id> - Remove premium"
            await callback_query.message.edit_text(text, reply_markup=InlineKeyboards.back_button("admin", lang))
        elif data == "admin_settings":
            text = "⚙️ **Bot Settings**\n\nAll settings are configurable via .env"
            await callback_query.message.edit_text(text, reply_markup=InlineKeyboards.back_button("admin", lang))
        elif data == "admin_logs":
            text = "📜 **Logs**\n\nUse /logs to view recent logs."
            await callback_query.message.edit_text(text, reply_markup=InlineKeyboards.back_button("admin", lang))
        elif data == "admin":
            text = loc.t("admin.title", lang)
            await callback_query.message.edit_text(text, reply_markup=InlineKeyboards.admin_panel(lang))
        await callback_query.answer()

    @app.on_message(filters.command("adminreset") & filters.user(settings.OWNER_ID))
    async def admin_reset_command(client: Client, message: Message):
        if message._services:
            eco_svc = message._services.get("economy")
            if eco_svc:
                await eco_svc.reset_all()
                await message.reply_text(loc.t("admin.economy_reset", "en"))

    @app.on_message(filters.command("adminadd") & filters.user(settings.OWNER_ID))
    async def admin_add_command(client: Client, message: Message):
        args = message.text.split()
        if len(args) < 3:
            await message.reply_text("Usage: /adminadd <user_id> <amount>")
            return
        try:
            target_id = int(args[1])
            amount = int(args[2])
        except ValueError:
            await message.reply_text("Invalid arguments.")
            return
        if message._services:
            eco_svc = message._services.get("economy")
            if eco_svc:
                await eco_svc.add_coins(target_id, amount, "Admin grant")
                await message.reply_text(f"✅ Added {format_number(amount)} to {target_id}")

    @app.on_message(filters.command("adminban") & filters.user(settings.OWNER_ID))
    async def admin_ban_command(client: Client, message: Message):
        args = message.text.split()
        if len(args) < 2:
            await message.reply_text("Usage: /adminban <user_id>")
            return
        try:
            target_id = int(args[1])
        except ValueError:
            await message.reply_text("Invalid user ID.")
            return
        if message._services:
            user_svc = message._services.get("user")
            if user_svc:
                await user_svc.ban_user(target_id, "Banned by admin")
                await message.reply_text(loc.t("admin.user_banned", "en", user=f"`{target_id}`"))

    @app.on_message(filters.command("adminunban") & filters.user(settings.OWNER_ID))
    async def admin_unban_command(client: Client, message: Message):
        args = message.text.split()
        if len(args) < 2:
            await message.reply_text("Usage: /adminunban <user_id>")
            return
        try:
            target_id = int(args[1])
        except ValueError:
            await message.reply_text("Invalid user ID.")
            return
        if message._services:
            user_svc = message._services.get("user")
            if user_svc:
                await user_svc.unban_user(target_id)
                await message.reply_text(loc.t("admin.user_unbanned", "en", user=f"`{target_id}`"))
