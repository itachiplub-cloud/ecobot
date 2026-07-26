from __future__ import annotations

from pyrogram import Client, filters
from pyrogram.types import CallbackQuery, Message

from bot.core import loc
from config import settings


def register(app: Client):
    @app.on_message(filters.command("events") & filters.user(settings.OWNER_ID))
    async def events_command(client: Client, message: Message):
        if message._services:
            event_svc = message._services.get("event")
            if event_svc:
                events = await event_svc.get_active_events()
                text = "🎉 **Active Events**\n\n"
                if events:
                    for e in events:
                        text += f"  📌 {e.name} ({e.event_type})\n"
                else:
                    text += "No active events."
                await message.reply_text(text)

    @app.on_message(filters.command("createevent") & filters.user(settings.OWNER_ID))
    async def create_event_command(client: Client, message: Message):
        args = message.text.split(maxsplit=2)
        if len(args) < 3:
            await message.reply_text("Usage: /createevent <type> <name> [description]")
            return
        event_type = args[1]
        name = args[2]
        description = args[3] if len(args) > 3 else ""
        if message._services:
            event_svc = message._services.get("event")
            if event_svc:
                await event_svc.create_event(name, event_type, description, created_by=message.from_user.id)
                await message.reply_text(f"✅ Event '{name}' created!")

    @app.on_message(filters.command("joinevent"))
    async def join_event_command(client: Client, message: Message):
        args = message.text.split()
        if len(args) < 2:
            await message.reply_text("Usage: /joinevent <event_id>")
            return
        event_id = args[1]
        if message._services:
            event_svc = message._services.get("event")
            if event_svc:
                success = await event_svc.join_event(event_id, message.from_user.id)
                if success:
                    await message.reply_text("✅ Joined event!")
                else:
                    await message.reply_text("❌ Failed to join event.")
