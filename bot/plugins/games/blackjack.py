from __future__ import annotations

import random
from pyrogram import Client, filters
from pyrogram.types import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup

from bot.core import loc
from bot.keyboards.inline import InlineKeyboards
from bot.utils.helpers import format_number

CARDS = list(range(2, 12)) + list(range(2, 11))
FACE_NAMES = {11: "J", 12: "Q", 13: "K", 14: "A"}


def _draw_card() -> int:
    return random.randint(2, 14)


def _card_value(card: int) -> int:
    if card >= 11:
        return 10
    return card


def _hand_value(hand: list) -> int:
    total = sum(_card_value(c) for c in hand)
    aces = hand.count(14)
    while total > 21 and aces > 0:
        total -= 10
        aces -= 1
    return total


def _card_display(card: int) -> str:
    suits = ["♠️", "♥️", "♦️", "♣️"]
    suit = random.choice(suits)
    name = str(card) if card <= 10 else FACE_NAMES.get(card, str(card))
    return f"{name}{suit}"


def register(app: Client):
    @app.on_message(filters.command("blackjack") | filters.command("bj"))
    async def blackjack_command(client: Client, message):
        args = message.text.split()
        if len(args) < 2:
            await message.reply_text("Usage: /blackjack <amount>")
            return
        try:
            amount = int(args[1])
        except ValueError:
            await message.reply_text("Invalid amount.")
            return
        await _start_blackjack(message, amount)

    @app.on_callback_query(filters.regex("^blackjack$"))
    async def blackjack_menu(client: Client, callback_query: CallbackQuery):
        lang = "en"
        text = f"{loc.t('games.blackjack_title', lang)}\n\nUsage: /blackjack <amount>"
        await callback_query.message.edit_text(text, reply_markup=InlineKeyboards.back_button("games_menu", lang))
        await callback_query.answer()


async def _start_blackjack(message, bet: int):
    lang = "en"
    user = message.from_user
    if message._services:
        eco_svc = message._services.get("economy")
        user_svc = message._services.get("user")
        ach_svc = message._services.get("achievement")
        if eco_svc:
            result = await eco_svc.remove_coins(user.id, bet, "Blackjack bet")
            if not result["success"]:
                await message.reply_text(loc.t("error.insufficient_funds", lang))
                return
            player = [_draw_card(), _draw_card()]
            dealer = [_draw_card(), _draw_card()]
            player_val = _hand_value(player)
            dealer_val = _hand_value(dealer)
            if player_val == 21 and len(player) == 2:
                winnings = int(bet * 2.5)
                await eco_svc.add_coins(user.id, winnings, "Blackjack")
                if user_svc:
                    await user_svc.increment_field(user.id, "games_played")
                if ach_svc:
                    await ach_svc.check_achievement(user.id, "games_10")
                dealer_cards = " ".join(_card_display(c) for c in dealer)
                player_cards = " ".join(_card_display(c) for c in player)
                text = f"🃏 **BLACKJACK!**\n\nPlayer: {player_cards} ({player_val})\nDealer: {dealer_cards} ({dealer_val})\n\n🎉 Won {format_number(winnings)} coins!"
                await message.reply_text(text)
                return
            while _hand_value(dealer) < 17:
                dealer.append(_draw_card())
            dealer_val = _hand_value(dealer)
            if dealer_val > 21:
                winnings = bet * 2
                await eco_svc.add_coins(user.id, winnings, "Blackjack win")
                if user_svc:
                    await user_svc.increment_field(user.id, "games_played")
                if ach_svc:
                    await ach_svc.check_achievement(user.id, "games_10")
                dealer_cards = " ".join(_card_display(c) for c in dealer)
                player_cards = " ".join(_card_display(c) for c in player)
                text = f"🃏 **Blackjack**\n\nPlayer: {player_cards} ({player_val})\nDealer: {dealer_cards} ({dealer_val})\n\n🎉 Dealer busted! Won {format_number(winnings)} coins!"
                await message.reply_text(text)
            elif player_val > dealer_val:
                winnings = bet * 2
                await eco_svc.add_coins(user.id, winnings, "Blackjack win")
                if user_svc:
                    await user_svc.increment_field(user.id, "games_played")
                if ach_svc:
                    await ach_svc.check_achievement(user.id, "games_10")
                dealer_cards = " ".join(_card_display(c) for c in dealer)
                player_cards = " ".join(_card_display(c) for c in player)
                text = f"🃏 **Blackjack**\n\nPlayer: {player_cards} ({player_val})\nDealer: {dealer_cards} ({dealer_val})\n\n🎉 Won {format_number(winnings)} coins!"
                await message.reply_text(text)
            elif dealer_val > player_val:
                if user_svc:
                    await user_svc.increment_field(user.id, "games_played")
                if ach_svc:
                    await ach_svc.check_achievement(user.id, "games_10")
                dealer_cards = " ".join(_card_display(c) for c in dealer)
                player_cards = " ".join(_card_display(c) for c in player)
                text = f"🃏 **Blackjack**\n\nPlayer: {player_cards} ({player_val})\nDealer: {dealer_cards} ({dealer_val})\n\n😔 Lost {format_number(bet)} coins."
                await message.reply_text(text)
            else:
                await eco_svc.add_coins(user.id, bet, "Blackjack push")
                if user_svc:
                    await user_svc.increment_field(user.id, "games_played")
                dealer_cards = " ".join(_card_display(c) for c in dealer)
                player_cards = " ".join(_card_display(c) for c in player)
                text = f"🃏 **Blackjack**\n\nPlayer: {player_cards} ({player_val})\nDealer: {dealer_cards} ({dealer_val})\n\n🤝 Push! Bet returned."
                await message.reply_text(text)
