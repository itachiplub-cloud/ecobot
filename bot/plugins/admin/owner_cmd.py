from __future__ import annotations

from pyrogram import Client, filters
from pyrogram.types import Message

from bot.core import loc
from config import settings


def register(app: Client):
    @app.on_message(filters.command("addsudo") & filters.user(settings.OWNER_ID))
    async def addsudo_command(client: Client, message: Message):
        lang = "en"
        args = message.text.split()
        target_id = None
        if message.reply_to_message:
            target_id = message.reply_to_message.from_user.id
        elif len(args) >= 2:
            try:
                target_id = int(args[1])
            except ValueError:
                await message.reply_text(loc.t("owner.invalid_id", lang))
                return
        else:
            await message.reply_text("Usage: /addsudo <user_id> or reply to a user")
            return
        if message._services:
            admin_svc = message._services.get("admin")
            if admin_svc:
                await admin_svc.add_sudo(target_id, message.from_user.id)
                await message.reply_text(loc.t("owner.sudo_added", lang, user=f"`{target_id}`"))

    @app.on_message(filters.command("delsudo") & filters.user(settings.OWNER_ID))
    async def delsudo_command(client: Client, message: Message):
        lang = "en"
        args = message.text.split()
        if len(args) < 2:
            await message.reply_text("Usage: /delsudo <user_id>")
            return
        try:
            target_id = int(args[1])
        except ValueError:
            await message.reply_text(loc.t("owner.invalid_id", lang))
            return
        if message._services:
            admin_svc = message._services.get("admin")
            if admin_svc:
                await admin_svc.remove_sudo(target_id)
                await message.reply_text(loc.t("owner.sudo_removed", lang, user=f"`{target_id}`"))

    @app.on_message(filters.command("listsudo") & filters.user(settings.OWNER_ID))
    async def listsudo_command(client: Client, message: Message):
        lang = "en"
        if message._services:
            admin_svc = message._services.get("admin")
            if admin_svc:
                admins = await admin_svc.get_all_admins()
                if admins:
                    text = loc.t("owner.sudo_list", lang, list="\n".join(
                        [f"  • `{a.user_id}` ({a.role})" for a in admins]
                    ))
                else:
                    text = loc.t("owner.no_sudo", lang)
                await message.reply_text(text)

    @app.on_message(filters.command("broadcast") & filters.user(settings.OWNER_ID))
    async def broadcast_command(client: Client, message: Message):
        args = message.text.split(maxsplit=1)
        if len(args) < 2:
            await message.reply_text("Usage: /broadcast <message>")
            return
        broadcast_text = args[1]
        if message._services:
            mail_svc = message._services.get("mail")
            user_svc = message._services.get("user")
            if mail_svc and user_svc:
                count = await user_svc.count_users()
                await message.reply_text(loc.t("admin.broadcast_sent", "en", count=count))

    @app.on_message(filters.command("maintenance") & filters.user(settings.OWNER_ID))
    async def maintenance_command(client: Client, message: Message):
        args = message.text.split()
        if len(args) < 2:
            await message.reply_text("Usage: /maintenance <on/off>")
            return
        state = args[1].lower()
        if state == "on":
            await message.reply_text(loc.t("admin.maintenance_on", "en"))
        elif state == "off":
            await message.reply_text(loc.t("admin.maintenance_off", "en"))
        else:
            await message.reply_text("Usage: /maintenance <on/off>")

    @app.on_message(filters.command("reload") & filters.user(settings.OWNER_ID))
    async def reload_command(client: Client, message: Message):
        from bot.core import loc as loc_instance
        loc_instance.reload()
        await message.reply_text("✅ Plugins and locale reloaded.")
