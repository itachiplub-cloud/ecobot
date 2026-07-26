from pyrogram import Client

from bot.plugins.clans import clans_cmd


def register(app: Client):
    clans_cmd.register(app)
