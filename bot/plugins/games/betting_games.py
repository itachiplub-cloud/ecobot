from __future__ import annotations

import random
from pyrogram import Client, filters
from pyrogram.types import Message, CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup

from bot.core import loc
from bot.keyboards.inline import InlineKeyboards
from bot.utils.helpers import format_number


def register(app: Client):

    @app.on_message(filters.command("betroll") & (filters.private | filters.group))
    async def betroll_command(client: Client, message: Message):
        await _play_number_game(client, message, "bet_roll", 1, 100, lambda v: v > 50, 2.0)

    @app.on_message(filters.command("highlow") & (filters.private | filters.group))
    async def highlow_command(client: Client, message: Message):
        lang = "en"
        args = message.text.split()
        if len(args) < 3:
            await message.reply_text(f"Usage: /highlow <bet> <high/low>")
            return
        try:
            bet = int(args[1])
        except ValueError:
            await message.reply_text(loc.t("error.invalid_input", lang))
            return
        choice = args[2].lower()
        if choice not in ("high", "low"):
            await message.reply_text("Choose 'high' or 'low'")
            return
        services = getattr(message, '_services', None)
        if not services:
            return
        game_svc = services.get("game")
        cd_svc = services.get("cooldown")
        if not game_svc:
            return
        config = await game_svc.get_config("high_low")
        if cd_svc:
            on_cd, remaining = await cd_svc.is_on_cooldown(message.from_user.id, "game_high_low")
            if on_cd:
                await message.reply_text(loc.t("cooldown.active", lang, time=cd_svc.format_time(remaining)))
                return
        first = random.randint(1, 6)
        second = random.randint(1, 6)
        if choice == "high":
            won = second > first
        else:
            won = second < first
        payout = int(bet * 2) if won else 0
        result = await game_svc.play_game(
            message.from_user.id, "high_low", bet, won, payout,
            chat_id=message.chat.id, chat_type=message.chat.type.value,
            first=first, second=second, choice=choice,
        )
        if not result["success"]:
            await message.reply_text(f"❌ {result.get('reason', 'Error')}")
            return
        emoji1 = "⬆️" if first > 3 else "⬇️"
        emoji2 = "⬆️" if second > 3 else "⬇️"
        text = (
            f"🎲 {first} {emoji1} → {second} {emoji2}\n\n"
            f"{'🎉 Won' if won else '😔 Lost'} {format_number(payout if won else bet)} coins!\n"
            f"💎 Wallet: {format_number(result['wallet'])}"
        )
        await message.reply_text(text)
        if cd_svc:
            await cd_svc.set_cooldown(message.from_user.id, "game_high_low", config.cooldown_seconds)

    @app.on_message(filters.command("wheel") & (filters.private | filters.group))
    async def wheel_command(client: Client, message: Message):
        await _play_number_game(client, message, "wheel", 1, 12, lambda v: v in [7, 8, 9, 10, 11, 12], 2.0)

    @app.on_message(filters.command("treasure") & (filters.private | filters.group))
    async def treasure_command(client: Client, message: Message):
        await _play_number_game(client, message, "treasure_box", 1, 10, lambda v: v == 7, 5.0)

    @app.on_message(filters.command("luckycard") & (filters.private | filters.group))
    async def luckycard_command(client: Client, message: Message):
        await _play_number_game(client, message, "lucky_card", 1, 10, lambda v: v in [7, 8, 9], 3.0)

    @app.on_message(filters.command("numberguess") & (filters.private | filters.group))
    async def numberguess_command(client: Client, message: Message):
        lang = "en"
        args = message.text.split()
        if len(args) < 3:
            await message.reply_text(f"Usage: /numberguess <bet> <1-6>")
            return
        try:
            bet = int(args[1])
            guess = int(args[2])
        except ValueError:
            await message.reply_text(loc.t("error.invalid_input", lang))
            return
        if guess < 1 or guess > 6:
            await message.reply_text("Guess must be 1-6")
            return
        services = getattr(message, '_services', None)
        if not services:
            return
        game_svc = services.get("game")
        cd_svc = services.get("cooldown")
        if not game_svc:
            return
        config = await game_svc.get_config("number_guess")
        if cd_svc:
            on_cd, remaining = await cd_svc.is_on_cooldown(message.from_user.id, "game_number_guess")
            if on_cd:
                await message.reply_text(loc.t("cooldown.active", lang, time=cd_svc.format_time(remaining)))
                return
        rolled = random.randint(1, 6)
        won = rolled == guess
        payout = int(bet * 6) if won else 0
        result = await game_svc.play_game(
            message.from_user.id, "number_guess", bet, won, payout,
            chat_id=message.chat.id, chat_type=message.chat.type.value,
            guess=guess, rolled=rolled,
        )
        if not result["success"]:
            await message.reply_text(f"❌ {result.get('reason', 'Error')}")
            return
        text = (
            f"🎲 You guessed: {guess} | Rolled: {rolled}\n\n"
            f"{'🎉 JACKPOT! Won' if won else '😔 Lost'} {format_number(payout if won else bet)} coins!\n"
            f"💎 Wallet: {format_number(result['wallet'])}"
        )
        await message.reply_text(text)
        if cd_svc:
            await cd_svc.set_cooldown(message.from_user.id, "game_number_guess", config.cooldown_seconds)

    @app.on_message(filters.command("crash") & (filters.private | filters.group))
    async def crash_command(client: Client, message: Message):
        lang = "en"
        args = message.text.split()
        if len(args) < 2:
            await message.reply_text(f"Usage: /crash <bet>")
            return
        try:
            bet = int(args[1])
        except ValueError:
            await message.reply_text(loc.t("error.invalid_input", lang))
            return
        services = getattr(message, '_services', None)
        if not services:
            return
        game_svc = services.get("game")
        cd_svc = services.get("cooldown")
        if not game_svc:
            return
        config = await game_svc.get_config("crash")
        if cd_svc:
            on_cd, remaining = await cd_svc.is_on_cooldown(message.from_user.id, "game_crash")
            if on_cd:
                await message.reply_text(loc.t("cooldown.active", lang, time=cd_svc.format_time(remaining)))
                return
        crash_point = round(random.uniform(1.0, 10.0), 2)
        multiplier = crash_point
        payout = int(bet * multiplier)
        won = True
        result = await game_svc.play_game(
            message.from_user.id, "crash", bet, won, payout,
            chat_id=message.chat.id, chat_type=message.chat.type.value,
            crash_point=crash_point,
        )
        if not result["success"]:
            await message.reply_text(f"❌ {result.get('reason', 'Error')}")
            return
        text = (
            f"📈 **Crash**\n\n"
            f"Crashed at {multiplier}x!\n"
            f"💰 Won {format_number(payout)} coins!\n"
            f"💎 Wallet: {format_number(result['wallet'])}"
        )
        await message.reply_text(text)
        if cd_svc:
            await cd_svc.set_cooldown(message.from_user.id, "game_crash", config.cooldown_seconds)


