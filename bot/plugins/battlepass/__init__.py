from pyrogram import Client

from bot.plugins.battlepass import battlepass_cmd, gamepass_cmd


def register(app: Client):
    battlepass_cmd.register(app)
    gamepass_cmd.register(app)
