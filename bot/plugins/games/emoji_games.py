from __future__ import annotations

import asyncio
from pyrogram import Client, filters
from pyrogram.types import Message, CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup

from bot.core import loc
from bot.keyboards.inline import InlineKeyboards
from bot.utils.helpers import format_number


def register(app: Client):

    @app.on_message(filters.command("dart") & (filters.private | filters.group))
    async def dart_command(client: Client, message: Message):
        await _play_emoji_game(client, message, "dart", "🎯")

    @app.on_message(filters.command("bowling") & (filters.private | filters.group))
    async def bowling_command(client: Client, message: Message):
        await _play_emoji_game(client, message, "bowling", "🎳")

    @app.on_message(filters.command("basketball") & (filters.private | filters.group))
    async def basketball_command(client: Client, message: Message):
        await _play_emoji_game(client, message, "basketball", "🏀")

    @app.on_message(filters.command("football") & (filters.private | filters.group))
    async def football_command(client: Client, message: Message):
        await _play_emoji_game(client, message, "football", "⚽")

    @app.on_message(filters.command("diceroll") & (filters.private | filters.group))
    async def diceroll_command(client: Client, message: Message):
        await _play_emoji_game(client, message, "dice_roll", "🎲")


async def _play_emoji_game(client: Client, message: Message, game_type: str, emoji: str):
    user = message.from_user
    lang = "en"
    args = message.text.split()
    if len(args) < 2:
        await message.reply_text(f"Usage: /{game_type} <bet>")
        return
    try:
        bet = int(args[1])
    except ValueError:
        await message.reply_text(loc.t("error.invalid_input", lang))
        return

    services = getattr(message, '_services', None)
    if not services:
        await message.reply_text(loc.t("error.general", lang))
        return

    game_svc = services.get("game")
    eco_svc = services.get("economy")
    user_svc = services.get("user")
    ach_svc = services.get("achievement")
    cd_svc = services.get("cooldown")

    if not game_svc:
        await message.reply_text(loc.t("error.general", lang))
        return

    config = await game_svc.get_config(game_type)
    if not config.is_enabled:
        await message.reply_text(f"❌ {game_type} is currently disabled.")
        return

    if cd_svc:
        on_cd, remaining = await cd_svc.is_on_cooldown(user.id, f"game_{game_type}")
        if on_cd:
            time_str = cd_svc.format_time(remaining)
            await message.reply_text(loc.t("cooldown.active", lang, time=time_str))
            return

    sent = await client.send_dice(chat_id=message.chat.id, emoji=emoji)
    await asyncio.sleep(4)

    value = sent.dice.value
    result = game_svc.telegram_dice_result(emoji, value)

    win_values = {
        "🎯": [5, 6],
        "🎳": [5, 6],
        "🏀": [4, 5],
        "⚽": [4, 5],
        "🎲": [4, 5, 6],
    }
    won = value in win_values.get(emoji, [5, 6])
    multiplier = config.multiplier if won else 0
    payout = int(bet * multiplier) if won else 0

    game_result = await game_svc.play_game(
        user.id, game_type, bet, won, payout,
        chat_id=message.chat.id, chat_type=message.chat.type.value,
        emoji=emoji, dice_value=value,
    )

    if not game_result["success"]:
        reason = game_result.get("reason", "unknown")
        if reason == "insufficient_funds":
            await message.reply_text(loc.t("error.insufficient_funds", lang))
        elif reason == "daily_limit":
            await message.reply_text(f"❌ Daily limit reached ({game_result['limit']})")
        else:
            await message.reply_text(loc.t("error.general", lang))
        return

    if won:
        text = (
            f"{result['display']}\n\n"
            f"🎉 **You won!**\n"
            f"💰 Bet: {format_number(bet)} | Won: {format_number(payout)}\n"
            f"💎 Wallet: {format_number(game_result['wallet'])}\n"
            f"📊 Games today: {game_result['daily_remaining']} remaining"
        )
    else:
        text = (
            f"{result['display']}\n\n"
            f"😔 **You lost!**\n"
            f"💰 Lost: {format_number(bet)}\n"
            f"💎 Wallet: {format_number(game_result['wallet'])}\n"
            f"📊 Games today: {game_result['daily_remaining']} remaining"
        )

    if user_svc:
        await user_svc.increment_field(user.id, "games_played")
    if ach_svc:
        if won:
            await ach_svc.check_achievement(user.id, "games_10")
        stats = game_result.get("stats")
        if stats and stats.games_won >= 100:
            await ach_svc.check_achievement(user.id, "games_100")

    if cd_svc:
        await cd_svc.set_cooldown(user.id, f"game_{game_type}", config.cooldown_seconds)

    await message.reply_text(text)
