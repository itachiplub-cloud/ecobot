from bot.database.repositories.user_repo import UserRepository
from bot.database.repositories.economy_repo import EconomyRepository
from bot.database.repositories.inventory_repo import InventoryRepository
from bot.database.repositories.item_repo import ItemRepository
from bot.database.repositories.shop_repo import ShopRepository
from bot.database.repositories.pet_repo import PetRepository
from bot.database.repositories.guild_repo import GuildRepository
from bot.database.repositories.quest_repo import QuestRepository
from bot.database.repositories.daily_repo import DailyRepository
from bot.database.repositories.battle_pass_repo import BattlePassRepository
from bot.database.repositories.transaction_repo import TransactionRepository
from bot.database.repositories.bank_repo import BankRepository
from bot.database.repositories.market_repo import MarketRepository
from bot.database.repositories.event_repo import EventRepository
from bot.database.repositories.cooldown_repo import CooldownRepository
from bot.database.repositories.achievement_repo import AchievementRepository
from bot.database.repositories.mail_repo import MailRepository
from bot.database.repositories.leaderboard_repo import LeaderboardRepository
from bot.database.repositories.admin_repo import AdminRepository
from bot.database.repositories.settings_repo import SettingsRepository
from bot.database.repositories.premium_repo import PremiumRepository
from bot.database.repositories.log_repo import LogRepository
from bot.database.repositories.statistics_repo import StatisticsRepository
from bot.database.repositories.stock_repo import StockRepository
from bot.database.repositories.stock_portfolio_repo import StockPortfolioRepository
from bot.database.repositories.stock_transaction_repo import StockTransactionRepository
from bot.database.repositories.stock_event_repo import StockMarketEventRepository
from bot.database.repositories.stock_watchlist_repo import StockWatchlistRepository
from bot.database.repositories.stock_price_history_repo import StockPriceHistoryRepository
from bot.database.repositories.group_ranking_repo import GroupRankingRepository
from bot.database.repositories.investment_repo import InvestmentRepository
from bot.database.repositories.audit_log_repo import AuditLogRepository
from bot.database.repositories.soft_delete_repo import SoftDeleteRepository
from bot.database.repositories.game_config_repo import GameConfigRepository
from bot.database.repositories.game_stats_repo import GameStatsRepository
from bot.database.repositories.game_history_repo import GameHistoryRepository
from bot.database.repositories.game_pass_repo import GamePassRepository

__all__ = [
    "UserRepository",
    "EconomyRepository",
    "InventoryRepository",
    "ItemRepository",
    "ShopRepository",
    "PetRepository",
    "GuildRepository",
    "QuestRepository",
    "DailyRepository",
    "BattlePassRepository",
    "TransactionRepository",
    "BankRepository",
    "MarketRepository",
    "EventRepository",
    "CooldownRepository",
    "AchievementRepository",
    "MailRepository",
    "LeaderboardRepository",
    "AdminRepository",
    "SettingsRepository",
    "PremiumRepository",
    "LogRepository",
    "StatisticsRepository",
    "StockRepository",
    "StockPortfolioRepository",
    "StockTransactionRepository",
    "StockMarketEventRepository",
    "StockWatchlistRepository",
    "StockPriceHistoryRepository",
    "GroupRankingRepository",
    "InvestmentRepository",
    "AuditLogRepository",
    "SoftDeleteRepository",
    "GameConfigRepository",
    "GameStatsRepository",
    "GameHistoryRepository",
    "GamePassRepository",
]
