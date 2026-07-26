from __future__ import annotations

from pyrogram import Client, filters
from pyrogram.types import CallbackQuery, Message

from bot.core import loc
from bot.keyboards.inline import InlineKeyboards
from bot.utils.helpers import format_number


def register(app: Client):
    @app.on_message(filters.command("market"))
    async def market_command(client: Client, message: Message):
        lang = "en"
        await message.reply_text(loc.t("market.title", lang), reply_markup=InlineKeyboards.market_menu(lang))

    @app.on_message(filters.command("marketlist") | filters.command("msell"))
    async def market_list_command(client: Client, message: Message):
        args = message.text.split()
        if len(args) < 3:
            await message.reply_text("Usage: /msell <item_id> <price>")
            return
        item_id = args[1]
        try:
            price = int(args[2])
        except ValueError:
            await message.reply_text("Invalid price.")
            return
        if message._services:
            market_svc = message._services.get("market")
            inv_svc = message._services.get("inventory")
            if market_svc and inv_svc:
                has = await inv_svc.has_item(message.from_user.id, item_id)
                if not has:
                    await message.reply_text(loc.t("error.not_found", "en"))
                    return
                result = await market_svc.create_listing(message.from_user.id, item_id, 1, price)
                if result["success"]:
                    await inv_svc.remove_item(message.from_user.id, item_id)
                    await message.reply_text(loc.t("market.list_success", "en", item=item_id, price=format_number(price)))

    @app.on_callback_query(filters.regex("^market_menu$"))
    async def market_menu_callback(client: Client, callback_query: CallbackQuery):
        lang = "en"
        text = loc.t("market.title", lang)
        try:
            await callback_query.message.edit_text(text, reply_markup=InlineKeyboards.market_menu(lang))
        except Exception:
            await callback_query.message.reply_text(text, reply_markup=InlineKeyboards.market_menu(lang))
        await callback_query.answer()

    @app.on_callback_query(filters.regex("^market_browse$"))
    async def market_browse_callback(client: Client, callback_query: CallbackQuery):
        lang = "en"
        if callback_query._services:
            market_svc = callback_query._services.get("market")
            if market_svc:
                listings = await market_svc.get_listings(limit=20)
                if listings:
                    text = loc.t("market.browse", lang) + "\n\n"
                    for l in listings[:15]:
                        text += f"  📦 {l.item_id} | 💰 {format_number(l.price)} | ID: {l.listing_id}\n"
                else:
                    text = loc.t("market.no_listings", lang)
                try:
                    await callback_query.message.edit_text(text, reply_markup=InlineKeyboards.back_button("market_menu", lang))
                except Exception:
                    await callback_query.message.reply_text(text, reply_markup=InlineKeyboards.back_button("market_menu", lang))
        await callback_query.answer()

    @app.on_callback_query(filters.regex("^market_sell$"))
    async def market_sell_callback(client: Client, callback_query: CallbackQuery):
        lang = "en"
        text = "💰 **Sell Item**\n\nUse: /msell <item_id> <price>"
        try:
            await callback_query.message.edit_text(text, reply_markup=InlineKeyboards.back_button("market_menu", lang))
        except Exception:
            await callback_query.message.reply_text(text, reply_markup=InlineKeyboards.back_button("market_menu", lang))
        await callback_query.answer()

    @app.on_callback_query(filters.regex("^market_auctions$"))
    async def market_auctions_callback(client: Client, callback_query: CallbackQuery):
        lang = "en"
        if callback_query._services:
            market_svc = callback_query._services.get("market")
            if market_svc:
                auctions = await market_svc.get_active_auctions(10)
                if auctions:
                    text = "🔨 **Active Auctions**\n\n"
                    for a in auctions:
                        text += f"  📦 {a.item_id} | 💰 {format_number(a.current_bid)} | ID: {a.auction_id}\n"
                else:
                    text = "No active auctions."
                try:
                    await callback_query.message.edit_text(text, reply_markup=InlineKeyboards.back_button("market_menu", lang))
                except Exception:
                    await callback_query.message.reply_text(text, reply_markup=InlineKeyboards.back_button("market_menu", lang))
        await callback_query.answer()

    @app.on_callback_query(filters.regex("^market_my_listings$"))
    async def market_my_listings_callback(client: Client, callback_query: CallbackQuery):
        user = callback_query.from_user
        lang = "en"
        if callback_query._services:
            market_svc = callback_query._services.get("market")
            if market_svc:
                listings = await market_svc.get_user_listings(user.id)
                if listings:
                    text = "📋 **My Listings**\n\n"
                    for l in listings:
                        text += f"  📦 {l.item_id} | 💰 {format_number(l.price)} | ID: {l.listing_id}\n"
                else:
                    text = "No active listings."
                try:
                    await callback_query.message.edit_text(text, reply_markup=InlineKeyboards.back_button("market_menu", lang))
                except Exception:
                    await callback_query.message.reply_text(text, reply_markup=InlineKeyboards.back_button("market_menu", lang))
        await callback_query.answer()
