from pyrogram import Client

from bot.plugins.daily import daily_cmd


def register(app: Client):
    daily_cmd.register(app)
