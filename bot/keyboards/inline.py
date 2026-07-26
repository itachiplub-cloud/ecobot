from __future__ import annotations

from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from bot.core import loc


class InlineKeyboards:
    @staticmethod
    def main_menu(lang: str = "en") -> InlineKeyboardMarkup:
        return InlineKeyboardMarkup([
            [
                InlineKeyboardButton(loc.t("btn.profile", lang), callback_data="profile"),
                InlineKeyboardButton(loc.t("btn.help", lang), callback_data="help"),
            ],
            [
                InlineKeyboardButton(loc.t("btn.economy", lang), callback_data="economy"),
                InlineKeyboardButton(loc.t("btn.rpg", lang), callback_data="rpg_menu"),
            ],
            [
                InlineKeyboardButton(loc.t("btn.inventory", lang), callback_data="inventory"),
                InlineKeyboardButton(loc.t("btn.shop", lang), callback_data="shop"),
            ],
            [
                InlineKeyboardButton(loc.t("btn.games", lang), callback_data="games_menu"),
                InlineKeyboardButton(loc.t("btn.quests", lang), callback_data="quests"),
            ],
            [
                InlineKeyboardButton(loc.t("btn.pets", lang), callback_data="pets_menu"),
                InlineKeyboardButton(loc.t("btn.clans", lang), callback_data="clans_menu"),
            ],
            [
                InlineKeyboardButton(loc.t("btn.market", lang), callback_data="market_menu"),
                InlineKeyboardButton(loc.t("btn.leaderboard", lang), callback_data="leaderboard"),
            ],
            [
                InlineKeyboardButton(loc.t("btn.settings", lang), callback_data="settings"),
                InlineKeyboardButton(loc.t("btn.updates", lang), url="https://t.me/updates"),
            ],
        ])

    @staticmethod
    def back_button(callback_data: str = "main_menu", lang: str = "en") -> InlineKeyboardMarkup:
        return InlineKeyboardMarkup([
            [InlineKeyboardButton(loc.t("btn.back", lang), callback_data=callback_data)],
            [InlineKeyboardButton(loc.t("btn.close", lang), callback_data="close")],
        ])

    @staticmethod
    def close_button(lang: str = "en") -> InlineKeyboardMarkup:
        return InlineKeyboardMarkup([
            [InlineKeyboardButton(loc.t("btn.close", lang), callback_data="close")],
        ])

    @staticmethod
    def economy_menu(lang: str = "en") -> InlineKeyboardMarkup:
        return InlineKeyboardMarkup([
            [
                InlineKeyboardButton(loc.t("btn.balance", lang), callback_data="balance"),
                InlineKeyboardButton(loc.t("btn.deposit", lang), callback_data="deposit"),
            ],
            [
                InlineKeyboardButton(loc.t("btn.withdraw", lang), callback_data="withdraw"),
                InlineKeyboardButton(loc.t("btn.transfer", lang), callback_data="transfer"),
            ],
            [
                InlineKeyboardButton(loc.t("btn.bank_info", lang), callback_data="bank_info"),
                InlineKeyboardButton(loc.t("btn.loans", lang), callback_data="loans"),
            ],
            [
                InlineKeyboardButton(loc.t("btn.transactions", lang), callback_data="transactions"),
            ],
            [InlineKeyboardButton(loc.t("btn.back", lang), callback_data="main_menu")],
        ])

    @staticmethod
    def work_menu(lang: str = "en") -> InlineKeyboardMarkup:
        return InlineKeyboardMarkup([
            [InlineKeyboardButton(loc.t("btn.work", lang), callback_data="work")],
            [InlineKeyboardButton(loc.t("btn.job_list", lang), callback_data="jobs_list")],
            [InlineKeyboardButton(loc.t("btn.back", lang), callback_data="main_menu")],
        ])

    @staticmethod
    def crime_menu(lang: str = "en") -> InlineKeyboardMarkup:
        return InlineKeyboardMarkup([
            [InlineKeyboardButton(loc.t("btn.beg", lang), callback_data="beg")],
            [InlineKeyboardButton(loc.t("btn.steal", lang), callback_data="steal")],
            [InlineKeyboardButton(loc.t("btn.rob", lang), callback_data="rob")],
            [InlineKeyboardButton(loc.t("btn.heist", lang), callback_data="heist")],
            [InlineKeyboardButton(loc.t("btn.hack", lang), callback_data="hack")],
            [InlineKeyboardButton(loc.t("btn.back", lang), callback_data="main_menu")],
        ])

    @staticmethod
    def games_menu(lang: str = "en") -> InlineKeyboardMarkup:
        return InlineKeyboardMarkup([
            [
                InlineKeyboardButton(loc.t("btn.coinflip", lang), callback_data="coinflip"),
                InlineKeyboardButton(loc.t("btn.slots", lang), callback_data="slots"),
            ],
            [
                InlineKeyboardButton(loc.t("btn.blackjack", lang), callback_data="blackjack"),
                InlineKeyboardButton(loc.t("btn.roulette", lang), callback_data="roulette"),
            ],
            [
                InlineKeyboardButton(loc.t("btn.dice", lang), callback_data="dice_game"),
                InlineKeyboardButton(loc.t("btn.wheel", lang), callback_data="wheel"),
            ],
            [
                InlineKeyboardButton(loc.t("btn.mines", lang), callback_data="mines"),
                InlineKeyboardButton(loc.t("btn.crash", lang), callback_data="crash"),
            ],
            [InlineKeyboardButton(loc.t("btn.back", lang), callback_data="main_menu")],
        ])

    @staticmethod
    def rpg_menu(lang: str = "en") -> InlineKeyboardMarkup:
        return InlineKeyboardMarkup([
            [
                InlineKeyboardButton(loc.t("btn.stats", lang), callback_data="rpg_stats"),
                InlineKeyboardButton(loc.t("btn.equipment", lang), callback_data="equipment"),
            ],
            [
                InlineKeyboardButton(loc.t("btn.dungeon", lang), callback_data="dungeon"),
                InlineKeyboardButton(loc.t("btn.boss", lang), callback_data="boss"),
            ],
            [
                InlineKeyboardButton(loc.t("btn.pvp", lang), callback_data="pvp"),
                InlineKeyboardButton(loc.t("btn.fish", lang), callback_data="fish"),
            ],
            [InlineKeyboardButton(loc.t("btn.mine", lang), callback_data="mine")],
            [InlineKeyboardButton(loc.t("btn.back", lang), callback_data="main_menu")],
        ])

    @staticmethod
    def profile_menu(lang: str = "en") -> InlineKeyboardMarkup:
        return InlineKeyboardMarkup([
            [
                InlineKeyboardButton(loc.t("btn.inventory", lang), callback_data="inventory"),
                InlineKeyboardButton(loc.t("btn.achievements", lang), callback_data="achievements"),
            ],
            [
                InlineKeyboardButton(loc.t("btn.pets", lang), callback_data="pets_menu"),
                InlineKeyboardButton(loc.t("btn.battlepass", lang), callback_data="battlepass"),
            ],
            [InlineKeyboardButton(loc.t("btn.back", lang), callback_data="main_menu")],
        ])

    @staticmethod
    def shop_menu(lang: str = "en") -> InlineKeyboardMarkup:
        return InlineKeyboardMarkup([
            [InlineKeyboardButton(loc.t("btn.shop_permanent", lang), callback_data="shop_permanent")],
            [InlineKeyboardButton(loc.t("btn.shop_daily", lang), callback_data="shop_daily")],
            [InlineKeyboardButton(loc.t("btn.shop_weekly", lang), callback_data="shop_weekly")],
            [InlineKeyboardButton(loc.t("btn.shop_premium", lang), callback_data="shop_premium")],
            [InlineKeyboardButton(loc.t("btn.back", lang), callback_data="main_menu")],
        ])

    @staticmethod
    def clan_menu(lang: str = "en") -> InlineKeyboardMarkup:
        return InlineKeyboardMarkup([
            [InlineKeyboardButton(loc.t("btn.clan_create", lang), callback_data="clan_create")],
            [InlineKeyboardButton(loc.t("btn.clan_info", lang), callback_data="clan_info")],
            [InlineKeyboardButton(loc.t("btn.clan_members", lang), callback_data="clan_members")],
            [InlineKeyboardButton(loc.t("btn.clan_war", lang), callback_data="clan_war")],
            [InlineKeyboardButton(loc.t("btn.clan_shop", lang), callback_data="clan_shop")],
            [InlineKeyboardButton(loc.t("btn.back", lang), callback_data="main_menu")],
        ])

    @staticmethod
    def market_menu(lang: str = "en") -> InlineKeyboardMarkup:
        return InlineKeyboardMarkup([
            [InlineKeyboardButton(loc.t("btn.market_browse", lang), callback_data="market_browse")],
            [InlineKeyboardButton(loc.t("btn.market_sell", lang), callback_data="market_sell")],
            [InlineKeyboardButton(loc.t("btn.market_auctions", lang), callback_data="market_auctions")],
            [InlineKeyboardButton(loc.t("btn.market_my_listings", lang), callback_data="market_my_listings")],
            [InlineKeyboardButton(loc.t("btn.back", lang), callback_data="main_menu")],
        ])

    @staticmethod
    def pets_menu(lang: str = "en") -> InlineKeyboardMarkup:
        return InlineKeyboardMarkup([
            [InlineKeyboardButton(loc.t("btn.pet_list", lang), callback_data="pet_list")],
            [InlineKeyboardButton(loc.t("btn.pet_equip", lang), callback_data="pet_equip")],
            [InlineKeyboardButton(loc.t("btn.pet_feed", lang), callback_data="pet_feed")],
            [InlineKeyboardButton(loc.t("btn.pet_play", lang), callback_data="pet_play")],
            [InlineKeyboardButton(loc.t("btn.pet_evolve", lang), callback_data="pet_evolve")],
            [InlineKeyboardButton(loc.t("btn.back", lang), callback_data="main_menu")],
        ])

    @staticmethod
    def settings_menu(lang: str = "en") -> InlineKeyboardMarkup:
        return InlineKeyboardMarkup([
            [InlineKeyboardButton(loc.t("btn.language", lang), callback_data="language")],
            [InlineKeyboardButton(loc.t("btn.notifications", lang), callback_data="toggle_notifications")],
            [InlineKeyboardButton(loc.t("btn.private_profile", lang), callback_data="toggle_private")],
            [InlineKeyboardButton(loc.t("btn.back", lang), callback_data="main_menu")],
        ])

    @staticmethod
    def admin_panel(lang: str = "en") -> InlineKeyboardMarkup:
        return InlineKeyboardMarkup([
            [
                InlineKeyboardButton(loc.t("btn.admin_broadcast", lang), callback_data="admin_broadcast"),
                InlineKeyboardButton(loc.t("btn.admin_economy", lang), callback_data="admin_economy"),
            ],
            [
                InlineKeyboardButton(loc.t("btn.admin_users", lang), callback_data="admin_users"),
                InlineKeyboardButton(loc.t("btn.admin_premium", lang), callback_data="admin_premium"),
            ],
            [
                InlineKeyboardButton(loc.t("btn.admin_settings", lang), callback_data="admin_settings"),
                InlineKeyboardButton(loc.t("btn.admin_logs", lang), callback_data="admin_logs"),
            ],
            [InlineKeyboardButton(loc.t("btn.back", lang), callback_data="main_menu")],
        ])

    @staticmethod
    def confirm_action(action: str, lang: str = "en") -> InlineKeyboardMarkup:
        return InlineKeyboardMarkup([
            [
                InlineKeyboardButton(loc.t("btn.confirm_yes", lang), callback_data=f"confirm_{action}"),
                InlineKeyboardButton(loc.t("btn.confirm_no", lang), callback_data="main_menu"),
            ],
        ])

    @staticmethod
    def pagination(page: int, total: int, prefix: str, lang: str = "en") -> InlineKeyboardMarkup:
        buttons = []
        if page > 1:
            buttons.append(InlineKeyboardButton(loc.t("btn.prev", lang), callback_data=f"{prefix}_page_{page - 1}"))
        buttons.append(InlineKeyboardButton(f"{page}/{total}", callback_data="noop"))
        if page < total:
            buttons.append(InlineKeyboardButton(loc.t("btn.next", lang), callback_data=f"{prefix}_page_{page + 1}"))
        return InlineKeyboardMarkup([buttons])

    @staticmethod
    def game_pass_keyboard(tier: int, is_premium: bool) -> InlineKeyboardMarkup:
        buttons = []
        for t in range(1, min(tier + 3, 11)):
            buttons.append([
                InlineKeyboardButton(
                    f"🎁 Claim Tier {t}",
                    callback_data=f"gamepass_claim_{t}",
                )
            ])
        if not is_premium:
            buttons.append([
                InlineKeyboardButton("👑 Upgrade to Premium", callback_data="gamepass_premium"),
            ])
        buttons.append([InlineKeyboardButton("◀️ Back", callback_data="main_menu")])
        return InlineKeyboardMarkup(buttons)

    @staticmethod
    def bank_leaderboard(lang: str = "en") -> InlineKeyboardMarkup:
        return InlineKeyboardMarkup([
            [
                InlineKeyboardButton("💰 Richest", callback_data="lb_bank_richest"),
                InlineKeyboardButton("🏦 Top Savers", callback_data="lb_bank_savers"),
            ],
            [
                InlineKeyboardButton("📄 Most Loans", callback_data="lb_bank_loans"),
                InlineKeyboardButton("📈 Investments", callback_data="lb_bank_investments"),
            ],
            [InlineKeyboardButton(loc.t("btn.back", lang), callback_data="main_menu")],
        ])

    @staticmethod
    def owner_panel(lang: str = "en") -> InlineKeyboardMarkup:
        return InlineKeyboardMarkup([
            [
                InlineKeyboardButton("👥 Users", callback_data="op_users"),
                InlineKeyboardButton("💰 Economy", callback_data="op_economy"),
            ],
            [
                InlineKeyboardButton("🏦 Bank", callback_data="op_bank"),
                InlineKeyboardButton("🎮 Games", callback_data="op_games"),
            ],
            [
                InlineKeyboardButton("🏆 Leaderboards", callback_data="op_leaderboards"),
                InlineKeyboardButton("📊 Stats", callback_data="op_stats"),
            ],
            [
                InlineKeyboardButton("📂 Database", callback_data="op_database"),
                InlineKeyboardButton("🤖 Sudo", callback_data="op_sudo"),
            ],
            [
                InlineKeyboardButton("🎉 Events", callback_data="op_events"),
                InlineKeyboardButton("📢 Broadcast", callback_data="op_broadcast"),
            ],
            [
                InlineKeyboardButton("⚙️ Settings", callback_data="op_settings"),
                InlineKeyboardButton("📜 Logs", callback_data="op_logs"),
            ],
            [InlineKeyboardButton(loc.t("btn.close", lang), callback_data="close")],
        ])
