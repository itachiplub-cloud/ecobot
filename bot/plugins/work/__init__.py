from pyrogram import Client

from bot.plugins.work import work_cmd


def register(app: Client):
    work_cmd.register(app)
