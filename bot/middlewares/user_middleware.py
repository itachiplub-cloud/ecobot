from __future__ import annotations

from pyrogram import Client
from pyrogram.types import Message

from config import settings


class UserMiddleware:
    def __init__(self):
        pass

    async def __call__(self, client: Client, message: Message, handler):
        if message.from_user and message.from_user.id == settings.OWNER_ID:
            message._is_owner = True
        else:
            message._is_owner = False

        if message._services:
            user_svc = message._services.get("user")
            if user_svc and message.from_user:
                user = await user_svc.get_or_create(
                    message.from_user.id,
                    username=message.from_user.username,
                    first_name=message.from_user.first_name,
                    last_name=message.from_user.last_name,
                )
                message._db_user = user
                if user.is_banned:
                    return
                await user_svc.update_user(message.from_user.id)

        return await handler(client, message)
