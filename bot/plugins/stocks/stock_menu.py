from __future__ import annotations

from pyrogram import Client, filters
from pyrogram.types import Message, CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup

from bot.core import loc
from bot.keyboards.inline import InlineKeyboards
from bot.utils.helpers import format_number


def register(app: Client):

    @app.on_message(filters.command("stocks"))
    async def stocks_command(client: Client, message: Message):
        services = getattr(message, '_services', None)
        if not services:
            return
        stock_svc = services.get("stock_market")
        if not stock_svc:
            return
        stock_count = await stock_svc.stock_repo.count_stocks()
        text = (
            f"📈 **Virtual Stock Market**\n\n"
            f"🏢 Companies Listed: {stock_count}\n"
            f"💰 Tax Rate: 2%\n\n"
            "Buy low, sell high. Prices change every 10 minutes!\n"
        )
        kb = _stocks_main_kb()
        await message.reply_text(text, reply_markup=kb)

    @app.on_callback_query(filters.regex("^stocks_menu$"))
    async def stocks_menu_callback(client: Client, cb: CallbackQuery):
        services = getattr(cb, '_services', None) or getattr(cb.message, '_services', None)
        if not services:
            return
        stock_svc = services.get("stock_market")
        if stock_svc:
            stock_count = await stock_svc.stock_repo.count_stocks()
            text = f"📈 **Virtual Stock Market**\n\n🏢 Companies: {stock_count}\n"
            try:
                await cb.message.edit_text(text, reply_markup=_stocks_main_kb())
            except Exception:
                await cb.message.reply_text(text, reply_markup=_stocks_main_kb())
        await cb.answer()

    @app.on_callback_query(filters.regex("^stocks_market$"))
    async def stocks_market_callback(client: Client, cb: CallbackQuery):
        services = getattr(cb, '_services', None) or getattr(cb.message, '_services', None)
        if not services:
            return
        stock_svc = services.get("stock_market")
        if stock_svc:
            stocks = await stock_svc.get_all_stocks()
            text = "📈 **Market Overview**\n\n"
            for s in stocks[:20]:
                change = ((s.current_price - s.opening_price) / s.opening_price * 100) if s.opening_price > 0 else 0
                arrow = "🟢" if change >= 0 else "🔴"
                text += f"{arrow} **{s.ticker}** — {s.name[:20]} — ${s.current_price:.2f} ({change:+.1f}%)\n"
            if len(stocks) > 20:
                text += f"\n... and {len(stocks)-20} more"
            kb = InlineKeyboardMarkup([
                [InlineKeyboardButton("📊 Top Gainers", callback_data="stock_gainers"),
                 InlineKeyboardButton("📉 Top Losers", callback_data="stock_losers")],
                [InlineKeyboardButton("🔍 Search", callback_data="stock_search"),
                 InlineKeyboardButton("⭐ Watchlist", callback_data="stock_watchlist")],
                [InlineKeyboardButton("◀️ Back", callback_data="stocks_menu")],
            ])
            try:
                await cb.message.edit_text(text, reply_markup=kb)
            except Exception:
                pass
        await cb.answer()

    @app.on_callback_query(filters.regex("^stock_gainers$"))
    async def stock_gainers_callback(client: Client, cb: CallbackQuery):
        services = getattr(cb, '_services', None) or getattr(cb.message, '_services', None)
        if not services:
            return
        stock_svc = services.get("stock_market")
        if stock_svc:
            gainers = await stock_svc.get_top_gainers(10)
            text = "📊 **Top Gainers Today**\n\n"
            medals = ["🥇", "🥈", "🥉"]
            for i, s in enumerate(gainers):
                change = ((s.current_price - s.opening_price) / s.opening_price * 100) if s.opening_price > 0 else 0
                medal = medals[i] if i < 3 else f"#{i+1}"
                text += f"{medal} **{s.ticker}** — ${s.current_price:.2f} ({change:+.1f}%)\n"
            if not gainers:
                text += "No data yet."
            kb = InlineKeyboardMarkup([[InlineKeyboardButton("◀️ Back", callback_data="stocks_market")]])
            try:
                await cb.message.edit_text(text, reply_markup=kb)
            except Exception:
                pass
        await cb.answer()

    @app.on_callback_query(filters.regex("^stock_losers$"))
    async def stock_losers_callback(client: Client, cb: CallbackQuery):
        services = getattr(cb, '_services', None) or getattr(cb.message, '_services', None)
        if not services:
            return
        stock_svc = services.get("stock_market")
        if stock_svc:
            losers = await stock_svc.get_top_losers(10)
            text = "📉 **Top Losers Today**\n\n"
            medals = ["🥇", "🥈", "🥉"]
            for i, s in enumerate(losers):
                change = ((s.current_price - s.opening_price) / s.opening_price * 100) if s.opening_price > 0 else 0
                medal = medals[i] if i < 3 else f"#{i+1}"
                text += f"{medal} **{s.ticker}** — ${s.current_price:.2f} ({change:+.1f}%)\n"
            if not losers:
                text += "No data yet."
            kb = InlineKeyboardMarkup([[InlineKeyboardButton("◀️ Back", callback_data="stocks_market")]])
            try:
                await cb.message.edit_text(text, reply_markup=kb)
            except Exception:
                pass
        await cb.answer()

    @app.on_callback_query(filters.regex("^stock_search$"))
    async def stock_search_callback(client: Client, cb: CallbackQuery):
        text = "🔍 **Search Stocks**\n\nSend: `/stocksearch <query>`\n\nSearch by ticker, name, or sector."
        kb = InlineKeyboardMarkup([[InlineKeyboardButton("◀️ Back", callback_data="stocks_menu")]])
        try:
            await cb.message.edit_text(text, reply_markup=kb)
        except Exception:
            pass
        await cb.answer()

    @app.on_callback_query(filters.regex("^stock_watchlist$"))
    async def stock_watchlist_callback(client: Client, cb: CallbackQuery):
        services = getattr(cb, '_services', None) or getattr(cb.message, '_services', None)
        if not services:
            return
        stock_svc = services.get("stock_market")
        if stock_svc:
            wl = await stock_svc.get_watchlist(cb.from_user.id)
            text = "⭐ **Your Watchlist**\n\n"
            if wl:
                for item in wl:
                    arrow = "🟢" if item["change"] >= 0 else "🔴"
                    text += f"{arrow} **{item['ticker']}** — ${item['price']:.2f} ({item['change']:+.1f}%)\n"
            else:
                text += "Empty. Add stocks with `/addwatch <ticker>`"
            kb = InlineKeyboardMarkup([[InlineKeyboardButton("◀️ Back", callback_data="stocks_menu")]])
            try:
                await cb.message.edit_text(text, reply_markup=kb)
            except Exception:
                pass
        await cb.answer()

    @app.on_message(filters.command("stockinfo"))
    async def stockinfo_command(client: Client, message: Message):
        services = getattr(message, '_services', None)
        if not services:
            return
        stock_svc = services.get("stock_market")
        args = message.text.split()
        if len(args) < 2:
            await message.reply_text("Usage: /stockinfo <ticker>")
            return
        info = await stock_svc.get_stock_info(args[1])
        if not info:
            await message.reply_text(f"❌ Stock '{args[1]}' not found.")
            return
        change = info["change_pct"]
        arrow = "🟢" if change >= 0 else "🔴"
        text = (
            f"📈 **{info['name']}** ({info['ticker']})\n\n"
            f"💰 Price: ${info['price']:.2f}\n"
            f"{arrow} Change: {change:+.2f}%\n"
            f"📊 Open: ${info['open']:.2f}\n"
            f"📉 Prev Close: ${info['prev_close']:.2f}\n"
            f"📈 High: ${info['high']:.2f}\n"
            f"📉 Low: ${info['low']:.2f}\n"
            f"📦 Volume: {format_number(info['volume'])}\n"
            f"🏢 Market Cap: ${format_number(int(info['market_cap']))}\n"
            f"⚡ Volatility: {info['volatility']}\n"
            f"🔥 Popularity: {info['popularity']:.0f}/100\n"
            f"📊 Available: {format_number(info['available'])}/{format_number(info['total'])} shares\n"
        )
        kb = InlineKeyboardMarkup([
            [InlineKeyboardButton("🛒 Buy", callback_data=f"stock_buy_{info['ticker']}"),
             InlineKeyboardButton("💰 Sell", callback_data=f"stock_sell_{info['ticker']}")],
            [InlineKeyboardButton("⭐ Watch", callback_data=f"stock_addwatch_{info['ticker']}"),
             InlineKeyboardButton("📜 History", callback_data=f"stock_history_{info['ticker']}")],
            [InlineKeyboardButton("◀️ Back", callback_data="stocks_menu")],
        ])
        await message.reply_text(text, reply_markup=kb)

    @app.on_message(filters.command("buy"))
    async def buy_command(client: Client, message: Message):
        services = getattr(message, '_services', None)
        if not services:
            return
        stock_svc = services.get("stock_market")
        eco_svc = services.get("economy")
        args = message.text.split()
        if len(args) < 3:
            await message.reply_text("Usage: /buy <ticker> <shares>")
            return
        ticker = args[1].upper()
        try:
            shares = int(args[2])
        except ValueError:
            await message.reply_text("Invalid share count.")
            return
        balance = await eco_svc.get_balance(message.from_user.id)
        result = await stock_svc.buy_shares(message.from_user.id, ticker, shares, balance["wallet"])
        if result["success"]:
            await eco_svc.remove_coins(message.from_user.id, result["total_with_tax"], f"Stock buy: {ticker}")
            await message.reply_text(
                f"✅ **Bought {result['shares']} shares of {ticker}**\n\n"
                f"💰 Price: ${result['price']:.2f}/share\n"
                f"💳 Total: ${result['total']:,}\n"
                f"📋 Tax: ${result['tax']:,}\n"
                f"📊 New Avg Price: ${result['new_avg']:.2f}"
            )
        else:
            reason = result.get("reason", "unknown")
            await message.reply_text(f"❌ Purchase failed: {reason}")

    @app.on_message(filters.command("sell"))
    async def sell_command(client: Client, message: Message):
        services = getattr(message, '_services', None)
        if not services:
            return
        stock_svc = services.get("stock_market")
        eco_svc = services.get("economy")
        args = message.text.split()
        if len(args) < 3:
            await message.reply_text("Usage: /sell <ticker> <shares>")
            return
        ticker = args[1].upper()
        try:
            shares = int(args[2])
        except ValueError:
            await message.reply_text("Invalid share count.")
            return
        result = await stock_svc.sell_shares(message.from_user.id, ticker, shares)
        if result["success"]:
            await eco_svc.add_coins(message.from_user.id, result["net"], f"Stock sell: {ticker}")
            emoji = "📈" if result["profit"] >= 0 else "📉"
            await message.reply_text(
                f"✅ **Sold {result['shares']} shares of {ticker}**\n\n"
                f"💰 Price: ${result['price']:.2f}/share\n"
                f"💵 Received: ${result['net']:,}\n"
                f"📋 Tax: ${result['tax']:,}\n"
                f"{emoji} Profit: ${result['profit']:,}"
            )
        else:
            reason = result.get("reason", "unknown")
            await message.reply_text(f"❌ Sale failed: {reason}")

    @app.on_message(filters.command("portfolio"))
    async def portfolio_command(client: Client, message: Message):
        services = getattr(message, '_services', None)
        if not services:
            return
        stock_svc = services.get("stock_market")
        portfolio = await stock_svc.get_portfolio(message.from_user.id)
        if not portfolio:
            await message.reply_text("📊 **Your Portfolio**\n\nEmpty. Buy stocks with `/buy <ticker> <shares>`")
            return
        text = "💼 **Your Portfolio**\n\n"
        total_value = 0
        total_profit = 0
        for h in portfolio:
            if h["shares"] <= 0:
                continue
            arrow = "🟢" if h["profit"] >= 0 else "🔴"
            fav = "⭐" if h["is_favorite"] else ""
            sl = f" 🛑{h['stop_loss']}%" if h["stop_loss"] else ""
            tp = f" 🎯{h['take_profit']}%" if h["take_profit"] else ""
            text += (
                f"{fav}{arrow} **{h['ticker']}** — {h['shares']} shares\n"
                f"   Avg: ${h['avg_buy']:.2f} → Now: ${h['current']:.2f}\n"
                f"   Value: ${h['value']:,} | P/L: ${h['profit']:,} ({h['pct']:+.1f}%){sl}{tp}\n\n"
            )
            total_value += h["value"]
            total_profit += h["profit"]
        text += f"📊 Total Value: ${total_value:,}\n"
        text += f"💰 Total P/L: ${total_profit:,}"
        await message.reply_text(text)

    @app.on_message(filters.command("watchlist") | filters.command("wl"))
    async def watchlist_command(client: Client, message: Message):
        services = getattr(message, '_services', None)
        if not services:
            return
        stock_svc = services.get("stock_market")
        wl = await stock_svc.get_watchlist(message.from_user.id)
        text = "⭐ **Your Watchlist**\n\n"
        if wl:
            for item in wl:
                arrow = "🟢" if item["change"] >= 0 else "🔴"
                text += f"{arrow} **{item['ticker']}** — ${item['price']:.2f} ({item['change']:+.1f}%)\n"
        else:
            text += "Empty. Add with `/addwatch <ticker>`"
        await message.reply_text(text)

    @app.on_message(filters.command("addwatch"))
    async def addwatch_command(client: Client, message: Message):
        services = getattr(message, '_services', None)
        if not services:
            return
        stock_svc = services.get("stock_market")
        args = message.text.split()
        if len(args) < 2:
            await message.reply_text("Usage: /addwatch <ticker>")
            return
        ok = await stock_svc.add_to_watchlist(message.from_user.id, args[1])
        if ok:
            await message.reply_text(f"✅ {args[1].upper()} added to watchlist.")
        else:
            await message.reply_text(f"❌ Stock '{args[1]}' not found.")

    @app.on_message(filters.command("removewatch"))
    async def removewatch_command(client: Client, message: Message):
        services = getattr(message, '_services', None)
        if not services:
            return
        stock_svc = services.get("stock_market")
        args = message.text.split()
        if len(args) < 2:
            await message.reply_text("Usage: /removewatch <ticker>")
            return
        ok = await stock_svc.remove_from_watchlist(message.from_user.id, args[1])
        if ok:
            await message.reply_text(f"✅ {args[1].upper()} removed from watchlist.")
        else:
            await message.reply_text("❌ Not on your watchlist.")

    @app.on_message(filters.command("stockhistory"))
    async def stockhistory_command(client: Client, message: Message):
        services = getattr(message, '_services', None)
        if not services:
            return
        stock_svc = services.get("stock_market")
        args = message.text.split()
        if len(args) < 2:
            await message.reply_text("Usage: /stockhistory <ticker>")
            return
        history = await stock_svc.get_history(args[1].upper(), 15)
        if not history:
            await message.reply_text("❌ No price history found.")
            return
        text = f"📜 **Price History — {args[1].upper()}**\n\n"
        for h in history:
            text += f"  ${h.price:.2f} | Vol: {format_number(h.volume)} | {h.recorded_at.strftime('%m-%d %H:%M')}\n"
        await message.reply_text(text)

    @app.on_message(filters.command("stocksearch"))
    async def stocksearch_command(client: Client, message: Message):
        services = getattr(message, '_services', None)
        if not services:
            return
        stock_svc = services.get("stock_market")
        args = message.text.split(maxsplit=1)
        if len(args) < 2:
            await message.reply_text("Usage: /stocksearch <query>")
            return
        results = await stock_svc.search_stocks(args[1])
        text = f"🔍 **Search: {args[1]}**\n\n"
        for s in results[:15]:
            change = ((s.current_price - s.opening_price) / s.opening_price * 100) if s.opening_price > 0 else 0
            arrow = "🟢" if change >= 0 else "🔴"
            text += f"{arrow} **{s.ticker}** — {s.name[:25]} — ${s.current_price:.2f} ({change:+.1f}%)\n"
        if not results:
            text += "No stocks found."
        await message.reply_text(text)

    @app.on_message(filters.command("stoploss"))
    async def stoploss_command(client: Client, message: Message):
        services = getattr(message, '_services', None)
        if not services:
            return
        stock_svc = services.get("stock_market")
        args = message.text.split()
        if len(args) < 3:
            await message.reply_text("Usage: /stoploss <ticker> <percent>\nExample: /stoploss DGN 15")
            return
        try:
            pct = float(args[2].replace("%", ""))
        except ValueError:
            await message.reply_text("Invalid percentage.")
            return
        result = await stock_svc.set_stop_loss(message.from_user.id, args[1], pct)
        if result["success"]:
            await message.reply_text(f"✅ Stop loss set for {args[1].upper()} at {pct}% loss.")
        else:
            await message.reply_text(f"❌ {result.get('reason', 'Failed')}")

    @app.on_message(filters.command("takeprofit"))
    async def takeprofit_command(client: Client, message: Message):
        services = getattr(message, '_services', None)
        if not services:
            return
        stock_svc = services.get("stock_market")
        args = message.text.split()
        if len(args) < 3:
            await message.reply_text("Usage: /takeprofit <ticker> <percent>\nExample: /takeprofit DGN 30")
            return
        try:
            pct = float(args[2].replace("%", ""))
        except ValueError:
            await message.reply_text("Invalid percentage.")
            return
        result = await stock_svc.set_take_profit(message.from_user.id, args[1], pct)
        if result["success"]:
            await message.reply_text(f"✅ Take profit set for {args[1].upper()} at {pct}% gain.")
        else:
            await message.reply_text(f"❌ {result.get('reason', 'Failed')}")

    @app.on_message(filters.command("topgainers"))
    async def topgainers_command(client: Client, message: Message):
        services = getattr(message, '_services', None)
        if not services:
            return
        stock_svc = services.get("stock_market")
        gainers = await stock_svc.get_top_gainers(10)
        text = "📊 **Top Gainers Today**\n\n"
        medals = ["🥇", "🥈", "🥉"]
        for i, s in enumerate(gainers):
            change = ((s.current_price - s.opening_price) / s.opening_price * 100) if s.opening_price > 0 else 0
            medal = medals[i] if i < 3 else f"#{i+1}"
            text += f"{medal} **{s.ticker}** — {s.name[:20]} — ${s.current_price:.2f} ({change:+.1f}%)\n"
        if not gainers:
            text += "No data yet."
        await message.reply_text(text)

    @app.on_message(filters.command("toplosers"))
    async def toplosers_command(client: Client, message: Message):
        services = getattr(message, '_services', None)
        if not services:
            return
        stock_svc = services.get("stock_market")
        losers = await stock_svc.get_top_losers(10)
        text = "📉 **Top Losers Today**\n\n"
        medals = ["🥇", "🥈", "🥉"]
        for i, s in enumerate(losers):
            change = ((s.current_price - s.opening_price) / s.opening_price * 100) if s.opening_price > 0 else 0
            medal = medals[i] if i < 3 else f"#{i+1}"
            text += f"{medal} **{s.ticker}** — {s.name[:20]} — ${s.current_price:.2f} ({change:+.1f}%)\n"
        if not losers:
            text += "No data yet."
        await message.reply_text(text)

    @app.on_message(filters.command("stockstats"))
    async def stockstats_command(client: Client, message: Message):
        services = getattr(message, '_services', None)
        if not services:
            return
        stock_svc = services.get("stock_market")
        stats = await stock_svc.get_portfolio_stats(message.from_user.id)
        trades = await stock_svc.get_user_trade_count(message.from_user.id)
        text = (
            f"📊 **Your Stock Stats**\n\n"
            f"💼 Stocks Owned: {stats['stocks_count']}\n"
            f"💰 Total Invested: ${format_number(stats['total_invested'])}\n"
            f"📈 Current Value: ${format_number(stats['total_value'])}\n"
            f"📊 Current P/L: ${format_number(stats['total_profit'])}\n"
            f"📈 Lifetime Profit: ${format_number(stats['lifetime_profit'])}\n"
            f"📉 Lifetime Loss: ${format_number(stats['lifetime_loss'])}\n"
            f"🔄 Total Trades: {trades}\n"
        )
        await message.reply_text(text)

    @app.on_message(filters.command("stocklb") | filters.command("stockleaderboard"))
    async def stock_leaderboard_command(client: Client, message: Message):
        text = "🏆 **Stock Market Leaderboards**\n\nSelect category:"
        kb = InlineKeyboardMarkup([
            [InlineKeyboardButton("💰 Top Investors", callback_data="stocklb_investors"),
             InlineKeyboardButton("📈 Highest P/L", callback_data="stocklb_profit")],
            [InlineKeyboardButton("📊 Best ROI", callback_data="stocklb_roi"),
             InlineKeyboardButton("🔄 Most Active", callback_data="stocklb_active")],
            [InlineKeyboardButton("🏆 Most Stocks", callback_data="stocklb_most"),
             InlineKeyboardButton("📉 Biggest Loss", callback_data="stocklb_loss")],
            [InlineKeyboardButton("◀️ Back", callback_data="stocks_menu")],
        ])
        await message.reply_text(text, reply_markup=kb)

    @app.on_callback_query(filters.regex("^stocklb_investors$"))
    async def stocklb_investors_cb(client: Client, cb: CallbackQuery):
        services = getattr(cb, '_services', None) or getattr(cb.message, '_services', None)
        if not services:
            return
        stock_svc = services.get("stock_market")
        top = await stock_svc.get_top_investors(10)
        text = "💰 **Top Investors**\n\n"
        medals = ["🥇", "🥈", "🥉"]
        for i, entry in enumerate(top):
            medal = medals[i] if i < 3 else f"#{i+1}"
            text += f"{medal} `{entry['_id']}` — ${format_number(int(entry['total_value']))} ({entry['stocks_count']} stocks)\n"
        if not top:
            text += "No data."
        try:
            await cb.message.edit_text(text, reply_markup=InlineKeyboards.back_button("stocks_menu"))
        except Exception:
            pass
        await cb.answer()

    @app.on_callback_query(filters.regex("^stocklb_profit$"))
    async def stocklb_profit_cb(client: Client, cb: CallbackQuery):
        services = getattr(cb, '_services', None) or getattr(cb.message, '_services', None)
        if not services:
            return
        stock_svc = services.get("stock_market")
        top = await stock_svc.get_highest_profit(10)
        text = "📈 **Highest Profit**\n\n"
        medals = ["🥇", "🥈", "🥉"]
        for i, entry in enumerate(top):
            medal = medals[i] if i < 3 else f"#{i+1}"
            text += f"{medal} `{entry['_id']}` — ${format_number(int(entry['total_profit']))}\n"
        if not top:
            text += "No data."
        try:
            await cb.message.edit_text(text, reply_markup=InlineKeyboards.back_button("stocks_menu"))
        except Exception:
            pass
        await cb.answer()

    @app.on_callback_query(filters.regex("^stocklb_roi$"))
    async def stocklb_roi_cb(client: Client, cb: CallbackQuery):
        services = getattr(cb, '_services', None) or getattr(cb.message, '_services', None)
        if not services:
            return
        stock_svc = services.get("stock_market")
        top = await stock_svc.get_best_roi(10)
        text = "📊 **Best ROI**\n\n"
        medals = ["🥇", "🥈", "🥉"]
        for i, entry in enumerate(top):
            medal = medals[i] if i < 3 else f"#{i+1}"
            text += f"{medal} `{entry['_id']}` — {entry.get('roi', 0):.1f}%\n"
        if not top:
            text += "No data."
        try:
            await cb.message.edit_text(text, reply_markup=InlineKeyboards.back_button("stocks_menu"))
        except Exception:
            pass
        await cb.answer()

    @app.on_callback_query(filters.regex("^stocklb_active$"))
    async def stocklb_active_cb(client: Client, cb: CallbackQuery):
        services = getattr(cb, '_services', None) or getattr(cb.message, '_services', None)
        if not services:
            return
        stock_svc = services.get("stock_market")
        top = await stock_svc.get_most_active(10)
        text = "🔄 **Most Active Traders**\n\n"
        medals = ["🥇", "🥈", "🥉"]
        for i, entry in enumerate(top):
            medal = medals[i] if i < 3 else f"#{i+1}"
            text += f"{medal} `{entry['_id']}` — {entry['total_shares']} shares ({entry['stocks_count']} stocks)\n"
        if not top:
            text += "No data."
        try:
            await cb.message.edit_text(text, reply_markup=InlineKeyboards.back_button("stocks_menu"))
        except Exception:
            pass
        await cb.answer()

    @app.on_callback_query(filters.regex("^stocklb_most$"))
    async def stocklb_most_cb(client: Client, cb: CallbackQuery):
        services = getattr(cb, '_services', None) or getattr(cb.message, '_services', None)
        if not services:
            return
        stock_svc = services.get("stock_market")
        top = await stock_svc.get_most_active(10)
        text = "🏆 **Most Stocks Owned**\n\n"
        medals = ["🥇", "🥈", "🥉"]
        for i, entry in enumerate(top):
            medal = medals[i] if i < 3 else f"#{i+1}"
            text += f"{medal} `{entry['_id']}` — {entry['stocks_count']} unique stocks\n"
        if not top:
            text += "No data."
        try:
            await cb.message.edit_text(text, reply_markup=InlineKeyboards.back_button("stocks_menu"))
        except Exception:
            pass
        await cb.answer()

    @app.on_callback_query(filters.regex("^stocklb_loss$"))
    async def stocklb_loss_cb(client: Client, cb: CallbackQuery):
        services = getattr(cb, '_services', None) or getattr(cb.message, '_services', None)
        if not services:
            return
        stock_svc = services.get("stock_market")
        top = await stock_svc.get_highest_loss(10)
        text = "📉 **Biggest Losses**\n\n"
        medals = ["🥇", "🥈", "🥉"]
        for i, entry in enumerate(top):
            medal = medals[i] if i < 3 else f"#{i+1}"
            text += f"{medal} `{entry['_id']}` — ${format_number(int(entry['total_loss']))}\n"
        if not top:
            text += "No data."
        try:
            await cb.message.edit_text(text, reply_markup=InlineKeyboards.back_button("stocks_menu"))
        except Exception:
            pass
        await cb.answer()


def _stocks_main_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("📈 Market", callback_data="stocks_market"),
         InlineKeyboardButton("💼 Portfolio", callback_data="stocks_portfolio")],
        [InlineKeyboardButton("⭐ Watchlist", callback_data="stock_watchlist"),
         InlineKeyboardButton("📜 History", callback_data="stocks_history")],
        [InlineKeyboardButton("📊 Top Gainers", callback_data="stock_gainers"),
         InlineKeyboardButton("📉 Top Losers", callback_data="stock_losers")],
        [InlineKeyboardButton("🏆 Rankings", callback_data="stocks_rankings"),
         InlineKeyboardButton("🔍 Search", callback_data="stock_search")],
        [InlineKeyboardButton("◀️ Back", callback_data="main_menu")],
    ])
