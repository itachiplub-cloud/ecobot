from pyrogram import Client

from bot.plugins.pets import pets_cmd


def register(app: Client):
    pets_cmd.register(app)
