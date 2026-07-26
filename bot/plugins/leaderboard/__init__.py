from pyrogram import Client

from bot.plugins.leaderboard import leaderboard_cmd, group_ranking_cmd


def register(app: Client):
    leaderboard_cmd.register(app)
    group_ranking_cmd.register(app)
