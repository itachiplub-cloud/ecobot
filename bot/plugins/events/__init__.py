from pyrogram import Client

from bot.plugins.events import events_cmd


def register(app: Client):
    events_cmd.register(app)
