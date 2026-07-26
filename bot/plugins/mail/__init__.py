from pyrogram import Client

from bot.plugins.mail import mail_cmd


def register(app: Client):
    mail_cmd.register(app)
