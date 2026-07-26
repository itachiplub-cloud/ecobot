from pyrogram import Client

from bot.plugins.shop import shop_cmd


def register(app: Client):
    shop_cmd.register(app)
