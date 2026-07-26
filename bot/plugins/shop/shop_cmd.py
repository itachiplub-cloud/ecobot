from __future__ import annotations

from pyrogram import Client, filters
from pyrogram.types import CallbackQuery, Message

from bot.core import loc
from bot.keyboards.inline import InlineKeyboards
from bot.utils.helpers import format_number


def register(app: Client):
    @app.on_message(filters.command("shop"))
    async def shop_command(client: Client, message: Message):
        lang = "en"
        await message.reply_text(loc.t("shop.title", lang), reply_markup=InlineKeyboards.shop_menu(lang))

    @app.on_message(filters.command("buy"))
    async def buy_command(client: Client, message: Message):
        args = message.text.split()
        if len(args) < 2:
            await message.reply_text("Usage: /buy <item_id> [quantity]")
            return
        item_id = args[1]
        quantity = int(args[2]) if len(args) > 2 else 1
        user = message.from_user
        if message._services:
            shop_svc = message._services.get("shop")
            if shop_svc:
                result = await shop_svc.buy_item(user.id, item_id, "permanent", quantity)
                if result["success"]:
                    await message.reply_text(loc.t("shop.buy_success", "en", item=result.get("item", item_id), amount=format_number(result["paid"])))
                else:
                    reason = result.get("reason", "unknown")
                    if reason == "insufficient_funds":
                        await message.reply_text(loc.t("error.insufficient_funds", "en"))
                    elif reason == "out_of_stock":
                        await message.reply_text(loc.t("shop.buy_no_stock", "en"))
                    else:
                        await message.reply_text(loc.t("shop.buy_failed", "en"))

    @app.on_message(filters.command("sell"))
    async def sell_command(client: Client, message: Message):
        args = message.text.split()
        if len(args) < 2:
            await message.reply_text("Usage: /sell <item_id> [quantity]")
            return
        item_id = args[1]
        quantity = int(args[2]) if len(args) > 2 else 1
        user = message.from_user
        if message._services:
            shop_svc = message._services.get("shop")
            if shop_svc:
                result = await shop_svc.sell_item(user.id, item_id, quantity)
                if result["success"]:
                    await message.reply_text(loc.t("shop.sell_success", "en", item=result.get("item", item_id), amount=format_number(result["earned"])))
                else:
                    await message.reply_text(loc.t("shop.sell_failed", "en"))

    @app.on_callback_query(filters.regex("^shop$"))
    async def shop_callback(client: Client, callback_query: CallbackQuery):
        lang = "en"
        text = loc.t("shop.title", lang)
        try:
            await callback_query.message.edit_text(text, reply_markup=InlineKeyboards.shop_menu(lang))
        except Exception:
            await callback_query.message.reply_text(text, reply_markup=InlineKeyboards.shop_menu(lang))
        await callback_query.answer()

    @app.on_callback_query(filters.regex("^shop_permanent$"))
    async def shop_permanent_callback(client: Client, callback_query: CallbackQuery):
        lang = "en"
        if callback_query._services:
            shop_svc = callback_query._services.get("shop")
            if shop_svc:
                items = await shop_svc.get_shop_items("permanent")
                if items:
                    text = loc.t("shop.title", lang) + " - Permanent\n\n"
                    for s in items[:10]:
                        text += f"  📦 {s.item_id} | 💰 {format_number(s.price_override or 0)}\n"
                else:
                    text = "No items in shop."
                try:
                    await callback_query.message.edit_text(text, reply_markup=InlineKeyboards.back_button("shop", lang))
                except Exception:
                    await callback_query.message.reply_text(text, reply_markup=InlineKeyboards.back_button("shop", lang))
        await callback_query.answer()

    @app.on_callback_query(filters.regex("^shop_daily$"))
    async def shop_daily_callback(client: Client, callback_query: CallbackQuery):
        lang = "en"
        text = loc.t("shop.daily_reset", lang, time="24h")
        await callback_query.message.edit_text(text, reply_markup=InlineKeyboards.back_button("shop", lang))
        await callback_query.answer()

    @app.on_callback_query(filters.regex("^shop_weekly$"))
    async def shop_weekly_callback(client: Client, callback_query: CallbackQuery):
        lang = "en"
        text = "📅 Weekly Shop - Resets every Monday!"
        await callback_query.message.edit_text(text, reply_markup=InlineKeyboards.back_button("shop", lang))
        await callback_query.answer()

    @app.on_callback_query(filters.regex("^shop_premium$"))
    async def shop_premium_callback(client: Client, callback_query: CallbackQuery):
        lang = "en"
        text = "👑 Premium Shop - Requires Premium membership!"
        await callback_query.message.edit_text(text, reply_markup=InlineKeyboards.back_button("shop", lang))
        await callback_query.answer()
