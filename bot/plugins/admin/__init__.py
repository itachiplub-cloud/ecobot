from pyrogram import Client

from bot.plugins.admin import admin_cmd, owner_cmd, owner_panel, enhanced_owner_cmds, owner_panel_actions


def register(app: Client):
    admin_cmd.register(app)
    owner_cmd.register(app)
    owner_panel.register(app)
    enhanced_owner_cmds.register(app)
    owner_panel_actions.register(app)
