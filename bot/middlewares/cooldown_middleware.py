from __future__ import annotations

from pyrogram import Client
from pyrogram.types import Message

from bot.core import loc


class CooldownMiddleware:
    def __init__(self, action: str, seconds: int):
        self.action = action
        self.seconds = seconds

    async def __call__(self, client: Client, message: Message, handler):
        if message._services:
            cd_svc = message._services.get("cooldown")
            if cd_svc and message.from_user:
                on_cd, remaining = await cd_svc.is_on_cooldown(message.from_user.id, self.action)
                if on_cd:
                    time_str = cd_svc.format_time(remaining)
                    text = loc.t("cooldown.active", message.db_lang, time=time_str)
                    await message.reply_text(text)
                    return
                await handler(client, message)
                await cd_svc.set_cooldown(message.from_user.id, self.action, self.seconds)
                return
        return await handler(client, message)
