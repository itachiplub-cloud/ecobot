from pyrogram import Client

from bot.plugins.achievements import achievements_cmd


def register(app: Client):
    achievements_cmd.register(app)
