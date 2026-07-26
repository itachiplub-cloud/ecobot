from __future__ import annotations

from pyrogram import filters
from pyrogram.types import Message

from config import settings


def is_owner():
    return filters.user(settings.OWNER_ID)


def is_sudo():
    async def func(flt, client, message: Message):
        if message.from_user and message.from_user.id == settings.OWNER_ID:
            return True
        if message._services:
            admin_svc = message._services.get("admin")
            if admin_svc:
                return await admin_svc.is_sudo(message.from_user.id)
        return False
    return filters.create(func)


def is_admin():
    async def func(flt, client, message: Message):
        if message.from_user and message.from_user.id == settings.OWNER_ID:
            return True
        if message._services:
            admin_svc = message._services.get("admin")
            if admin_svc:
                return await admin_svc.is_admin(message.from_user.id)
        return False
    return filters.create(func)


def is_private():
    return filters.private


def is_group():
    return filters.group


def is_not_banned():
    async def func(flt, client, message: Message):
        if message._services:
            user_svc = message._services.get("user")
            if user_svc and message.from_user:
                return not await user_svc.is_banned(message.from_user.id)
        return True
    return filters.create(func)


def has_cooldown(action: str, seconds: int):
    async def func(flt, client, message: Message):
        if message._services:
            cd_svc = message._services.get("cooldown")
            if cd_svc and message.from_user:
                on_cd, remaining = await cd_svc.is_on_cooldown(message.from_user.id, action)
                if on_cd:
                    return False
        return True
    return filters.create(func)
