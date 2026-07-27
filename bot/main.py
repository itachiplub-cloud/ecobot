from __future__ import annotations

import asyncio
import sys
import platform
from pathlib import Path

if platform.system() != "Windows":
    try:
        import uvloop
        asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
    except ImportError:
        pass

from loguru import logger
from pyrogram import Client, idle

from config import settings
from bot import set_app
from bot.database import connect_db, disconnect_db
from bot.database.indexes import create_indexes


def setup_logging():
    logger.remove()
    logger.add(sys.stderr, level=settings.LOG_LEVEL, format="<green>{time:HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>")
    Path("logs").mkdir(exist_ok=True)
    logger.add(settings.LOG_FILE, level="DEBUG", rotation="10 MB", retention="7 days")


async def main():
    setup_logging()
    logger.info("Starting Telegram Economy RPG Bot...")

    db = await connect_db(settings.MONGO_URI, settings.MONGO_DB_NAME)
    logger.info("Connected to MongoDB")

    await create_indexes(db)
    logger.info("Database indexes created")

    from bot.services.game_service import GameService
    game_svc = GameService(db)
    await game_svc.seed_configs()
    logger.info("Game configs seeded")

    from bot.services.stock_market_service import StockMarketService
    stock_svc = StockMarketService(db)
    from bot.plugins.stocks.seed_companies import seed_stocks
    seeded = await seed_stocks(stock_svc)
    logger.info(f"Stock market seeded: {seeded} new companies")

    app = Client(
        "economy_rpg_bot",
        api_id=settings.API_ID,
        api_hash=settings.API_HASH,
        bot_token=settings.BOT_TOKEN,
    )
    set_app(app)

    from bot.middlewares.database_middleware import DatabaseMiddleware
    from bot.middlewares.stats_middleware import StatisticsMiddleware

    db_middleware = DatabaseMiddleware()
    stats_middleware = StatisticsMiddleware()

    app.add_handler(db_middleware, group=-1)
    app.add_handler(stats_middleware, group=-2)

    from bot.plugins import register_core
    from bot.plugins.economy import register as reg_economy
    from bot.plugins.work import register as reg_work
    from bot.plugins.crime import register as reg_crime
    from bot.plugins.games import register as reg_games
    from bot.plugins.rpg import register as reg_rpg
    from bot.plugins.quests import register as reg_quests
    from bot.plugins.pets import register as reg_pets
    from bot.plugins.shop import register as reg_shop
    from bot.plugins.market import register as reg_market
    from bot.plugins.clans import register as reg_clans
    from bot.plugins.leaderboard import register as reg_leaderboard
    from bot.plugins.admin import register as reg_admin
    from bot.plugins.achievements import register as reg_achievements
    from bot.plugins.mail import register as reg_mail
    from bot.plugins.battlepass import register as reg_battlepass
    from bot.plugins.events import register as reg_events
    from bot.plugins.banking import register as reg_banking
    from bot.plugins.daily import register as reg_daily
    from bot.plugins.stocks import register as reg_stocks

    register_core(app)
    reg_economy(app)
    reg_work(app)
    reg_crime(app)
    reg_games(app)
    reg_rpg(app)
    reg_quests(app)
    reg_pets(app)
    reg_shop(app)
    reg_market(app)
    reg_clans(app)
    reg_leaderboard(app)
    reg_admin(app)
    reg_achievements(app)
    reg_mail(app)
    reg_battlepass(app)
    reg_events(app)
    reg_banking(app)
    reg_daily(app)
    reg_stocks(app)

    logger.info("All plugins registered")

    await app.start()
    logger.info("Bot started successfully")

    me = await app.get_me()
    logger.info(f"Logged in as {me.first_name} (@{me.username})")

    from bot.services.statistics_service import StatisticsService
    stats_svc = StatisticsService(db)
    await stats_svc.increment("commands_executed", 0)

    stock_svc.start_background_task(interval_minutes=10)
    logger.info("Stock market price updater started (10 min interval)")

    logger.info("Bot is running. Press Ctrl+C to stop.")
    await idle()

    logger.info("Stopping bot...")
    stock_svc.stop_background_task()
    await app.stop()
    await disconnect_db()
    logger.info("Bot stopped.")


if __name__ == "__main__":
    asyncio.run(main())
