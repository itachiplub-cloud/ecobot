from pyrogram import Client

from bot.plugins.economy import balance, deposit, withdraw, transfer


def register(app: Client):
    balance.register(app)
    deposit.register(app)
    withdraw.register(app)
    transfer.register(app)
