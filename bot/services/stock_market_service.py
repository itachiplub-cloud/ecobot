from __future__ import annotations

import asyncio
import random
from datetime import datetime, timedelta, timezone, timezone
from typing import Optional

from motor.motor_asyncio import AsyncIOMotorDatabase

from bot.database.repositories.stock_repo import StockRepository
from bot.database.repositories.stock_portfolio_repo import StockPortfolioRepository
from bot.database.repositories.stock_transaction_repo import StockTransactionRepository
from bot.database.repositories.stock_event_repo import StockMarketEventRepository
from bot.database.repositories.stock_watchlist_repo import StockWatchlistRepository
from bot.database.repositories.stock_price_history_repo import StockPriceHistoryRepository
from bot.database.models.stock import StockModel
from bot.database.models.stock_portfolio import StockPortfolioModel
from bot.database.models.stock_transaction import StockTransactionModel
from bot.database.models.stock_market_event import StockMarketEventModel
from bot.database.models.stock_price_history import StockPriceHistoryModel

TAX_RATE = 0.02

VOLATILITY_CONFIGS = {
    "low": {"min_change": -0.005, "max_change": 0.005, "event_multiplier": 0.5},
    "medium": {"min_change": -0.02, "max_change": 0.02, "event_multiplier": 1.0},
    "high": {"min_change": -0.05, "max_change": 0.05, "event_multiplier": 1.5},
    "extreme": {"min_change": -0.10, "max_change": 0.10, "event_multiplier": 2.0},
}

MARKET_EVENTS = [
    {"type": "earnings", "title": "📈 Company Earnings Report", "desc": "Strong quarterly earnings!", "mod": 0.05, "global": False},
    {"type": "scandal", "title": "📉 Company Scandal", "desc": "CEO involved in scandal!", "mod": -0.08, "global": False},
    {"type": "launch", "title": "🚀 Product Launch", "desc": "New blockbuster product announced!", "mod": 0.07, "global": False},
    {"type": "fire", "title": "🔥 Factory Fire", "desc": "Major factory damaged by fire!", "mod": -0.06, "global": False},
    {"type": "subsidy", "title": "💰 Government Subsidy", "desc": "Government grants subsidy!", "mod": 0.04, "global": False},
    {"type": "rumor", "title": "⚠️ Bankruptcy Rumor", "desc": "Rumors of financial trouble!", "mod": -0.10, "global": False},
    {"type": "boom", "title": "🌎 Global Economic Boom", "desc": "Markets rally worldwide!", "mod": 0.03, "global": True},
    {"type": "crash", "title": "💥 Market Crash", "desc": "Panic selling across all sectors!", "mod": -0.12, "global": True},
    {"type": "bull", "title": "🐂 Bull Market", "desc": "Investors are optimistic!", "mod": 0.02, "global": True},
    {"type": "bear", "title": "🐻 Bear Market", "desc": "Market sentiment turns negative.", "mod": -0.02, "global": True},
    {"type": "merger", "title": "🤝 Merger Announcement", "desc": "Major merger deal signed!", "mod": 0.06, "global": False},
    {"type": "lawsuit", "title": "⚖️ Major Lawsuit", "desc": "Facing massive lawsuit!", "mod": -0.05, "global": False},
    {"type": "patent", "title": "💡 Patent Breakthrough", "desc": "Revolutionary patent filed!", "mod": 0.08, "global": False},
    {"type": "recall", "title": "📦 Product Recall", "desc": "Millions of products recalled!", "mod": -0.04, "global": False},
    {"type": "expansion", "title": "🌏 Global Expansion", "desc": "Entering new international markets!", "mod": 0.05, "global": False},
]


