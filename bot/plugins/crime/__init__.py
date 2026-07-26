from pyrogram import Client

from bot.plugins.crime import crime_cmd


def register(app: Client):
    crime_cmd.register(app)
