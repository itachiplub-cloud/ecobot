from __future__ import annotations

from pyrogram import Client
from pyrogram.types import Message, CallbackQuery

from bot.database import get_db
from bot.services import (
    EconomyService, UserService, InventoryService, ShopService,
    PetService, GuildService, QuestService, DailyService,
    BattlePassService, BankService, MarketService, EventService,
    CooldownService, AchievementService, MailService,
    LeaderboardService, AdminService, PremiumService,
    LogService, StatisticsService, GameService, OwnerService,
    EnhancedBankService, GroupRankingService, StockMarketService,
)


class DatabaseMiddleware:
    def __init__(self):
        self._services: dict | None = None

    def _init_services(self):
        if self._services is None:
            db = get_db()
            self._services = {
                "economy": EconomyService(db),
                "user": UserService(db),
                "inventory": InventoryService(db),
                "shop": ShopService(db),
                "pet": PetService(db),
                "guild": GuildService(db),
                "quest": QuestService(db),
                "daily": DailyService(db),
                "battle_pass": BattlePassService(db),
                "bank": BankService(db),
                "market": MarketService(db),
                "event": EventService(db),
                "cooldown": CooldownService(db),
                "achievement": AchievementService(db),
                "mail": MailService(db),
                "leaderboard": LeaderboardService(db),
                "admin": AdminService(db),
                "premium": PremiumService(db),
                "log": LogService(db),
                "statistics": StatisticsService(db),
                "game": GameService(db),
                "owner": OwnerService(db),
                "enhanced_bank": EnhancedBankService(db),
                "group_ranking": GroupRankingService(db),
                "stock_market": StockMarketService(db),
            }
        return self._services

    async def __call__(self, client: Client, update):
        services = self._init_services()
        if isinstance(update, Message):
            update._services = services
        elif isinstance(update, CallbackQuery):
            if update.message:
                update.message._services = services
            update._services = services
        return