class StockMarketService:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.stock_repo = StockRepository(db)
        self.portfolio_repo = StockPortfolioRepository(db)
        self.tx_repo = StockTransactionRepository(db)
        self.event_repo = StockMarketEventRepository(db)
        self.watchlist_repo = StockWatchlistRepository(db)
        self.history_repo = StockPriceHistoryRepository(db)
        self.db = db
        self._running = False
        self._task: Optional[asyncio.Task] = None

    async def buy_shares(self, user_id: int, ticker: str, shares: int, wallet_balance: int) -> dict:
        stock = await self.stock_repo.get_stock(ticker)
        if not stock or not stock.is_active:
            return {"success": False, "reason": "not_found"}
        if shares <= 0:
            return {"success": False, "reason": "invalid_amount"}
        if shares > stock.available_shares:
            return {"success": False, "reason": "insufficient_shares", "available": stock.available_shares}

        total_cost = int(stock.current_price * shares)
        tax = int(total_cost * TAX_RATE)
        total_with_tax = total_cost + tax

        if total_with_tax > wallet_balance:
            return {"success": False, "reason": "insufficient_funds", "needed": total_with_tax}

        holding = await self.portfolio_repo.get_holding(user_id, ticker)
        if holding:
            old_total = holding.shares * holding.avg_buy_price
            new_total = old_total + total_cost
            new_shares = holding.shares + shares
            new_avg = new_total / new_shares
            holding.shares = new_shares
            holding.avg_buy_price = new_avg
            holding.total_invested += total_cost
        else:
            holding = StockPortfolioModel(
                user_id=user_id, ticker=ticker.upper(),
                shares=shares, avg_buy_price=stock.current_price,
                total_invested=total_cost,
            )

        await self.portfolio_repo.upsert_holding(holding)
        await self.stock_repo.update_stock(ticker,
            available_shares=stock.available_shares - shares,
            daily_volume=stock.daily_volume + shares,
        )

        tx = StockTransactionModel(
            user_id=user_id, ticker=ticker.upper(), action="buy",
            shares=shares, price_per_share=stock.current_price,
            total_amount=total_cost, tax=tax,
        )
        await self.tx_repo.add_transaction(tx)

        return {
            "success": True, "shares": shares, "price": stock.current_price,
            "total": total_cost, "tax": tax, "total_with_tax": total_with_tax,
            "new_avg": holding.avg_buy_price,
        }

    async def sell_shares(self, user_id: int, ticker: str, shares: int) -> dict:
        stock = await self.stock_repo.get_stock(ticker)
        if not stock:
            return {"success": False, "reason": "not_found"}

        holding = await self.portfolio_repo.get_holding(user_id, ticker)
        if not holding or holding.shares < shares:
            return {"success": False, "reason": "insufficient_shares", "owned": holding.shares if holding else 0}

        total_sale = int(stock.current_price * shares)
        tax = int(total_sale * TAX_RATE)
        net_sale = total_sale - tax

        profit_per_share = stock.current_price - holding.avg_buy_price
        profit = int(profit_per_share * shares) - tax
        if profit > 0:
            holding.lifetime_profit += profit
        else:
            holding.lifetime_loss += abs(profit)

        holding.shares -= shares
        holding.total_sold += shares
        holding.last_updated = datetime.now(timezone.utc)

        await self.portfolio_repo.upsert_holding(holding)
        await self.stock_repo.update_stock(ticker,
            available_shares=stock.available_shares + shares,
            daily_volume=stock.daily_volume + shares,
        )

        tx = StockTransactionModel(
            user_id=user_id, ticker=ticker.upper(), action="sell",
            shares=shares, price_per_share=stock.current_price,
            total_amount=total_sale, tax=tax, profit=profit,
        )
        await self.tx_repo.add_transaction(tx)

        return {
            "success": True, "shares": shares, "price": stock.current_price,
            "total": total_sale, "tax": tax, "net": net_sale, "profit": profit,
        }

    async def get_portfolio(self, user_id: int) -> list[dict]:
        holdings = await self.portfolio_repo.get_user_portfolio(user_id)
        result = []
        for h in holdings:
            stock = await self.stock_repo.get_stock(h.ticker)
            current_price = stock.current_price if stock else 0
            value = int(current_price * h.shares)
            profit = int((current_price - h.avg_buy_price) * h.shares)
            pct = ((current_price - h.avg_buy_price) / h.avg_buy_price * 100) if h.avg_buy_price > 0 else 0
            result.append({
                "ticker": h.ticker, "shares": h.shares,
                "avg_buy": h.avg_buy_price, "current": current_price,
                "value": value, "profit": profit, "pct": pct,
                "stop_loss": h.stop_loss_pct, "take_profit": h.take_profit_pct,
                "is_favorite": h.is_favorite,
                "lifetime_profit": h.lifetime_profit, "lifetime_loss": h.lifetime_loss,
            })
        return result

    async def set_stop_loss(self, user_id: int, ticker: str, pct: float) -> dict:
        stock = await self.stock_repo.get_stock(ticker)
        if not stock:
            return {"success": False, "reason": "not_found"}
        holding = await self.portfolio_repo.get_holding(user_id, ticker)
        if not holding or holding.shares <= 0:
            return {"success": False, "reason": "no_position"}
        if pct <= 0 or pct >= 100:
            return {"success": False, "reason": "invalid_pct"}
        await self.portfolio_repo.update_holding(user_id, ticker, stop_loss_pct=pct)
        return {"success": True, "pct": pct}

    async def set_take_profit(self, user_id: int, ticker: str, pct: float) -> dict:
        stock = await self.stock_repo.get_stock(ticker)
        if not stock:
            return {"success": False, "reason": "not_found"}
        holding = await self.portfolio_repo.get_holding(user_id, ticker)
        if not holding or holding.shares <= 0:
            return {"success": False, "reason": "no_position"}
        if pct <= 0 or pct >= 500:
            return {"success": False, "reason": "invalid_pct"}
        await self.portfolio_repo.update_holding(user_id, ticker, take_profit_pct=pct)
        return {"success": True, "pct": pct}

    async def check_stop_loss_take_profit(self) -> list[dict]:
        triggered = []
        sl_holdings = await self.portfolio_repo.get_stop_loss_triggers()
        for h in sl_holdings:
            stock = await self.stock_repo.get_stock(h.ticker)
            if not stock:
                continue
            loss_pct = ((h.avg_buy_price - stock.current_price) / h.avg_buy_price) * 100
            if loss_pct >= (h.stop_loss_pct or 999):
                result = await self.sell_shares(h.user_id, h.ticker, h.shares)
                if result["success"]:
                    triggered.append({"type": "stop_loss", "ticker": h.ticker, "user_id": h.user_id, "loss_pct": loss_pct})

        tp_holdings = await self.portfolio_repo.get_take_profit_triggers()
        for h in tp_holdings:
            stock = await self.stock_repo.get_stock(h.ticker)
            if not stock:
                continue
            gain_pct = ((stock.current_price - h.avg_buy_price) / h.avg_buy_price) * 100
            if gain_pct >= (h.take_profit_pct or 999):
                result = await self.sell_shares(h.user_id, h.ticker, h.shares)
                if result["success"]:
                    triggered.append({"type": "take_profit", "ticker": h.ticker, "user_id": h.user_id, "gain_pct": gain_pct})

        return triggered

    async def toggle_favorite(self, user_id: int, ticker: str) -> bool:
        holding = await self.portfolio_repo.get_holding(user_id, ticker)
        if not holding:
            return False
        new_val = not holding.is_favorite
        await self.portfolio_repo.update_holding(user_id, ticker, is_favorite=new_val)
        return new_val

    async def add_to_watchlist(self, user_id: int, ticker: str) -> bool:
        stock = await self.stock_repo.get_stock(ticker)
        if not stock:
            return False
        return await self.watchlist_repo.add_to_watchlist(user_id, ticker)

    async def remove_from_watchlist(self, user_id: int, ticker: str) -> bool:
        return await self.watchlist_repo.remove_from_watchlist(user_id, ticker)

    async def get_watchlist(self, user_id: int) -> list[dict]:
        wl = await self.watchlist_repo.get_watchlist(user_id)
        result = []
        for ticker in wl.tickers:
            stock = await self.stock_repo.get_stock(ticker)
            if stock:
                change = ((stock.current_price - stock.opening_price) / stock.opening_price * 100) if stock.opening_price > 0 else 0
                result.append({"ticker": ticker, "name": stock.name, "price": stock.current_price, "change": change})
        return result

    async def update_prices(self) -> list[dict]:
        changes = []
        stocks = await self.stock_repo.get_all_stocks()
        active_events = await self.event_repo.get_active_events()
        await self.event_repo.expire_events()

        for stock in stocks:
            vc = VOLATILITY_CONFIGS.get(stock.volatility, VOLATILITY_CONFIGS["medium"])
            change_pct = random.uniform(vc["min_change"], vc["max_change"])

            for event in active_events:
                if event.is_global or (event.ticker and event.ticker.upper() == stock.ticker):
                    em = vc["event_multiplier"]
                    change_pct += event.price_modifier * em

            popularity_factor = (stock.popularity - 50) / 500
            change_pct += popularity_factor * 0.001

            buy_pressure = max(-0.01, min(0.01, (stock.daily_volume / max(stock.total_shares, 1)) * 0.1))
            change_pct += buy_pressure

            new_price = stock.current_price * (1 + change_pct)
            new_price = max(0.01, round(new_price, 2))

            await self.stock_repo.update_stock(stock.ticker,
                current_price=new_price,
                daily_high=max(stock.daily_high, new_price) if stock.daily_high > 0 else new_price,
                daily_low=min(stock.daily_low, new_price) if stock.daily_low < 999999 else new_price,
            )

            history = StockPriceHistoryModel(
                ticker=stock.ticker, price=new_price,
                volume=stock.daily_volume,
                high=stock.daily_high if stock.daily_high > 0 else new_price,
                low=stock.daily_low if stock.daily_low < 999999 else new_price,
            )
            await self.history_repo.record_price(history)

            changes.append({"ticker": stock.ticker, "old": stock.current_price, "new": new_price, "change": change_pct * 100})

        return changes

    async def reset_daily(self) -> None:
        stocks = await self.stock_repo.get_all_stocks()
        for stock in stocks:
            await self.stock_repo.update_stock(stock.ticker,
                previous_close=stock.current_price,
                opening_price=stock.current_price,
                daily_volume=0,
                daily_high=0,
                daily_low=999999,
            )

    async def market_crash(self, severity: float = 0.3) -> dict:
        stocks = await self.stock_repo.get_all_stocks()
        crashed = []
        for stock in stocks:
            drop = random.uniform(0.1, severity)
            new_price = max(0.01, stock.current_price * (1 - drop))
            await self.stock_repo.update_stock(stock.ticker, current_price=round(new_price, 2))
            crashed.append({"ticker": stock.ticker, "drop": drop * 100})
        event = StockMarketEventModel(
            event_id=f"crash_{datetime.now(timezone.utc).timestamp()}",
            event_type="crash", title="💥 MARKET CRASH",
            description=f"Markets crashed! Severity: {severity*100:.0f}%",
            price_modifier=-severity, is_global=True, active=True,
            expires_at=datetime.now(timezone.utc) + timedelta(hours=1),
        )
        await self.event_repo.create_event(event)
        return {"affected": len(crashed), "severity": severity}

    async def market_boom(self, strength: float = 0.2) -> dict:
        stocks = await self.stock_repo.get_all_stocks()
        boomed = []
        for stock in stocks:
            gain = random.uniform(0.05, strength)
            new_price = stock.current_price * (1 + gain)
            await self.stock_repo.update_stock(stock.ticker, current_price=round(new_price, 2))
            boomed.append({"ticker": stock.ticker, "gain": gain * 100})
        event = StockMarketEventModel(
            event_id=f"boom_{datetime.now(timezone.utc).timestamp()}",
            event_type="boom", title="🐂 MARKET BOOM",
            description=f"Markets booming! Strength: {strength*100:.0f}%",
            price_modifier=strength, is_global=True, active=True,
            expires_at=datetime.now(timezone.utc) + timedelta(hours=1),
        )
        await self.event_repo.create_event(event)
        return {"affected": len(boomed), "strength": strength}

    async def trigger_random_event(self) -> Optional[dict]:
        if random.random() > 0.3:
            return None
        template = random.choice(MARKET_EVENTS)
        stock = None
        if not template["global"]:
            stocks = await self.stock_repo.get_all_stocks()
            if stocks:
                stock = random.choice(stocks)

        event = StockMarketEventModel(
            event_id=f"evt_{datetime.now(timezone.utc).timestamp()}_{random.randint(1000,9999)}",
            event_type=template["type"],
            ticker=stock.ticker if stock else None,
            title=template["title"],
            description=template["desc"],
            price_modifier=template["mod"],
            is_global=template["global"],
            active=True,
            expires_at=datetime.now(timezone.utc) + timedelta(minutes=random.randint(10, 60)),
        )
        await self.event_repo.create_event(event)

        if stock:
            new_price = max(0.01, stock.current_price * (1 + template["mod"]))
            await self.stock_repo.update_stock(stock.ticker, current_price=round(new_price, 2))

        return {"event": template["title"], "desc": template["desc"], "ticker": stock.ticker if stock else "ALL", "mod": template["mod"]}

    async def get_history(self, ticker: str, limit: int = 20) -> list[StockPriceHistoryModel]:
        return await self.history_repo.get_price_history(ticker, limit)

    async def get_transaction_history(self, user_id: int, limit: int = 20) -> list[StockTransactionModel]:
        return await self.tx_repo.get_user_transactions(user_id, limit=limit)

    async def get_user_trade_count(self, user_id: int) -> int:
        return await self.tx_repo.get_user_trades(user_id)

    async def create_stock(self, ticker: str, name: str, sector: str, price: float, shares: int, volatility: str) -> StockModel:
        stock = StockModel(
            ticker=ticker.upper(), name=name, sector=sector,
            current_price=price, opening_price=price, previous_close=price,
            market_cap=price * shares, total_shares=shares, available_shares=shares,
            volatility=volatility, daily_high=price, daily_low=price,
        )
        return await self.stock_repo.create_stock(stock)

    async def delete_stock(self, ticker: str) -> bool:
        return await self.stock_repo.delete_stock(ticker)

    async def set_stock_price(self, ticker: str, price: float) -> bool:
        stock = await self.stock_repo.get_stock(ticker)
        if not stock:
            return False
        await self.stock_repo.update_stock(ticker, current_price=price, opening_price=price)
        return True

    async def set_stock_volatility(self, ticker: str, volatility: str) -> bool:
        if volatility not in VOLATILITY_CONFIGS:
            return False
        await self.stock_repo.update_stock(ticker, volatility=volatility)
        return True

    async def get_stock(self, ticker: str) -> Optional[StockModel]:
        return await self.stock_repo.get_stock(ticker)

    async def get_all_stocks(self) -> list[StockModel]:
        return await self.stock_repo.get_all_stocks()

    async def get_top_gainers(self, limit: int = 10) -> list[StockModel]:
        return await self.stock_repo.get_top_gainers(limit)

    async def get_top_losers(self, limit: int = 10) -> list[StockModel]:
        return await self.stock_repo.get_top_losers(limit)

    async def search_stocks(self, query: str, limit: int = 20) -> list[StockModel]:
        return await self.stock_repo.search_stocks(query, limit)

    async def get_portfolio_stats(self, user_id: int) -> dict:
        portfolio = await self.get_portfolio(user_id)
        total_invested = sum(h["avg_buy"] * h["shares"] for h in portfolio)
        total_value = sum(h["value"] for h in portfolio)
        total_profit = sum(h["profit"] for h in portfolio)
        total_lt_profit = sum(h["lifetime_profit"] for h in portfolio)
        total_lt_loss = sum(h["lifetime_loss"] for h in portfolio)
        stocks_count = len([h for h in portfolio if h["shares"] > 0])
        return {
            "total_invested": total_invested, "total_value": total_value,
            "total_profit": total_profit, "stocks_count": stocks_count,
            "lifetime_profit": total_lt_profit, "lifetime_loss": total_lt_loss,
        }

    async def get_top_investors(self, limit: int = 10):
        return await self.portfolio_repo.get_top_investors(limit)

    async def get_highest_portfolio(self, limit: int = 10):
        return await self.portfolio_repo.get_highest_portfolio_value(limit)

    async def get_highest_profit(self, limit: int = 10):
        return await self.portfolio_repo.get_highest_profit(limit)

    async def get_highest_loss(self, limit: int = 10):
        return await self.portfolio_repo.get_highest_loss(limit)

    async def get_best_roi(self, limit: int = 10):
        return await self.portfolio_repo.get_best_roi(limit)

    async def get_most_active(self, limit: int = 10):
        return await self.portfolio_repo.get_most_stocks_owned(limit)

    async def get_stock_info(self, ticker: str) -> Optional[dict]:
        stock = await self.stock_repo.get_stock(ticker)
        if not stock:
            return None
        change = ((stock.current_price - stock.opening_price) / stock.opening_price * 100) if stock.opening_price > 0 else 0
        return {
            "ticker": stock.ticker, "name": stock.name, "sector": stock.sector,
            "price": stock.current_price, "open": stock.opening_price,
            "prev_close": stock.previous_close, "change_pct": change,
            "market_cap": stock.market_cap, "volume": stock.daily_volume,
            "high": stock.daily_high, "low": stock.daily_low,
            "volatility": stock.volatility, "popularity": stock.popularity,
            "available": stock.available_shares, "total": stock.total_shares,
        }

    async def reset_market(self) -> None:
        await self.stock_repo.reset_all_prices()

    def start_background_task(self, interval_minutes: int = 10) -> None:
        if self._running:
            return
        self._running = True
        self._task = asyncio.create_task(self._price_update_loop(interval_minutes))

    def stop_background_task(self) -> None:
        self._running = False
        if self._task:
            self._task.cancel()

    async def _price_update_loop(self, interval_minutes: int) -> None:
        while self._running:
            try:
                await asyncio.sleep(interval_minutes * 60)
                if not self._running:
                    break
                await self.update_prices()
                await self.check_stop_loss_take_profit()
                await self.trigger_random_event()
            except asyncio.CancelledError:
                break
            except Exception:
                await asyncio.sleep(60)
