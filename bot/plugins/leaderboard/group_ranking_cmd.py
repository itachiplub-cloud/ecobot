from __future__ import annotations

from pyrogram import Client, filters
from pyrogram.types import CallbackQuery, Message, InlineKeyboardButton, InlineKeyboardMarkup

from bot.core import loc
from bot.keyboards.inline import InlineKeyboards
from bot.utils.helpers import format_number


def register(app: Client):

    @app.on_message(filters.command("grouplb") & filters.group)
    async def group_leaderboard_command(client: Client, message: Message):
        services = getattr(message, '_services', None)
        if not services:
            return
        gr_svc = services.get("group_ranking")
        if not gr_svc:
            return
        group_id = message.chat.id
        text = f"🏆 **Group Leaderboard** — {message.chat.title}\n\nSelect ranking type:\n"
        kb = InlineKeyboardMarkup([
            [InlineKeyboardButton("⭐ XP", callback_data=f"glb_xp_{group_id}"),
             InlineKeyboardButton("💰 Coins", callback_data=f"glb_coins_{group_id}")],
            [InlineKeyboardButton("💬 Messages", callback_data=f"glb_msgs_{group_id}"),
             InlineKeyboardButton("🎮 Games", callback_data=f"glb_games_{group_id}")],
            [InlineKeyboardButton("👤 My Rank", callback_data=f"glb_myrank_{group_id}")],
        ])
        await message.reply_text(text, reply_markup=kb)

    @app.on_message(filters.command("grouplb") & filters.private)
    async def group_leaderboard_global(client: Client, message: Message):
        services = getattr(message, '_services', None)
        if not services:
            return
        gr_svc = services.get("group_ranking")
        if not gr_svc:
            return
        text = "🏆 **Group Rankings** — Global\n\n"
        categories = ["xp_earned", "coins_earned", "messages_sent", "games_played"]
        cat_labels = {"xp_earned": "⭐ XP", "coins_earned": "💰 Coins", "messages_sent": "💬 Messages", "games_played": "🎮 Games"}
        kb = InlineKeyboardMarkup([
            [InlineKeyboardButton("⭐ Global XP", callback_data="glb_global_xp"),
             InlineKeyboardButton("💰 Global Coins", callback_data="glb_global_coins")],
            [InlineKeyboardButton("💬 Global Messages", callback_data="glb_global_msgs")],
            [InlineKeyboardButton("◀️ Back", callback_data="main_menu")],
        ])
        await message.reply_text(text, reply_markup=kb)

    @app.on_callback_query(filters.regex(r"^glb_xp_(-?\d+)$"))
    async def glb_xp_callback(client: Client, callback: CallbackQuery):
        group_id = int(callback.data.split("_")[-1])
        services = getattr(callback, '_services', None) or getattr(callback.message, '_services', None)
        if not services:
            return
        gr_svc = services.get("group_ranking")
        if gr_svc:
            top = await gr_svc.get_group_top(group_id, "xp_earned", 10)
            text = f"⭐ **Top XP** — {callback.message.chat.title}\n\n"
            medals = ["🥇", "🥈", "🥉"]
            for i, entry in enumerate(top):
                medal = medals[i] if i < 3 else f"#{i+1}"
                text += f"{medal} `{entry.user_id}` — {format_number(entry.xp_earned)} XP\n"
            if not top:
                text += "No activity yet."
            kb = InlineKeyboardMarkup([[InlineKeyboardButton("◀️ Back", callback_data=f"glb_menu_{group_id}")]])
            try:
                await callback.message.edit_text(text, reply_markup=kb)
            except Exception:
                pass
        await callback.answer()

    @app.on_callback_query(filters.regex(r"^glb_coins_(-?\d+)$"))
    async def glb_coins_callback(client: Client, callback: CallbackQuery):
        group_id = int(callback.data.split("_")[-1])
        services = getattr(callback, '_services', None) or getattr(callback.message, '_services', None)
        if not services:
            return
        gr_svc = services.get("group_ranking")
        if gr_svc:
            top = await gr_svc.get_group_top(group_id, "coins_earned", 10)
            text = f"💰 **Top Coins** — {callback.message.chat.title}\n\n"
            medals = ["🥇", "🥈", "🥉"]
            for i, entry in enumerate(top):
                medal = medals[i] if i < 3 else f"#{i+1}"
                text += f"{medal} `{entry.user_id}` — {format_number(entry.coins_earned)} coins\n"
            if not top:
                text += "No activity yet."
            kb = InlineKeyboardMarkup([[InlineKeyboardButton("◀️ Back", callback_data=f"glb_menu_{group_id}")]])
            try:
                await callback.message.edit_text(text, reply_markup=kb)
            except Exception:
                pass
        await callback.answer()

    @app.on_callback_query(filters.regex(r"^glb_msgs_(-?\d+)$"))
    async def glb_msgs_callback(client: Client, callback: CallbackQuery):
        group_id = int(callback.data.split("_")[-1])
        services = getattr(callback, '_services', None) or getattr(callback.message, '_services', None)
        if not services:
            return
        gr_svc = services.get("group_ranking")
        if gr_svc:
            top = await gr_svc.get_group_top(group_id, "messages_sent", 10)
            text = f"💬 **Top Messages** — {callback.message.chat.title}\n\n"
            medals = ["🥇", "🥈", "🥉"]
            for i, entry in enumerate(top):
                medal = medals[i] if i < 3 else f"#{i+1}"
                text += f"{medal} `{entry.user_id}` — {format_number(entry.messages_sent)} msgs\n"
            if not top:
                text += "No activity yet."
            kb = InlineKeyboardMarkup([[InlineKeyboardButton("◀️ Back", callback_data=f"glb_menu_{group_id}")]])
            try:
                await callback.message.edit_text(text, reply_markup=kb)
            except Exception:
                pass
        await callback.answer()

    @app.on_callback_query(filters.regex(r"^glb_games_(-?\d+)$"))
    async def glb_games_callback(client: Client, callback: CallbackQuery):
        group_id = int(callback.data.split("_")[-1])
        services = getattr(callback, '_services', None) or getattr(callback.message, '_services', None)
        if not services:
            return
        gr_svc = services.get("group_ranking")
        if gr_svc:
            top = await gr_svc.get_group_top(group_id, "games_played", 10)
            text = f"🎮 **Top Games** — {callback.message.chat.title}\n\n"
            medals = ["🥇", "🥈", "🥉"]
            for i, entry in enumerate(top):
                medal = medals[i] if i < 3 else f"#{i+1}"
                text += f"{medal} `{entry.user_id}` — {format_number(entry.games_played)} games\n"
            if not top:
                text += "No activity yet."
            kb = InlineKeyboardMarkup([[InlineKeyboardButton("◀️ Back", callback_data=f"glb_menu_{group_id}")]])
            try:
                await callback.message.edit_text(text, reply_markup=kb)
            except Exception:
                pass
        await callback.answer()

    @app.on_callback_query(filters.regex(r"^glb_myrank_(-?\d+)$"))
    async def glb_myrank_callback(client: Client, callback: CallbackQuery):
        group_id = int(callback.data.split("_")[-1])
        services = getattr(callback, '_services', None) or getattr(callback.message, '_services', None)
        if not services:
            return
        gr_svc = services.get("group_ranking")
        if gr_svc:
            stats = await gr_svc.get_user_stats(callback.from_user.id, group_id)
            if not stats:
                await callback.answer("You have no activity in this group yet.", show_alert=True)
                return
            xp_rank = await gr_svc.get_user_rank(callback.from_user.id, group_id, "xp_earned")
            coins_rank = await gr_svc.get_user_rank(callback.from_user.id, group_id, "coins_earned")
            msgs_rank = await gr_svc.get_user_rank(callback.from_user.id, group_id, "messages_sent")
            text = (
                f"👤 **Your Group Rank**\n\n"
                f"⭐ XP: {format_number(stats.xp_earned)} (Rank #{xp_rank})\n"
                f"💰 Coins: {format_number(stats.coins_earned)} (Rank #{coins_rank})\n"
                f"💬 Messages: {format_number(stats.messages_sent)} (Rank #{msgs_rank})\n"
                f"🎮 Games: {format_number(stats.games_played)}\n"
            )
            kb = InlineKeyboardMarkup([[InlineKeyboardButton("◀️ Back", callback_data=f"glb_menu_{group_id}")]])
            try:
                await callback.message.edit_text(text, reply_markup=kb)
            except Exception:
                pass
        await callback.answer()

    @app.on_callback_query(filters.regex(r"^glb_menu_(-?\d+)$"))
    async def glb_menu_callback(client: Client, callback: CallbackQuery):
        group_id = int(callback.data.split("_")[-1])
        text = f"🏆 **Group Leaderboard** — Select ranking type:\n"
        kb = InlineKeyboardMarkup([
            [InlineKeyboardButton("⭐ XP", callback_data=f"glb_xp_{group_id}"),
             InlineKeyboardButton("💰 Coins", callback_data=f"glb_coins_{group_id}")],
            [InlineKeyboardButton("💬 Messages", callback_data=f"glb_msgs_{group_id}"),
             InlineKeyboardButton("🎮 Games", callback_data=f"glb_games_{group_id}")],
            [InlineKeyboardButton("👤 My Rank", callback_data=f"glb_myrank_{group_id}")],
        ])
        try:
            await callback.message.edit_text(text, reply_markup=kb)
        except Exception:
            pass
        await callback.answer()

    @app.on_callback_query(filters.regex(r"^glb_global_xp$"))
    async def glb_global_xp_callback(client: Client, callback: CallbackQuery):
        services = getattr(callback, '_services', None) or getattr(callback.message, '_services', None)
        if not services:
            return
        gr_svc = services.get("group_ranking")
        if gr_svc:
            top = await gr_svc.get_global_top("xp_earned", 10)
            text = "⭐ **Global XP Leaders** (All Groups)\n\n"
            medals = ["🥇", "🥈", "🥉"]
            for i, entry in enumerate(top):
                medal = medals[i] if i < 3 else f"#{i+1}"
                text += f"{medal} `{entry.user_id}` — {format_number(entry.xp_earned)} XP\n"
            if not top:
                text += "No data yet."
            try:
                await callback.message.edit_text(text, reply_markup=InlineKeyboards.back_button("main_menu"))
            except Exception:
                pass
        await callback.answer()

    @app.on_callback_query(filters.regex(r"^glb_global_coins$"))
    async def glb_global_coins_callback(client: Client, callback: CallbackQuery):
        services = getattr(callback, '_services', None) or getattr(callback.message, '_services', None)
        if not services:
            return
        gr_svc = services.get("group_ranking")
        if gr_svc:
            top = await gr_svc.get_global_top("coins_earned", 10)
            text = "💰 **Global Coin Leaders** (All Groups)\n\n"
            medals = ["🥇", "🥈", "🥉"]
            for i, entry in enumerate(top):
                medal = medals[i] if i < 3 else f"#{i+1}"
                text += f"{medal} `{entry.user_id}` — {format_number(entry.coins_earned)} coins\n"
            if not top:
                text += "No data yet."
            try:
                await callback.message.edit_text(text, reply_markup=InlineKeyboards.back_button("main_menu"))
            except Exception:
                pass
        await callback.answer()

    @app.on_callback_query(filters.regex(r"^glb_global_msgs$"))
    async def glb_global_msgs_callback(client: Client, callback: CallbackQuery):
        services = getattr(callback, '_services', None) or getattr(callback.message, '_services', None)
        if not services:
            return
        gr_svc = services.get("group_ranking")
        if gr_svc:
            top = await gr_svc.get_global_top("messages_sent", 10)
            text = "💬 **Global Message Leaders** (All Groups)\n\n"
            medals = ["🥇", "🥈", "🥉"]
            for i, entry in enumerate(top):
                medal = medals[i] if i < 3 else f"#{i+1}"
                text += f"{medal} `{entry.user_id}` — {format_number(entry.messages_sent)} msgs\n"
            if not top:
                text += "No data yet."
            try:
                await callback.message.edit_text(text, reply_markup=InlineKeyboards.back_button("main_menu"))
            except Exception:
                pass
        await callback.answer()
