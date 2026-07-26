from motor.motor_asyncio import AsyncIOMotorDatabase
from loguru import logger


async def create_indexes(db: AsyncIOMotorDatabase) -> None:
    """Create all MongoDB indexes on startup."""

    await db.users.create_index("user_id", unique=True)
    await db.users.create_index("username")
    await db.users.create_index("level")
    await db.users.create_index("xp")
    await db.users.create_index("joined_at")

    await db.economy.create_index("user_id", unique=True)
    await db.economy.create_index("wallet")
    await db.economy.create_index("bank")

    await db.inventory.create_index("user_id")
    await db.inventory.create_index([("user_id", 1), ("item_id", 1)])
    await db.inventory.create_index("item_id")

    await db.items.create_index("item_id", unique=True)
    await db.items.create_index("category")
    await db.items.create_index("rarity")

    await db.shop.create_index("item_id")
    await db.shop.create_index("shop_type")
    await db.shop.create_index("expires_at")

    await db.pets.create_index("user_id")
    await db.pets.create_index([("user_id", 1), ("pet_id", 1)])
    await db.pets.create_index("pet_type")

    await db.guilds.create_index("guild_id", unique=True)
    await db.guilds.create_index("name")
    await db.guilds.create_index("level")

    await db.guild_members.create_index("guild_id")
    await db.guild_members.create_index("user_id", unique=True)
    await db.guild_members.create_index([("guild_id", 1), ("role", 1)])

    await db.quests.create_index("user_id")
    await db.quests.create_index([("user_id", 1), ("quest_type", 1)])
    await db.quests.create_index("expires_at")

    await db.daily_rewards.create_index("user_id", unique=True)

    await db.battle_pass.create_index("user_id", unique=True)
    await db.battle_pass.create_index("season")

    await db.transactions.create_index("user_id")
    await db.transactions.create_index("created_at")
    await db.transactions.create_index([("user_id", 1), ("created_at", -1)])

    await db.banks.create_index("user_id", unique=True)

    await db.market.create_index("seller_id")
    await db.market.create_index("item_id")
    await db.market.create_index("price")
    await db.market.create_index("expires_at")
    await db.market.create_index([("item_id", 1), ("price", 1)])

    await db.auction.create_index("seller_id")
    await db.auction.create_index("item_id")
    await db.auction.create_index("current_bid")
    await db.auction.create_index("expires_at")

    await db.events.create_index("event_id", unique=True)
    await db.events.create_index("event_type")
    await db.events.create_index([("start_at", 1), ("end_at", 1)])

    await db.cooldowns.create_index([("user_id", 1), ("action", 1)], unique=True)
    await db.cooldowns.create_index("expires_at", expireAfterSeconds=0)

    await db.achievements.create_index("user_id")
    await db.achievements.create_index([("user_id", 1), ("achievement_id", 1)], unique=True)

    await db.mail.create_index("recipient_id")
    await db.mail.create_index([("recipient_id", 1), ("read", 1)])
    await db.mail.create_index("created_at", expireAfterSeconds=2592000)

    await db.leaderboards.create_index([("category", 1), ("score", -1)])
    await db.leaderboards.create_index("user_id")

    await db.admins.create_index("user_id", unique=True)

    await db.settings.create_index("key", unique=True)

    await db.premium.create_index("user_id", unique=True)
    await db.premium.create_index("expires_at")

    await db.logs.create_index("created_at", expireAfterSeconds=2592000)
    await db.logs.create_index("level")
    await db.logs.create_index("user_id")

    await db.statistics.create_index("stat_date")

    await db.group_rankings.create_index([("group_id", 1), ("user_id", 1)], unique=True)
    await db.group_rankings.create_index("group_id")
    await db.group_rankings.create_index("user_id")
    await db.group_rankings.create_index([("group_id", 1), ("xp_earned", -1)])
    await db.group_rankings.create_index([("group_id", 1), ("coins_earned", -1)])
    await db.group_rankings.create_index([("group_id", 1), ("messages_sent", -1)])

    await db.game_stats.create_index("user_id", unique=True)
    await db.game_stats.create_index("current_win_streak")
    await db.game_stats.create_index("best_win_streak")

    await db.game_history.create_index("user_id")
    await db.game_history.create_index([("user_id", 1), ("created_at", -1)])
    await db.game_history.create_index("game_type")

    await db.game_config.create_index("game_type", unique=True)

    await db.deleted_users.create_index("user_id", unique=True)
    await db.deleted_users.create_index("deleted_at")

    await db.audit_logs.create_index([("created_at", -1)])
    await db.audit_logs.create_index("admin_id")
    await db.audit_logs.create_index("action")

    await db.investments.create_index("user_id")
    await db.investments.create_index([("user_id", 1), ("status", 1)])
    await db.investments.create_index("investment_id")

    await db.game_pass.create_index("user_id", unique=True)

    await db.stocks.create_index("ticker", unique=True)
    await db.stocks.create_index("sector")
    await db.stocks.create_index("current_price")
    await db.stocks.create_index("is_active")

    await db.stock_portfolios.create_index([("user_id", 1), ("ticker", 1)])
    await db.stock_portfolios.create_index("user_id")
    await db.stock_portfolios.create_index("shares")

    await db.stock_transactions.create_index("user_id")
    await db.stock_transactions.create_index([("user_id", 1), ("created_at", -1)])
    await db.stock_transactions.create_index("ticker")

    await db.stock_market_events.create_index("event_id", unique=True)
    await db.stock_market_events.create_index("active")
    await db.stock_market_events.create_index("ticker")

    await db.stock_watchlists.create_index("user_id", unique=True)

    await db.stock_price_history.create_index([("ticker", 1), ("recorded_at", -1)])
    await db.stock_price_history.create_index("ticker")

    logger.info("All database indexes created successfully")
