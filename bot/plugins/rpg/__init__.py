from pyrogram import Client

from bot.plugins.rpg import rpg_menu, stats_cmd, equipment_cmd, dungeon_cmd, boss_cmd, pvp_cmd, fish_cmd, mine_cmd


def register(app: Client):
    rpg_menu.register(app)
    stats_cmd.register(app)
    equipment_cmd.register(app)
    dungeon_cmd.register(app)
    boss_cmd.register(app)
    pvp_cmd.register(app)
    fish_cmd.register(app)
    mine_cmd.register(app)
