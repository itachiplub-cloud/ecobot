from pyrogram import Client

from bot.plugins.games import (
    coinflip, slots, blackjack, roulette, dice_game, mines, crash,
    emoji_games, betting_games, mines_game, game_menu, game_stats_lb,
)


def register(app: Client):
    coinflip.register(app)
    slots.register(app)
    blackjack.register(app)
    roulette.register(app)
    dice_game.register(app)
    mines.register(app)
    crash.register(app)
    emoji_games.register(app)
    betting_games.register(app)
    mines_game.register(app)
    game_menu.register(app)
    game_stats_lb.register(app)
