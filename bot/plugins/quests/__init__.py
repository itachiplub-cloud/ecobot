from pyrogram import Client

from bot.plugins.quests import quests_cmd


def register(app: Client):
    quests_cmd.register(app)
