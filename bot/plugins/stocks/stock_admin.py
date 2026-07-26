from __future__ import annotations

from pyrogram import Client, filters
from pyrogram.types import Message

from config import settings
from bot.utils.helpers import format_number


def register(app: Client):

    @app.on_message(filters.command("createstock") & filters.user(settings.OWNER_ID))
    async def createstock_command(client: Client, message: Message):
        services = getattr(message, '_services', None)
        if not services:
            return
        stock_svc = services.get("stock_market")
        args = message.text.split(maxsplit=5)
        if len(args) < 6:
            await message.reply_text(
                "Usage: /createstock <TICKER> <Name> <sector> <price> <shares>\n"
                "Example: /createstock DGN Dragon Industries tech 150 500000"
            )
            return
        ticker, name, sector = args[1].upper(), args[2], args[3]
        try:
            price = float(args[4])
            shares = int(args[5])
        except (ValueError, IndexError):
            await message.reply_text("Invalid price or shares.")
            return
        try:
            stock = await stock_svc.create_stock(ticker, name, sector, price, shares, "medium")
            await message.reply_text(
                f"✅ **Stock Created**\n\n"
                f"🏢 {stock.name} ({stock.ticker})\n"
                f"💰 Price: ${stock.current_price:.2f}\n"
                f"📊 Shares: {format_number(stock.total_shares)}\n"
                f"⚡ Volatility: {stock.volatility}"
            )
        except Exception as e:
            await message.reply_text(f"❌ Error: {e}")

    @app.on_message(filters.command("deletestock") & filters.user(settings.OWNER_ID))
    async def deletestock_command(client: Client, message: Message):
        services = getattr(message, '_services', None)
        if not services:
            return
        stock_svc = services.get("stock_market")
        args = message.text.split()
        if len(args) < 2:
            await message.reply_text("Usage: /deletestock <TICKER>")
            return
        ok = await stock_svc.delete_stock(args[1])
        if ok:
            await message.reply_text(f"✅ Stock {args[1].upper()} deleted.")
        else:
            await message.reply_text(f"❌ Stock '{args[1]}' not found.")

    @app.on_message(filters.command("setstockprice") & filters.user(settings.OWNER_ID))
    async def setstockprice_command(client: Client, message: Message):
        services = getattr(message, '_services', None)
        if not services:
            return
        stock_svc = services.get("stock_market")
        args = message.text.split()
        if len(args) < 3:
            await message.reply_text("Usage: /setstockprice <TICKER> <price>")
            return
        try:
            price = float(args[2])
        except ValueError:
            await message.reply_text("Invalid price.")
            return
        ok = await stock_svc.set_stock_price(args[1], price)
        if ok:
            await message.reply_text(f"✅ {args[1].upper()} price set to ${price:.2f}")
        else:
            await message.reply_text(f"❌ Stock '{args[1]}' not found.")

    @app.on_message(filters.command("setstockvolatility") & filters.user(settings.OWNER_ID))
    async def setstockvolatility_command(client: Client, message: Message):
        services = getattr(message, '_services', None)
        if not services:
            return
        stock_svc = services.get("stock_market")
        args = message.text.split()
        if len(args) < 3:
            await message.reply_text("Usage: /setstockvolatility <TICKER> <low|medium|high|extreme>")
            return
        ok = await stock_svc.set_stock_volatility(args[1], args[2].lower())
        if ok:
            await message.reply_text(f"✅ {args[1].upper()} volatility set to {args[2]}")
        else:
            await message.reply_text("❌ Invalid volatility or stock not found.")

    @app.on_message(filters.command("marketcrash") & filters.user(settings.OWNER_ID))
    async def marketcrash_command(client: Client, message: Message):
        services = getattr(message, '_services', None)
        if not services:
            return
        stock_svc = services.get("stock_market")
        args = message.text.split()
        severity = 0.3
        if len(args) >= 2:
            try:
                severity = float(args[1])
                severity = max(0.05, min(0.9, severity))
            except ValueError:
                pass
        result = await stock_svc.market_crash(severity)
        await message.reply_text(
            f"💥 **MARKET CRASH TRIGGERED**\n\n"
            f"📉 Severity: {result['severity']*100:.0f}%\n"
            f"🏢 Affected: {result['affected']} stocks\n"
            f"⚠️ All prices dropped significantly!"
        )

    @app.on_message(filters.command("marketboom") & filters.user(settings.OWNER_ID))
    async def marketboom_command(client: Client, message: Message):
        services = getattr(message, '_services', None)
        if not services:
            return
        stock_svc = services.get("stock_market")
        args = message.text.split()
        strength = 0.2
        if len(args) >= 2:
            try:
                strength = float(args[1])
                strength = max(0.05, min(0.5, strength))
            except ValueError:
                pass
        result = await stock_svc.market_boom(strength)
        await message.reply_text(
            f"🐂 **MARKET BOOM TRIGGERED**\n\n"
            f"📈 Strength: {result['strength']*100:.0f}%\n"
            f"🏢 Affected: {result['affected']} stocks\n"
            f"🚀 All prices surged!"
        )

    @app.on_message(filters.command("triggerevent") & filters.user(settings.OWNER_ID))
    async def triggerevent_command(client: Client, message: Message):
        services = getattr(message, '_services', None)
        if not services:
            return
        stock_svc = services.get("stock_market")
        event = await stock_svc.trigger_random_event()
        if event:
            await message.reply_text(
                f"🎉 **Event Triggered!**\n\n"
                f"{event['event']}\n"
                f"📝 {event['desc']}\n"
                f"🏢 Target: {event['ticker']}\n"
                f"📊 Impact: {event['mod']*100:+.1f}%"
            )
        else:
            await message.reply_text("No event triggered this time.")

    @app.on_message(filters.command("resetstockmarket") & filters.user(settings.OWNER_ID))
    async def resetstockmarket_command(client: Client, message: Message):
        services = getattr(message, '_services', None)
        if not services:
            return
        stock_svc = services.get("stock_market")
        args = message.text.split()
        if len(args) >= 2 and args[1] == "confirm":
            await stock_svc.reset_market()
            await message.reply_text("✅ Stock market prices reset to defaults.")
            return
        await message.reply_text("⚠️ This resets ALL stock prices!\nUse /resetstockmarket confirm")

    @app.on_message(filters.command("stockstatus") & filters.user(settings.OWNER_ID))
    async def stockstatus_command(client: Client, message: Message):
        services = getattr(message, '_services', None)
        if not services:
            return
        stock_svc = services.get("stock_market")
        stocks = await stock_svc.get_all_stocks()
        text = f"📊 **Stock Market Status**\n\n🏢 Total Stocks: {len(stocks)}\n\n"
        sectors = {}
        for s in stocks:
            if s.sector not in sectors:
                sectors[s.sector] = []
            sectors[s.sector].append(s)
        for sector, stocks_list in sorted(sectors.items()):
            text += f"📁 **{sector.title()}**: {len(stocks_list)} stocks\n"
        await message.reply_text(text)

    @app.on_message(filters.command("setstockupdateinterval") & filters.user(settings.OWNER_ID))
    async def setstockupdateinterval_command(client: Client, message: Message):
        services = getattr(message, '_services', None)
        if not services:
            return
        stock_svc = services.get("stock_market")
        args = message.text.split()
        if len(args) < 2:
            await message.reply_text("Usage: /setstockupdateinterval <minutes>\nNote: Takes effect on next bot restart.")
            return
        try:
            mins = int(args[1])
            await message.reply_text(f"✅ Update interval set to {mins} minutes. Restart bot to apply.")
        except ValueError:
            await message.reply_text("Invalid number.")
