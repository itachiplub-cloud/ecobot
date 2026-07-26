from __future__ import annotations

from pyrogram import Client, filters
from pyrogram.types import CallbackQuery, Message

from bot.core import loc
from bot.keyboards.inline import InlineKeyboards
from bot.utils.helpers import format_number


def register(app: Client):
    @app.on_message(filters.command("transfer") | filters.command("pay"))
    async def transfer_command(client: Client, message: Message):
        user = message.from_user
        lang = "en"
        args = message.text.split()
        if len(args) < 3:
            usage = "Usage: /transfer @username amount\nor reply to a user with /transfer amount"
            await message.reply_text(usage)
            return
        if message.reply_to_message:
            target_id = message.reply_to_message.from_user.id
            try:
                amount = int(args[1])
            except ValueError:
                await message.reply_text(loc.t("error.invalid_input", lang))
                return
        else:
            target_username = args[1].lstrip("@")
            try:
                target_user = await client.get_users(target_username)
                target_id = target_user.id
            except Exception:
                await message.reply_text(loc.t("error.user_not_found", lang))
                return
            try:
                amount = int(args[2])
            except ValueError:
                await message.reply_text(loc.t("error.invalid_input", lang))
                return
        if target_id == user.id:
            await message.reply_text("❌ You can't transfer to yourself.")
            return
        if message._services:
            eco_svc = message._services.get("economy")
            if eco_svc:
                result = await eco_svc.transfer(user.id, target_id, amount)
                if result["success"]:
                    text = loc.t("economy.transfer_success", lang, amount=format_number(amount), user=f"`{target_id}`")
                    await message.reply_text(text)
                else:
                    text = loc.t("economy.transfer_failed", lang)
                    await message.reply_text(text)
                return
        await message.reply_text(loc.t("error.general", lang))

    @app.on_callback_query(filters.regex("^transfer$"))
    async def transfer_callback(client: Client, callback_query: CallbackQuery):
        lang = "en"
        text = "💸 **Transfer**\n\nReply to a user with:\n/transfer <amount>\n\nor use:\n/transfer @username <amount>"
        await callback_query.message.edit_text(text, reply_markup=InlineKeyboards.back_button("economy", lang))
        await callback_query.answer()
