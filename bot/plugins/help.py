from __future__ import annotations

from pyrogram import Client, filters
from pyrogram.types import CallbackQuery, Message, InlineKeyboardButton, InlineKeyboardMarkup

from bot.core import loc
from bot.keyboards.inline import InlineKeyboards

HELP_PAGES = [
    {
        "title": "💰 Economy Commands",
        "text": (
            "💰 **Economy Commands**\n\n"
            "/balance — Check your balance\n"
            "/deposit <amount> — Deposit coins to bank\n"
            "/withdraw <amount> — Withdraw from bank\n"
            "/transfer @user <amount> — Send coins to someone\n"
            "/daily — Claim daily reward\n"
            "/daily claim — Collect daily bonus\n"
            "/weekly — Claim weekly reward\n"
            "/monthly — Claim monthly reward\n"
            "/yearly — Claim yearly reward\n"
        ),
    },
    {
        "title": "💼 Work & Crime",
        "text": (
            "💼 **Work Commands**\n\n"
            "/work — Work at your job\n"
            "/work list — View available jobs\n\n"
            "🚨 **Crime Commands**\n\n"
            "/crime — Crime menu\n"
            "/beg — Beg for coins\n"
            "/steal @user — Steal from someone\n"
            "/rob @user — Rob a player\n"
            "/heist — Rob a bank\n"
            "/hack @user — Hack a player\n"
        ),
    },
    {
        "title": "🎮 Casino Games",
        "text": (
            "🎮 **Casino Games**\n\n"
            "/coinflip heads|tails <amount> — Coin flip\n"
            "/slots <amount> — Slot machine\n"
            "/blackjack <amount> — Play blackjack\n"
            "/roulette red|black|green <amount> — Roulette\n"
            "/dice <amount> — Dice roll game\n"
            "/crash <amount> — Cash out before crash\n"
            "/mines <amount> — Minesweeper\n"
        ),
    },
    {
        "title": "🎯 Telegram Games",
        "text": (
            "🎯 **Animated Emoji Games**\n\n"
            "/dart <amount> — Dart throwing\n"
            "/bowling <amount> — Bowling\n"
            "/basketball <amount> — Basketball\n"
            "/football <amount> — Football\n"
            "/diceroll <amount> — Dice roll\n\n"
            "**Betting Games:**\n"
            "/betroll <number> <amount> — Bet on dice\n"
            "/highlow <amount> — High or low\n"
            "/wheel <amount> — Wheel of fortune\n"
            "/treasure <amount> — Treasure hunt\n"
            "/luckycard <amount> — Lucky card\n"
            "/numberguess <guess> <amount> — Guess the number\n"
        ),
    },
    {
        "title": "⚔️ RPG Combat",
        "text": (
            "⚔️ **RPG Commands**\n\n"
            "/stats — View your character stats\n"
            "/equip <item> — Equip an item\n"
            "/unequip <slot> — Unequip item\n\n"
            "**Dungeons:**\n"
            "/dungeon — Enter a dungeon\n"
            "/dungeon list — View dungeons\n\n"
            "**Boss Fights:**\n"
            "/boss — Fight a boss\n"
            "/boss list — View bosses\n\n"
            "**PvP:**\n"
            "/pvp @user — Challenge a player\n"
        ),
    },
    {
        "title": "🐟 Gathering",
        "text": (
            "🐟 **Fishing**\n\n"
            "/fish — Go fishing\n"
            "/fish inventory — View caught fish\n\n"
            "⛏️ **Mining**\n\n"
            "/mine — Go mining\n"
            "/mine inventory — View mined ores\n"
        ),
    },
    {
        "title": "📋 Quests",
        "text": (
            "📋 **Quest Commands**\n\n"
            "/quests — View active quests\n"
            "/dailyquests — View daily quests\n"
            "/weeklyquests — View weekly quests\n"
            "/monthlyquests — View monthly quests\n"
            "/claimquest <id> — Claim quest reward\n"
        ),
    },
    {
        "title": "🐾 Pets",
        "text": (
            "🐾 **Pet Commands**\n\n"
            "/pets — View your pets\n"
            "/feedpet <name> — Feed your pet\n"
            "/playpet <name> — Play with pet\n"
            "/evolvepet <name> — Evolve your pet\n"
            "/equippet <name> — Equip a pet\n"
        ),
    },
    {
        "title": "🏰 Clans",
        "text": (
            "🏰 **Clan Commands**\n\n"
            "/clan create <name> — Create a clan\n"
            "/clan join <name> — Join a clan\n"
            "/clan leave — Leave your clan\n"
            "/clan info — View clan info\n"
            "/clan members — View members\n"
            "/clan deposit <amount> — Deposit to treasury\n"
            "/clan disband — Disband your clan\n"
        ),
    },
    {
        "title": "📊 Market",
        "text": (
            "📊 **Market Commands**\n\n"
            "/market — Open player market\n"
            "/market sell <item> <price> — List an item\n"
            "/market buy <id> — Buy a listing\n"
            "/auction create <item> <bid> — Create auction\n"
            "/auction bid <id> <amount> — Place bid\n"
            "/mylistings — View your listings\n"
        ),
    },
    {
        "title": "🏦 Banking",
        "text": (
            "🏦 **Bank Commands**\n\n"
            "/bankinfo — Bank information\n"
            "/bank balance — Your bank balance\n"
            "/loan take <amount> — Take a loan\n"
            "/loan repay <amount> — Repay loan\n"
            "/invest <type> <amount> — Invest\n"
            "  Types: savings / fixed / growth / premium\n"
            "/myinvestments — View investments\n"
            "/withdrawinvestment <id> — Withdraw investment\n"
            "/transactions — Transaction history\n"
        ),
    },
    {
        "title": "📈 Stocks",
        "text": (
            "📈 **Stock Market Commands**\n\n"
            "/stocks — Open stock market\n"
            "/buy <ticker> <shares> — Buy shares\n"
            "/sell <ticker> <shares> — Sell shares\n"
            "/portfolio — Your portfolio\n"
            "/watchlist — Your watchlist\n"
            "/market — View all stocks\n"
            "/stockhistory <ticker> — Price history\n"
            "/stoploss <ticker> <percent> — Set stop loss\n"
            "/takeprofit <ticker> <percent> — Set take profit\n"
            "/topgainers — Today's top gainers\n"
            "/toplosers — Today's top losers\n"
            "/stocksearch <query> — Search stocks\n"
        ),
    },
    {
        "title": "👥 Social & Profile",
        "text": (
            "👥 **Social Commands**\n\n"
            "/profile — View your profile\n"
            "/profile @user — View other's profile\n"
            "/achievements — View achievements\n"
            "/battlepass — View battle pass\n"
            "/gamepass — View game pass\n"
            "/mail — Check your mail\n"
            "/leaderboard — View leaderboards\n"
            "/grouplb — Group rankings (in group)\n"
        ),
    },
    {
        "title": "⚙️ Settings & Misc",
        "text": (
            "⚙️ **Settings**\n\n"
            "/settings — Bot settings\n"
            "/help — This help menu\n"
            "/start — Start the bot\n\n"
            "📋 **Misc**\n\n"
            "/gamestats — Your game statistics\n"
            "/gametop — Game leaderboards\n"
            "/banklb — Bank leaderboard\n"
        ),
    },
    {
        "title": "👑 Admin Commands",
        "text": (
            "👑 **Admin / Owner Commands**\n\n"
            "/owner — Owner control panel\n"
            "/admin — Admin panel\n"
            "/ban <user> — Ban a user\n"
            "/unban <user> — Unban a user\n"
            "/broadcast <msg> — Broadcast message\n"
            "/addcoins <user> <amount> — Give coins\n"
            "/removecoins <user> <amount> — Remove coins\n"
            "/setcoins <user> <amount> — Set balance\n"
            "/resetuser <id> — Reset user\n"
            "/deleteuser <id> — Soft delete\n"
            "/recoveruser <id> — Recover deleted\n"
            "/gameon <type> — Enable game\n"
            "/gameoff <type> — Disable game\n"
            "/setcooldown <type> <sec> — Set cooldown\n"
            "/setdifficulty <type> <level> — Set difficulty\n"
            "/setinterest <rate> — Set bank interest\n"
            "/maintenance on|off — Maintenance mode\n"
            "/dbstatus — Database status\n"
        ),
    },
]


