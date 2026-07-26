from __future__ import annotations

from pyrogram import Client, filters
from pyrogram.types import CallbackQuery, Message

from bot.core import loc
from bot.keyboards.inline import InlineKeyboards
from bot.utils.helpers import format_number


def register(app: Client):
    @app.on_message(filters.command("withdraw"))
    async def withdraw_command(client: Client, message: Message):
        user = message.from_user
        lang = "en"
        args = message.text.split()
        if len(args) < 2:
            await message.reply_text(loc.t("economy.withdraw_prompt", lang))
            return
        try:
            amount = int(args[1])
        except ValueError:
            await message.reply_text(loc.t("error.invalid_input", lang))
            return
        if message._services:
            eco_svc = message._services.get("economy")
            if eco_svc:
                result = await eco_svc.withdraw(user.id, amount)
                if result["success"]:
                    text = f"{loc.t('economy.withdraw_success', lang, amount=format_number(amount))}\n💰 Wallet: {format_number(result['wallet'])}\n🏦 Bank: {format_number(result['bank'])}"
                else:
                    text = loc.t("economy.withdraw_failed", lang)
                await message.reply_text(text)
                return
        await message.reply_text(loc.t("error.general", lang))

    @app.on_callback_query(filters.regex("^withdraw$"))
    async def withdraw_callback(client: Client, callback_query: CallbackQuery):
        lang = "en"
        await callback_query.message.edit_text(
            loc.t("economy.withdraw_prompt", lang),
            reply_markup=InlineKeyboards.back_button("economy", lang),
        )
        await callback_query.answer()
