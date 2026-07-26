from __future__ import annotations

from pyrogram import Client, filters
from pyrogram.types import Message, CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup

from bot.core import loc
from config import settings
from bot.keyboards.inline import InlineKeyboards
from bot.utils.helpers import format_number


def register(app: Client):

    @app.on_message(filters.command("owner") & filters.user(settings.OWNER_ID))
    async def owner_panel_command(client: Client, message: Message):
        text = "👑 **OWNER PANEL**\n\nFull control over the bot."
        kb = _owner_main_panel("en")
        await message.reply_text(text, reply_markup=kb)

    @app.on_callback_query(filters.regex("^owner_panel$"))
    async def owner_panel_callback(client: Client, callback_query: CallbackQuery):
        if callback_query.from_user.id != settings.OWNER_ID:
            await callback_query.answer("❌ Owner only!", show_alert=True)
            return
        text = "👑 **OWNER PANEL**"
        kb = _owner_main_panel("en")
        try:
            await callback_query.message.edit_text(text, reply_markup=kb)
        except Exception:
            await callback_query.message.reply_text(text, reply_markup=kb)
        await callback_query.answer()

    @app.on_callback_query(filters.regex("^ow_users$"))
    async def ow_users_callback(client: Client, callback_query: CallbackQuery):
        if callback_query.from_user.id != settings.OWNER_ID:
            await callback_query.answer("❌ Owner only!", show_alert=True)
            return
        text = "👤 **User Management**\n\nCommands:\n/userinfo <id> - View user\n/searchuser <name> - Search\n/findid <username> - Find by username\n/resetuser <id> - Reset user\n/deleteuser <id> - Soft delete\n/recoveruser <id> - Recover deleted\n/backupuser <id> - Backup user\n/cloneuser <from> <to> - Clone"
        kb = InlineKeyboardMarkup([
            [InlineKeyboardButton("🔍 Search User", callback_data="ow_search")],
            [InlineKeyboardButton("🗑️ Deleted Users", callback_data="ow_deleted")],
            [InlineKeyboardButton("⬅️ Back", callback_data="owner_panel")],
        ])
        await callback_query.message.edit_text(text, reply_markup=kb)
        await callback_query.answer()

    @app.on_callback_query(filters.regex("^ow_economy$"))
    async def ow_economy_callback(client: Client, callback_query: CallbackQuery):
        if callback_query.from_user.id != settings.OWNER_ID:
            await callback_query.answer("❌ Owner only!", show_alert=True)
            return
        text = "💰 **Economy Management**\n\nCommands:\n/addcoins <user> <amount>\n/removecoins <user> <amount>\n/setcoins <user> <amount>\n/addbank <user> <amount>\n/setbank <user> <amount>\n/resetbank <user>\n/resetwallet <user>\n/resetmoney <user>"
        kb = InlineKeyboardMarkup([
            [InlineKeyboardButton("➕ Add Coins", callback_data="ow_addcoins")],
            [InlineKeyboardButton("➖ Remove Coins", callback_data="ow_removecoins")],
            [InlineKeyboardButton("🔄 Reset All", callback_data="ow_resetmoney")],
            [InlineKeyboardButton("⬅️ Back", callback_data="owner_panel")],
        ])
        await callback_query.message.edit_text(text, reply_markup=kb)
        await callback_query.answer()

    @app.on_callback_query(filters.regex("^ow_bank$"))
    async def ow_bank_callback(client: Client, callback_query: CallbackQuery):
        if callback_query.from_user.id != settings.OWNER_ID:
            await callback_query.answer("❌ Owner only!", show_alert=True)
            return
        text = "🏦 **Bank Management**\n\nCommands:\n/setinterest <rate> - Set interest rate\n/resetinterest - Reset to default\n/addinvestment <user> <amount> <type>\n/endinvestment <user> <id>"
        kb = InlineKeyboardMarkup([
            [InlineKeyboardButton("📈 Set Interest", callback_data="ow_setinterest")],
            [InlineKeyboardButton("⬅️ Back", callback_data="owner_panel")],
        ])
        await callback_query.message.edit_text(text, reply_markup=kb)
        await callback_query.answer()

    @app.on_callback_query(filters.regex("^ow_games$"))
    async def ow_games_callback(client: Client, callback_query: CallbackQuery):
        if callback_query.from_user.id != settings.OWNER_ID:
            await callback_query.answer("❌ Owner only!", show_alert=True)
            return
        text = "🎮 **Game Management**\n\nCommands:\n/gameon <type> - Enable game\n/gameoff <type> - Disable game\n/setcooldown <type> <seconds>\n/setdifficulty <type> <level>\n/setreward <type> <xp> <coins>\n/setbetlimit <type> <min> <max>\n/setmultiplier <type> <mult>\n/resetgamestats - Reset all stats"
        kb = InlineKeyboardMarkup([
            [InlineKeyboardButton("✅ Game On", callback_data="ow_gameon"), InlineKeyboardButton("❌ Game Off", callback_data="ow_gameoff")],
            [InlineKeyboardButton("⏱️ Cooldown", callback_data="ow_setcd")],
            [InlineKeyboardButton("🎯 Difficulty", callback_data="ow_setdiff")],
            [InlineKeyboardButton("💰 Rewards", callback_data="ow_setreward")],
            [InlineKeyboardButton("⬅️ Back", callback_data="owner_panel")],
        ])
        await callback_query.message.edit_text(text, reply_markup=kb)
        await callback_query.answer()

    @app.on_callback_query(filters.regex("^ow_leaderboards$"))
    async def ow_leaderboards_callback(client: Client, callback_query: CallbackQuery):
        if callback_query.from_user.id != settings.OWNER_ID:
            await callback_query.answer("❌ Owner only!", show_alert=True)
            return
        text = "🏆 **Leaderboard Management**\n\nCommands:\n/resetleaderboard global\n/resetleaderboard group\n/resetleaderboard games\n/rebuildleaderboard"
        kb = InlineKeyboardMarkup([
            [InlineKeyboardButton("🔄 Rebuild All", callback_data="ow_rebuildlb")],
            [InlineKeyboardButton("🗑️ Reset Global", callback_data="ow_resetlb_global")],
            [InlineKeyboardButton("⬅️ Back", callback_data="owner_panel")],
        ])
        await callback_query.message.edit_text(text, reply_markup=kb)
        await callback_query.answer()

    @app.on_callback_query(filters.regex("^ow_stats$"))
    async def ow_stats_callback(client: Client, callback_query: CallbackQuery):
        if callback_query.from_user.id != settings.OWNER_ID:
            await callback_query.answer("❌ Owner only!", show_alert=True)
            return
        text = "📊 **Statistics**\n\nCommands:\n/resetstats - Reset all stats\n/rebuildstats - Rebuild from data\n/recountxp - Recalculate XP\n/recountmoney - Recalculate balances"
        kb = InlineKeyboardMarkup([
            [InlineKeyboardButton("🔄 Rebuild", callback_data="ow_rebuildstats")],
            [InlineKeyboardButton("⬅️ Back", callback_data="owner_panel")],
        ])
        await callback_query.message.edit_text(text, reply_markup=kb)
        await callback_query.answer()

    @app.on_callback_query(filters.regex("^ow_database$"))
    async def ow_database_callback(client: Client, callback_query: CallbackQuery):
        if callback_query.from_user.id != settings.OWNER_ID:
            await callback_query.answer("❌ Owner only!", show_alert=True)
            return
        text = "📂 **Database**\n\nCommands:\n/dbbackup - Create backup\n/dbrestore - Restore backup\n/dboptimize - Optimize collections\n/dbcompact - Compact data\n/dbstatus - Show DB status"
        kb = InlineKeyboardMarkup([
            [InlineKeyboardButton("💾 Backup", callback_data="ow_dbbackup")],
            [InlineKeyboardButton("📊 Status", callback_data="ow_dbstatus")],
            [InlineKeyboardButton("⬅️ Back", callback_data="owner_panel")],
        ])
        await callback_query.message.edit_text(text, reply_markup=kb)
        await callback_query.answer()

    @app.on_callback_query(filters.regex("^ow_sudo$"))
    async def ow_sudo_callback(client: Client, callback_query: CallbackQuery):
        if callback_query.from_user.id != settings.OWNER_ID:
            await callback_query.answer("❌ Owner only!", show_alert=True)
            return
        text = "👥 **Sudo Management**\n\nCommands:\n/addsudo <user_id>\n/delsudo <user_id>\n/listsudo"
        kb = InlineKeyboardMarkup([
            [InlineKeyboardButton("📋 List Sudo", callback_data="ow_listsudo")],
            [InlineKeyboardButton("⬅️ Back", callback_data="owner_panel")],
        ])
        await callback_query.message.edit_text(text, reply_markup=kb)
        await callback_query.answer()

    @app.on_callback_query(filters.regex("^ow_events$"))
    async def ow_events_callback(client: Client, callback_query: CallbackQuery):
        if callback_query.from_user.id != settings.OWNER_ID:
            await callback_query.answer("❌ Owner only!", show_alert=True)
            return
        text = "🎁 **Events**\n\nCommands:\n/startevent <type> <name>\n/stopevent <id>\n/giveaway\n/spawnboss"
        kb = InlineKeyboardMarkup([
            [InlineKeyboardButton("➕ Start Event", callback_data="ow_startevent")],
            [InlineKeyboardButton("📢 Giveaway", callback_data="ow_giveaway")],
            [InlineKeyboardButton("⬅️ Back", callback_data="owner_panel")],
        ])
        await callback_query.message.edit_text(text, reply_markup=kb)
        await callback_query.answer()

    @app.on_callback_query(filters.regex("^ow_broadcast$"))
    async def ow_broadcast_callback(client: Client, callback_query: CallbackQuery):
        if callback_query.from_user.id != settings.OWNER_ID:
            await callback_query.answer("❌ Owner only!", show_alert=True)
            return
        text = "📢 **Broadcast**\n\nCommands:\n/broadcast <msg> - All users\n/gbroadcast <msg> - All groups\n/dmbroadcast <msg> - DM all users"
        kb = InlineKeyboardMarkup([
            [InlineKeyboardButton("📢 Broadcast", callback_data="ow_dobroadcast")],
            [InlineKeyboardButton("⬅️ Back", callback_data="owner_panel")],
        ])
        await callback_query.message.edit_text(text, reply_markup=kb)
        await callback_query.answer()

    @app.on_callback_query(filters.regex("^ow_settings$"))
    async def ow_settings_callback(client: Client, callback_query: CallbackQuery):
        if callback_query.from_user.id != settings.OWNER_ID:
            await callback_query.answer("❌ Owner only!", show_alert=True)
            return
        text = "⚙️ **Bot Settings**\n\nAll settings configurable via .env or commands.\n\n/maintenance on|off\n/reload\n/restart\n/shutdown"
        kb = InlineKeyboardMarkup([
            [InlineKeyboardButton("🔧 Maintenance", callback_data="ow_maintenance")],
            [InlineKeyboardButton("🔄 Reload", callback_data="ow_reload")],
            [InlineKeyboardButton("⬅️ Back", callback_data="owner_panel")],
        ])
        await callback_query.message.edit_text(text, reply_markup=kb)
        await callback_query.answer()

    @app.on_callback_query(filters.regex("^ow_logs$"))
    async def ow_logs_callback(client: Client, callback_query: CallbackQuery):
        if callback_query.from_user.id != settings.OWNER_ID:
            await callback_query.answer("❌ Owner only!", show_alert=True)
            return
        text = "📝 **Audit Logs**\n\nCommands:\n/logs - View recent logs\n/logs <admin_id> - Admin-specific logs\n/logs <action> - Filter by action"
        kb = InlineKeyboardMarkup([
            [InlineKeyboardButton("📜 Recent Logs", callback_data="ow_recentlogs")],
            [InlineKeyboardButton("⬅️ Back", callback_data="owner_panel")],
        ])
        await callback_query.message.edit_text(text, reply_markup=kb)
        await callback_query.answer()

    @app.on_callback_query(filters.regex("^ow_maintenance$"))
    async def ow_maintenance_toggle(client: Client, callback_query: CallbackQuery):
        if callback_query.from_user.id != settings.OWNER_ID:
            await callback_query.answer("❌ Owner only!", show_alert=True)
            return
        await callback_query.answer("Use /maintenance on or /maintenance off", show_alert=True)

    @app.on_callback_query(filters.regex("^ow_reload$"))
    async def ow_reload_action(client: Client, callback_query: CallbackQuery):
        if callback_query.from_user.id != settings.OWNER_ID:
            await callback_query.answer("❌ Owner only!", show_alert=True)
            return
        from bot.core import loc as loc_instance
        loc_instance.reload()
        await callback_query.answer("✅ Reloaded!", show_alert=True)

    @app.on_callback_query(filters.regex("^ow_recentlogs$"))
    async def ow_recentlogs_callback(client: Client, callback_query: CallbackQuery):
        if callback_query.from_user.id != settings.OWNER_ID:
            await callback_query.answer("❌ Owner only!", show_alert=True)
            return
        services = getattr(callback_query, '_services', None)
        if services:
            owner_svc = services.get("owner")
            if owner_svc:
                logs = await owner_svc.get_audit_logs(limit=10)
                text = "📝 **Recent Audit Logs**\n\n"
                for log in logs:
                    text += f"⚙️ {log.action} | Admin: `{log.admin_id}` | {log.created_at.strftime('%m-%d %H:%M')}\n"
                if not logs:
                    text += "No recent logs."
                try:
                    await callback_query.message.edit_text(text, reply_markup=InlineKeyboards.back_button("ow_logs", "en"))
                except Exception:
                    pass
        await callback_query.answer()


def _owner_main_panel(lang: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("👤 Users", callback_data="ow_users"), InlineKeyboardButton("💰 Economy", callback_data="ow_economy")],
        [InlineKeyboardButton("🏦 Bank", callback_data="ow_bank"), InlineKeyboardButton("🎮 Games", callback_data="ow_games")],
        [InlineKeyboardButton("🏆 Leaderboards", callback_data="ow_leaderboards"), InlineKeyboardButton("📊 Stats", callback_data="ow_stats")],
        [InlineKeyboardButton("📂 Database", callback_data="ow_database"), InlineKeyboardButton("👥 Sudo", callback_data="ow_sudo")],
        [InlineKeyboardButton("🎁 Events", callback_data="ow_events"), InlineKeyboardButton("📢 Broadcast", callback_data="ow_broadcast")],
        [InlineKeyboardButton("⚙️ Settings", callback_data="ow_settings"), InlineKeyboardButton("📝 Logs", callback_data="ow_logs")],
    ])