def register(app: Client):

    @app.on_message(filters.command("help"))
    async def help_command(client: Client, message: Message):
        page = 0
        text, kb = _build_page(page)
        await message.reply_text(text, reply_markup=kb)

    @app.on_callback_query(filters.regex("^help$"))
    async def help_callback(client: Client, cb: CallbackQuery):
        text, kb = _build_page(0)
        try:
            await cb.message.edit_text(text, reply_markup=kb)
        except Exception:
            await cb.message.reply_text(text, reply_markup=kb)
        await cb.answer()

    @app.on_callback_query(filters.regex(r"^help_page_(\d+)$"))
    async def help_page_callback(client: Client, cb: CallbackQuery):
        page = int(cb.data.split("_")[-1])
        text, kb = _build_page(page)
        try:
            await cb.message.edit_text(text, reply_markup=kb)
        except Exception:
            pass
        await cb.answer()

    @app.on_callback_query(filters.regex("^help_close$"))
    async def help_close_callback(client: Client, cb: CallbackQuery):
        try:
            await cb.message.delete()
        except Exception:
            pass
        await cb.answer()


def _build_page(page: int) -> tuple[str, InlineKeyboardMarkup]:
    total = len(HELP_PAGES)
    page = max(0, min(page, total - 1))
    p = HELP_PAGES[page]

    header = f"page {page + 1}/{total}\n\n"
    text = header + p["text"]

    buttons = []
    nav = []
    if page > 0:
        nav.append(InlineKeyboardButton("◀️ Prev", callback_data=f"help_page_{page - 1}"))
    nav.append(InlineKeyboardButton(f"{page + 1}/{total}", callback_data="noop"))
    if page < total - 1:
        nav.append(InlineKeyboardButton("Next ▶️", callback_data=f"help_page_{page + 1}"))
    buttons.append(nav)

    cat_row = []
    half = total // 2
    start = max(0, page - 2)
    end = min(total, page + 3)
    for i in range(start, end):
        label = HELP_PAGES[i]["title"].split(" ", 1)[-1][:12]
        prefix = "👉 " if i == page else ""
        cat_row.append(InlineKeyboardButton(f"{prefix}{label}", callback_data=f"help_page_{i}"))
        if len(cat_row) == 3:
            buttons.append(cat_row)
            cat_row = []
    if cat_row:
        buttons.append(cat_row)

    buttons.append([
        InlineKeyboardButton("🏠 Menu", callback_data="main_menu"),
        InlineKeyboardButton("✖️ Close", callback_data="help_close"),
    ])

    return text, InlineKeyboardMarkup(buttons)
