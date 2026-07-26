from __future__ import annotations

from pyrogram import Client, filters
from pyrogram.types import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup

from bot.core import loc
from bot.utils.helpers import format_number


def register(app: Client):

    @app.on_callback_query(filters.regex("^games_menu$"))
    async def games_menu_callback(client: Client, callback_query: CallbackQuery):
        lang = "en"
        text = "🎮 **Game Center**\n\n🎮 Telegram Animated Games:\n🎯 /dart <bet>\n🎳 /bowling <bet>\n🏀 /basketball <bet>\n⚽ /football <bet>\n🎲 /diceroll <bet>\n\n🎮 Classic Games:\n🪙 /coinflip <bet>\n🎰 /slots <bet>\n💣 /mines <bet>\n📈 /crash <bet>\n🃏 /blackjack <bet>\n🎡 /roulette <bet> <choice>\n🎲 /dice <bet>\n\n🎮 Betting Games:\n🎯 /betroll <bet>\n⬆️ /highlow <bet> <high/low>\n🎡 /wheel <bet>\n📦 /treasure <bet>\n🃏 /luckycard <bet>\n🔢 /numberguess <bet> <1-6>\n\n📊 /gamestats - Your stats\n🏆 /gameleaderboard - Leaderboards"
        kb = InlineKeyboardMarkup([
            [InlineKeyboardButton("🎯 Dart", callback_data="game_dart"), InlineKeyboardButton("🎳 Bowling", callback_data="game_bowling")],
            [InlineKeyboardButton("🏀 Basketball", callback_data="game_basketball"), InlineKeyboardButton("⚽ Football", callback_data="game_football")],
            [InlineKeyboardButton("🎰 Slots", callback_data="game_slots"), InlineKeyboardButton("💣 Mines", callback_data="game_mines")],
            [InlineKeyboardButton("📈 Crash", callback_data="game_crash"), InlineKeyboardButton("🪙 Coinflip", callback_data="game_coinflip")],
            [InlineKeyboardButton("🎯 Bet Roll", callback_data="game_betroll"), InlineKeyboardButton("⬆️ High/Low", callback_data="game_highlow")],
            [InlineKeyboardButton("📊 Game Stats", callback_data="game_stats"), InlineKeyboardButton("🏆 Leaderboards", callback_data="game_leaderboard")],
            [InlineKeyboardButton(loc.t("btn.back", lang), callback_data="main_menu")],
        ])
        try:
            await callback_query.message.edit_text(text, reply_markup=kb)
        except Exception:
            await callback_query.message.reply_text(text, reply_markup=kb)
        await callback_query.answer()
