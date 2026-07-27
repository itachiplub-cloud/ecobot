from pyrogram import Client


def register_core(app: Client):
    from bot.plugins import start, help as help_cmd, profile_cmd, settings_cmd

    start.register(app)
    help_cmd.register(app)
    profile_cmd.register(app)
    settings_cmd.register(app)
