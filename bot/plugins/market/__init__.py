from pyrogram import Client

from bot.plugins.market import market_cmd


def register(app: Client):
    market_cmd.register(app)
