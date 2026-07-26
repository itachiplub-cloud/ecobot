from pyrogram import Client

from bot.plugins.banking import banking_cmd, invest_cmd, bank_lb_cmd


def register(app: Client):
    banking_cmd.register(app)
    invest_cmd.register(app)
    bank_lb_cmd.register(app)
