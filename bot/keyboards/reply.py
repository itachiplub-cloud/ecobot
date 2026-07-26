from __future__ import annotations

from pyrogram.types import ReplyKeyboardMarkup, KeyboardButton


class ReplyKeyboards:
    @staticmethod
    def main_menu():
        return ReplyKeyboardMarkup(
            [[KeyboardButton("/start"), KeyboardButton("/help")]],
            resize_keyboard=True,
        )
