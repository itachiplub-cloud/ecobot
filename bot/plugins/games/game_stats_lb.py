from __future__ import annotations

from pyrogram import Client, filters
from pyrogram.types import Message, CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup

from bot.core import loc
from bot.keyboards.inline import InlineKeyboards
from bot.utils.helpers import format_number, progress_bar


def register(app: Client):

    @app.on_message(filters.command("gamestats") & (filters.private | filters.group))
    async def gamestats_command(client: Client, message: Message):
        user = message.from_user
        services = getattr(message, '_services', None)
        if not services:
            return
        game_svc = services.get("game")
        if not game_svc:
            return
        stats = await game_svc.get_stats(user.id)
        win_rate = (stats.games_won / stats.games_played * 100) if stats.games_played > 0 else 0
        net = stats.total_coins_won - stats.total_coins_lost
        text = (
            f"📊 **Game Statistics**\n\n"
            f"🎮 Played: {stats.games_played}\n"
            f"🏆 Won: {stats.games_won}\n"
            f"😔 Lost: {stats.games_lost}\n"
            f"📈 Win Rate: {win_rate:.1f}%\n\n"
            f"💰 Coins Won: {format_number(stats.total_coins_won)}\n"
            f"💸 Coins Lost: {format_number(stats.total_coins_lost)}\n"
            f"💎 Net: {format_number(net)}\n\n"
            f"🏅 Highest Win: {format_number(stats.highest_win)}\n"
            f"🎰 Highest Bet: {format_number(stats.highest_bet)}\n"
            f"🔥 Win Streak: {stats.current_win_streak}\n"
            f"❄️ Lose Streak: {stats.current_lose_streak}\n"
            f"⭐ Best Win Streak: {stats.longest_win_streak}\n"
            f"📊 Daily: {stats.daily_games} | Weekly: {stats.weekly_games}\n"
            f"📅 Monthly: {stats.monthly_games} | All: {stats.lifetime_games}"
        )
        await message.reply_text(text)

    @app.on_callback_query(filters.regex("^game_stats$"))
    async def game_stats_callback(client: Client, callback_query: CallbackQuery):
        user = callback_query.from_user
        services = getattr(callback_query, '_services', None)
        if not services:
            await callback_query.answer()
            return
        game_svc = services.get("game")
        if not game_svc:
            await callback_query.answer()
            return
        stats = await game_svc.get_stats(user.id)
        win_rate = (stats.games_won / stats.games_played * 100) if stats.games_played > 0 else 0
        net = stats.total_coins_won - stats.total_coins_lost
        text = (
            f"📊 **Game Statistics**\n\n"
            f"🎮 Played: {stats.games_played} | Won: {stats.games_won} | Lost: {stats.games_lost}\n"
            f"📈 Win Rate: {win_rate:.1f}%\n"
            f"💰 Won: {format_number(stats.total_coins_won)} | Lost: {format_number(stats.total_coins_lost)}\n"
            f"💎 Net: {format_number(net)}\n"
            f"🏅 Best: {format_number(stats.highest_win)} | Streak: {stats.longest_win_streak}"
        )
        try:
            await callback_query.message.edit_text(text, reply_markup=InlineKeyboards.back_button("games_menu", "en"))
        except Exception:
            pass
        await callback_query.answer()

    @app.on_callback_query(filters.regex("^game_leaderboard$"))
    async def game_leaderboard_callback(client: Client, callback_query: CallbackQuery):
        lang = "en"
        kb = InlineKeyboardMarkup([
            [InlineKeyboardButton("🎮 Most Played", callback_data="glb_played")],
            [InlineKeyboardButton("🏆 Most Wins", callback_data="glb_wins")],
            [InlineKeyboardButton("📈 Best Win Rate", callback_data="glb_winrate")],
            [InlineKeyboardButton("💰 Biggest Winner", callback_data="glb_earner")],
            [InlineKeyboardButton("🎰 Biggest Gambler", callback_data="glb_gambler")],
            [InlineKeyboardButton(loc.t("btn.back", lang), callback_data="games_menu")],
        ])
        try:
            await callback_query.message.edit_text("🏆 **Game Leaderboards**", reply_markup=kb)
        except Exception:
            pass
        await callback_query.answer()

    for lb_type, title, repo_method in [
        ("glb_played", "🎮 Most Played Games", "get_top_played"),
        ("glb_wins", "🏆 Most Wins", "get_top_winners"),
        ("glb_winrate", "📈 Best Win Rate", "get_top_win_rate"),
        ("glb_earner", "💰 Biggest Winners", "get_top_earners"),
        ("glb_gambler", "🎰 Biggest Gamblers", "get_top_bettors"),
    ]:
        @app.on_callback_query(filters.regex(f"^{lb_type}$"))
        async def glb_callback(client: Client, callback_query: CallbackQuery, _title=title, _method=repo_method):
            services = getattr(callback_query, '_services', None)
            if not services:
                await callback_query.answer()
                return
            game_svc = services.get("game")
            if not game_svc:
                await callback_query.answer()
                return
            method = getattr(game_svc.stats_repo, _method, None)
            if not method:
                await callback_query.answer()
                return
            top = await method(10)
            text = f"{_title}\n\n"
            medals = ["🥇", "🥈", "🥉"]
            for i, s in enumerate(top):
                medal = medals[i] if i < 3 else f"#{i+1}"
                text += f"{medal} `{s.user_id}` - {s.games_played} played, {s.games_won} won\n"
            if not top:
                text += "No data yet."
            try:
                await callback_query.message.edit_text(text, reply_markup=InlineKeyboards.back_button("game_leaderboard", "en"))
            except Exception:
                pass
            await callback_query.answer()
