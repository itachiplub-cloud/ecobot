from __future__ import annotations

import random
from pyrogram import Client, filters
from pyrogram.types import Message, CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup

from bot.core import loc
from bot.keyboards.inline import InlineKeyboards
from bot.utils.helpers import format_number


def register(app: Client):

    @app.on_message(filters.command("mines") & (filters.private | filters.group))
    async def mines_command(client: Client, message: Message):
        lang = "en"
        args = message.text.split()
        if len(args) < 2:
            await message.reply_text(f"Usage: /mines <bet>")
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
        config = await game_svc.get_config("mines")
        if cd_svc:
            on_cd, remaining = await cd_svc.is_on_cooldown(message.from_user.id, "game_mines")
            if on_cd:
                await message.reply_text(loc.t("cooldown.active", lang, time=cd_svc.format_time(remaining)))
                return

        grid_size = 25
        bomb_count = 5
        safe_count = grid_size - bomb_count
        multiplier = config.multiplier

        buttons = []
        grid = ["🟢"] * grid_size
        bombs = random.sample(range(grid_size), bomb_count)
        for i in range(grid_size):
            row = i // 5
            if len(buttons) <= row:
                buttons.append([])
            if i in bombs:
                grid[i] = "💣"
            buttons[row].append(InlineKeyboardButton("⬛", callback_data=f"mines_{message.from_user.id}_{bet}_{i}"))

        kb = InlineKeyboardMarkup(buttons)
        await message.reply_text(
            f"💣 **Mines**\n\nBet: {format_number(bet)} | Grid: 5x5 | Bombs: {bomb_count}\nClick tiles to reveal!",
            reply_markup=kb,
        )

    @app.on_callback_query(filters.regex(r"^mines_(\d+)_(\d+)_(\d+)$"))
    async def mines_tile_callback(client: Client, callback_query: CallbackQuery):
        parts = callback_query.data.split("_")
        owner_id = int(parts[1])
        bet = int(parts[2])
        tile = int(parts[3])
        lang = "en"

        if callback_query.from_user.id != owner_id:
            await callback_query.answer("This isn't your game!", show_alert=True)
            return

        services = getattr(callback_query, '_services', None)
        if not services:
            await callback_query.answer()
            return

        game_svc = services.get("game")
        if not game_svc:
            await callback_query.answer()
            return

        grid_size = 25
        bomb_count = 5
        random.seed(callback_query.message.id)
        bombs = random.sample(range(grid_size), bomb_count)
        random.seed()

        if tile in bombs:
            buttons = []
            for i in range(grid_size):
                row = i // 5
                if len(buttons) <= row:
                    buttons.append([])
                if i in bombs:
                    buttons[row].append(InlineKeyboardButton("💣", callback_data="noop"))
                else:
                    buttons[row].append(InlineKeyboardButton("🟢", callback_data="noop"))
            kb = InlineKeyboardMarkup(buttons)
            payout = 0
            won = False
            result = await game_svc.play_game(
                owner_id, "mines", bet, won, payout,
                chat_id=callback_query.message.chat.id,
            )
            try:
                await callback_query.message.edit_text(
                    f"💣 **BOOM!** You hit a mine!\n\n💰 Lost: {format_number(bet)} coins",
                    reply_markup=kb,
                )
            except Exception:
                pass
            await callback_query.answer("BOOM! 💥", show_alert=True)
        else:
            payout = int(bet * 1.5)
            won = True
            result = await game_svc.play_game(
                owner_id, "mines", bet, won, payout,
                chat_id=callback_query.message.chat.id,
            )
            try:
                await callback_query.message.edit_text(
                    f"💚 **Safe!**\n\n💰 Won: {format_number(payout)} coins\n💎 Wallet: {format_number(result.get('wallet', 0))}",
                )
            except Exception:
                pass
            await callback_query.answer(f"Safe! Won {format_number(payout)} coins!", show_alert=True)