async def _play_number_game(client: Client, message: Message, game_type: str, low: int, high: int, win_check, default_multiplier: float):
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
        return
    game_svc = services.get("game")
    cd_svc = services.get("cooldown")
    if not game_svc:
        return
    config = await game_svc.get_config(game_type)
    if cd_svc:
        on_cd, remaining = await cd_svc.is_on_cooldown(message.from_user.id, f"game_{game_type}")
        if on_cd:
            await message.reply_text(loc.t("cooldown.active", lang, time=cd_svc.format_time(remaining)))
            return
    value = random.randint(low, high)
    won = win_check(value)
    multiplier = config.multiplier if won else 0
    payout = int(bet * multiplier) if won else 0
    result = await game_svc.play_game(
        message.from_user.id, game_type, bet, won, payout,
        chat_id=message.chat.id, chat_type=message.chat.type.value,
        value=value,
    )
    if not result["success"]:
        await message.reply_text(f"❌ {result.get('reason', 'Error')}")
        return
    text = (
        f"🎯 Result: {value}\n\n"
        f"{'🎉 Won' if won else '😔 Lost'} {format_number(payout if won else bet)} coins!\n"
        f"💎 Wallet: {format_number(result['wallet'])}"
    )
    await message.reply_text(text)
    if cd_svc:
        await cd_svc.set_cooldown(message.from_user.id, f"game_{game_type}", config.cooldown_seconds)
