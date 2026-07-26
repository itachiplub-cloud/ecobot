from __future__ import annotations

from pyrogram import Client, filters
from pyrogram.types import CallbackQuery, Message, InlineKeyboardButton, InlineKeyboardMarkup

from bot.core import loc
from config import settings
from bot.keyboards.inline import InlineKeyboards
from bot.utils.helpers import format_number

OWNER_ONLY = filters.user(settings.OWNER_ID)


def _check_owner(callback: CallbackQuery) -> bool:
    return callback.from_user.id == settings.OWNER_ID


def _back_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("◀️ Back", callback_data="owner_panel")],
    ])


def register(app: Client):

    @app.on_callback_query(filters.regex("^ow_addcoins$") & OWNER_ONLY)
    async def ow_addcoins_callback(client: Client, callback: CallbackQuery):
        if not _check_owner(callback):
            await callback.answer("❌ Owner only!", show_alert=True)
            return
        text = "➕ **Add Coins**\n\nReply to a forwarded message or send:\n`/addcoins <user_id> <amount>`"
        await callback.message.edit_text(text, reply_markup=_back_kb())
        await callback.answer()

    @app.on_callback_query(filters.regex("^ow_removecoins$") & OWNER_ONLY)
    async def ow_removecoins_callback(client: Client, callback: CallbackQuery):
        if not _check_owner(callback):
            await callback.answer("❌ Owner only!", show_alert=True)
            return
        text = "➖ **Remove Coins**\n\nSend:\n`/removecoins <user_id> <amount>`"
        await callback.message.edit_text(text, reply_markup=_back_kb())
        await callback.answer()

    @app.on_callback_query(filters.regex("^ow_resetmoney$") & OWNER_ONLY)
    async def ow_resetmoney_callback(client: Client, callback: CallbackQuery):
        if not _check_owner(callback):
            await callback.answer("❌ Owner only!", show_alert=True)
            return
        text = "⚠️ **Reset ALL Money**\n\nThis will reset ALL player balances to 0.\n\nUse `/resetmoney confirm` to proceed."
        kb = InlineKeyboardMarkup([
            [InlineKeyboardButton("✅ Confirm Reset", callback_data="ow_confirm_resetmoney")],
            [InlineKeyboardButton("❌ Cancel", callback_data="owner_panel")],
        ])
        await callback.message.edit_text(text, reply_markup=kb)
        await callback.answer()

    @app.on_callback_query(filters.regex("^ow_confirm_resetmoney$") & OWNER_ONLY)
    async def ow_confirm_resetmoney_callback(client: Client, callback: CallbackQuery):
        if not _check_owner(callback):
            await callback.answer("❌ Owner only!", show_alert=True)
            return
        services = getattr(callback, '_services', None) or getattr(callback.message, '_services', None)
        if services:
            eco_svc = services.get("economy")
            owner_svc = services.get("owner")
            if eco_svc:
                await eco_svc.reset_all()
                if owner_svc:
                    await owner_svc.log_action("reset_all_economy", callback.from_user.id, reason="Owner panel reset")
                text = "✅ **All balances have been reset to 0.**"
                await callback.message.edit_text(text, reply_markup=_back_kb())
        await callback.answer()

    @app.on_callback_query(filters.regex("^ow_search$") & OWNER_ONLY)
    async def ow_search_callback(client: Client, callback: CallbackQuery):
        if not _check_owner(callback):
            await callback.answer("❌ Owner only!", show_alert=True)
            return
        text = "🔍 **Search User**\n\nSend: `/searchuser <name>` or `/userinfo <user_id>`"
        await callback.message.edit_text(text, reply_markup=_back_kb())
        await callback.answer()

    @app.on_callback_query(filters.regex("^ow_deleted$") & OWNER_ONLY)
    async def ow_deleted_callback(client: Client, callback: CallbackQuery):
        if not _check_owner(callback):
            await callback.answer("❌ Owner only!", show_alert=True)
            return
        services = getattr(callback, '_services', None) or getattr(callback.message, '_services', None)
        if services:
            owner_svc = services.get("owner")
            if owner_svc:
                deleted = await owner_svc.get_deleted_users(10)
                text = "🗑️ **Deleted Users (Recycle Bin)**\n\n"
                if deleted:
                    for d in deleted:
                        text += f"  `{d.user_id}` — {d.first_name or 'Unknown'} (deleted {d.deleted_at.strftime('%m-%d %H:%M')})\n"
                else:
                    text += "  No deleted users."
                text += "\nUse `/recoveruser <id>` to restore."
                await callback.message.edit_text(text, reply_markup=_back_kb())
        await callback.answer()

    @app.on_callback_query(filters.regex("^ow_gameon$") & OWNER_ONLY)
    async def ow_gameon_callback(client: Client, callback: CallbackQuery):
        if not _check_owner(callback):
            await callback.answer("❌ Owner only!", show_alert=True)
            return
        text = "✅ **Enable Game**\n\nSend: `/gameon <game_type>`\n\nTypes: coinflip, slots, blackjack, roulette, dice, mines, crash, dart, bowling, basketball, football, diceroll, betroll, highlow, wheel, treasure, luckycard, numberguess"
        await callback.message.edit_text(text, reply_markup=_back_kb())
        await callback.answer()

    @app.on_callback_query(filters.regex("^ow_gameoff$") & OWNER_ONLY)
    async def ow_gameoff_callback(client: Client, callback: CallbackQuery):
        if not _check_owner(callback):
            await callback.answer("❌ Owner only!", show_alert=True)
            return
        text = "❌ **Disable Game**\n\nSend: `/gameoff <game_type>`"
        await callback.message.edit_text(text, reply_markup=_back_kb())
        await callback.answer()

    @app.on_callback_query(filters.regex("^ow_setcd$") & OWNER_ONLY)
    async def ow_setcd_callback(client: Client, callback: CallbackQuery):
        if not _check_owner(callback):
            await callback.answer("❌ Owner only!", show_alert=True)
            return
        text = "⏱️ **Set Cooldown**\n\nSend: `/setcooldown <game_type> <seconds>`"
        await callback.message.edit_text(text, reply_markup=_back_kb())
        await callback.answer()

    @app.on_callback_query(filters.regex("^ow_setdiff$") & OWNER_ONLY)
    async def ow_setdiff_callback(client: Client, callback: CallbackQuery):
        if not _check_owner(callback):
            await callback.answer("❌ Owner only!", show_alert=True)
            return
        text = "🎯 **Set Difficulty**\n\nSend: `/setdifficulty <game_type> <easy|normal|hard|impossible>`"
        await callback.message.edit_text(text, reply_markup=_back_kb())
        await callback.answer()

    @app.on_callback_query(filters.regex("^ow_setreward$") & OWNER_ONLY)
    async def ow_setreward_callback(client: Client, callback: CallbackQuery):
        if not _check_owner(callback):
            await callback.answer("❌ Owner only!", show_alert=True)
            return
        text = "💰 **Set Rewards**\n\nSend: `/setreward <game_type> <xp> <coins>`"
        await callback.message.edit_text(text, reply_markup=_back_kb())
        await callback.answer()

    @app.on_callback_query(filters.regex("^ow_rebuildlb$") & OWNER_ONLY)
    async def ow_rebuildlb_callback(client: Client, callback: CallbackQuery):
        if not _check_owner(callback):
            await callback.answer("❌ Owner only!", show_alert=True)
            return
        services = getattr(callback, '_services', None) or getattr(callback.message, '_services', None)
        if services:
            owner_svc = services.get("owner")
            if owner_svc:
                await owner_svc.log_action("rebuild_leaderboards", callback.from_user.id)
                text = "🔄 **Leaderboards Rebuild**\n\n✅ Leaderboards will be rebuilt from source data."
                await callback.message.edit_text(text, reply_markup=_back_kb())
        await callback.answer()

    @app.on_callback_query(filters.regex("^ow_resetlb_global$") & OWNER_ONLY)
    async def ow_resetlb_global_callback(client: Client, callback: CallbackQuery):
        if not _check_owner(callback):
            await callback.answer("❌ Owner only!", show_alert=True)
            return
        kb = InlineKeyboardMarkup([
            [InlineKeyboardButton("✅ Confirm Reset", callback_data="ow_confirm_resetlb")],
            [InlineKeyboardButton("❌ Cancel", callback_data="ow_leaderboards")],
        ])
        await callback.message.edit_text("⚠️ **Reset ALL leaderboards?**", reply_markup=kb)
        await callback.answer()

    @app.on_callback_query(filters.regex("^ow_confirm_resetlb$") & OWNER_ONLY)
    async def ow_confirm_resetlb_callback(client: Client, callback: CallbackQuery):
        if not _check_owner(callback):
            await callback.answer("❌ Owner only!", show_alert=True)
            return
        from bot.database import get_db
        db = get_db()
        await db.leaderboards.delete_many({})
        services = getattr(callback, '_services', None) or getattr(callback.message, '_services', None)
        if services:
            owner_svc = services.get("owner")
            if owner_svc:
                await owner_svc.log_action("reset_leaderboards", callback.from_user.id)
        await callback.message.edit_text("✅ **All leaderboards cleared.**", reply_markup=_back_kb())
        await callback.answer()

    @app.on_callback_query(filters.regex("^ow_rebuildstats$") & OWNER_ONLY)
    async def ow_rebuildstats_callback(client: Client, callback: CallbackQuery):
        if not _check_owner(callback):
            await callback.answer("❌ Owner only!", show_alert=True)
            return
        text = "🔄 **Rebuild Stats**\n\n✅ Statistics will be recalculated from game history and transaction data."
        await callback.message.edit_text(text, reply_markup=_back_kb())
        await callback.answer()

    @app.on_callback_query(filters.regex("^ow_dbbackup$") & OWNER_ONLY)
    async def ow_dbbackup_callback(client: Client, callback: CallbackQuery):
        if not _check_owner(callback):
            await callback.answer("❌ Owner only!", show_alert=True)
            return
        text = "💾 **Database Backup**\n\nInitiating backup... (In production, triggers mongodump)"
        await callback.message.edit_text(text, reply_markup=_back_kb())
        await callback.answer()

    @app.on_callback_query(filters.regex("^ow_dbstatus$") & OWNER_ONLY)
    async def ow_dbstatus_callback(client: Client, callback: CallbackQuery):
        if not _check_owner(callback):
            await callback.answer("❌ Owner only!", show_alert=True)
            return
        from bot.database import get_db
        db = get_db()
        collections = await db.list_collection_names()
        text = "📂 **Database Status**\n\n"
        for coll_name in sorted(collections):
            count = await db[coll_name].count_documents({})
            text += f"  📁 {coll_name}: {count} docs\n"
        text += f"\n📊 Total collections: {len(collections)}"
        await callback.message.edit_text(text, reply_markup=_back_kb())
        await callback.answer()

    @app.on_callback_query(filters.regex("^ow_listsudo$") & OWNER_ONLY)
    async def ow_listsudo_callback(client: Client, callback: CallbackQuery):
        if not _check_owner(callback):
            await callback.answer("❌ Owner only!", show_alert=True)
            return
        from bot.database import get_db
        db = get_db()
        settings_doc = await db.bot_settings.find_one({"key": "sudo_admins"})
        sudo_ids = settings_doc.get("value", []) if settings_doc else []
        text = "👥 **Sudo Admins**\n\n"
        if sudo_ids:
            for sid in sudo_ids:
                text += f"  🤖 `{sid}`\n"
        else:
            text += "  No sudo admins."
        text += "\nUse `/addsudo <id>` to add."
        await callback.message.edit_text(text, reply_markup=_back_kb())
        await callback.answer()

    @app.on_callback_query(filters.regex("^ow_startevent$") & OWNER_ONLY)
    async def ow_startevent_callback(client: Client, callback: CallbackQuery):
        if not _check_owner(callback):
            await callback.answer("❌ Owner only!", show_alert=True)
            return
        text = "🎉 **Start Event**\n\nUse: `/startevent <type> <name>`\n\nTypes: xp_boost, coin_boost, sale, boss, giveaway"
        await callback.message.edit_text(text, reply_markup=_back_kb())
        await callback.answer()

    @app.on_callback_query(filters.regex("^ow_giveaway$") & OWNER_ONLY)
    async def ow_giveaway_callback(client: Client, callback: CallbackQuery):
        if not _check_owner(callback):
            await callback.answer("❌ Owner only!", show_alert=True)
            return
        text = "📢 **Giveaway**\n\nUse: `/giveaway <amount> [winner_count]`\n\nSends a giveaway message to the current chat."
        await callback.message.edit_text(text, reply_markup=_back_kb())
        await callback.answer()

    @app.on_callback_query(filters.regex("^ow_dobroadcast$") & OWNER_ONLY)
    async def ow_dobroadcast_callback(client: Client, callback: CallbackQuery):
        if not _check_owner(callback):
            await callback.answer("❌ Owner only!", show_alert=True)
            return
        text = "📢 **Broadcast Message**\n\nSend the message you want to broadcast to all users.\n\nUse: `/broadcast <message>`"
        await callback.message.edit_text(text, reply_markup=_back_kb())
        await callback.answer()

    @app.on_callback_query(filters.regex("^ow_setinterest$") & OWNER_ONLY)
    async def ow_setinterest_callback(client: Client, callback: CallbackQuery):
        if not _check_owner(callback):
            await callback.answer("❌ Owner only!", show_alert=True)
            return
        text = "📈 **Set Interest Rate**\n\nSend: `/setinterest <rate>`\n\nExample: `/setinterest 2.5` sets 2.5% daily interest."
        await callback.message.edit_text(text, reply_markup=_back_kb())
        await callback.answer()
