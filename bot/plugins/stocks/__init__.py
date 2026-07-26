from pyrogram import Client

from bot.plugins.stocks import stock_menu, stock_admin


def register(app: Client):
    stock_menu.register(app)
    stock_admin.register(app)
