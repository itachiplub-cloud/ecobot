from __future__ import annotations

from pyrogram import Client, filters
from pyrogram.types import CallbackQuery, Message

from bot.core import loc
from bot.keyboards.inline import InlineKeyboards


def register(app: Client):
    @app.on_message(filters.command("mail"))
    async def mail_command(client: Client, message: Message):
        user = message.from_user
        lang = "en"
        if message._services:
            mail_svc = message._services.get("mail")
            if mail_svc:
                unread = await mail_svc.get_unread_count(user.id)
                mails = await mail_svc.get_mail(user.id, 10)
                text = f"📬 **Mail** ({unread} unread)\n\n"
                for m in mails:
                    read_icon = "📩" if not m.read else "📭"
                    text += f"{read_icon} **{m.subject}**\n  {m.body[:100]}...\n\n"
                if not mails:
                    text += "No mail."
                await message.reply_text(text)
                return
        await message.reply_text(loc.t("error.general", lang))

    @app.on_message(filters.command("readmail"))
    async def readmail_command(client: Client, message: Message):
        if message._services:
            mail_svc = message._services.get("mail")
            if mail_svc:
                await mail_svc.mark_read(message.from_user.id)
                await message.reply_text("✅ All mail marked as read.")
