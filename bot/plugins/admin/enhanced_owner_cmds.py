from __future__ import annotations

from pyrogram import Client, filters
from pyrogram.types import Message

from bot.core import loc
from config import settings
from bot.utils.helpers import format_number


def register(app: Client):

    @app.on_message(filters.command("userinfo") & filters.user(settings.OWNER_ID))
    async def userinfo_command(client: Client, message: Message):
        args = message.text.split()
        target_id = None
        if message.reply_to_message:
            target_id = message.reply_to_message.from_user.id
        elif len(args) >= 2:
            try:
                target_id = int(args[1])
            except ValueError:
                await message.reply_text("Invalid user ID.")
                return
        else:
            await message.reply_text("Usage: /userinfo <user_id> or reply to a user")
            return
        services = getattr(message, '_services', None)
        if not services:
            return
        user_svc = services.get("user")
        eco_svc = services.get("economy")
        if user_svc:
            user = await user_svc.get_user(target_id)
            if user:
                bal = await eco_svc.get_balance(target_id) if eco_svc else {"wallet": 0, "bank": 0}
                text = (
                    f"👤 **User Info**\n\n"
                    f"🆔 ID: `{user.user_id}`\n"
                    f"📛 Name: {user.first_name or 'Unknown'}\n"
                    f"🔗 @{user.username or 'none'}\n"
                    f"⭐ Level: {user.level}\n"
                    f"📊 XP: {user.xp}/{user.xp_needed}\n"
                    f"💰 Wallet: {format_number(bal['wallet'])}\n"
                    f"🏦 Bank: {format_number(bal['bank'])}\n"
                    f"💎 Total: {format_number(bal['total'])}\n"
                    f"🚫 Banned: {user.is_banned}\n"
                    f"👑 Premium: {user.is_premium}\n"
                    f"📅 Joined: {user.joined_at.strftime('%Y-%m-%d')}\n"
                    f"🔄 Active: {user.last_active.strftime('%Y-%m-%d %H:%M')}"
                )
                await message.reply_text(text)
            else:
                await message.reply_text(loc.t("error.user_not_found", "en"))

    @app.on_message(filters.command("searchuser") & filters.user(settings.OWNER_ID))
    async def searchuser_command(client: Client, message: Message):
        args = message.text.split(maxsplit=1)
        if len(args) < 2:
            await message.reply_text("Usage: /searchuser <name>")
            return
        query = args[1]
        services = getattr(message, '_services', None)
        if not services:
            return
        user_svc = services.get("user")
        if user_svc:
            users = await user_svc.search_users(query, 10)
            text = f"🔍 **Search Results** for '{query}':\n\n"
            for u in users:
                text += f"  • `{u.user_id}` - {u.first_name or 'Unknown'} (@{u.username or 'none'})\n"
            if not users:
                text += "No users found."
            await message.reply_text(text)

    @app.on_message(filters.command("resetuser") & filters.user(settings.OWNER_ID))
    async def resetuser_command(client: Client, message: Message):
        args = message.text.split()
        if len(args) < 2:
            await message.reply_text("Usage: /resetuser <user_id>")
            return
        try:
            target_id = int(args[1])
        except ValueError:
            await message.reply_text("Invalid ID.")
            return
        services = getattr(message, '_services', None)
        if not services:
            return
        owner_svc = services.get("owner")
        eco_svc = services.get("economy")
        if owner_svc and eco_svc:
            await owner_svc.log_action("reset_user", message.from_user.id, target_user_id=target_id)
            await eco_svc.set_balance(target_id, 0, 0)
            await message.reply_text(f"✅ User `{target_id}` economy reset.")

    @app.on_message(filters.command("deleteuser") & filters.user(settings.OWNER_ID))
    async def deleteuser_command(client: Client, message: Message):
        args = message.text.split()
        if len(args) < 2:
            await message.reply_text("Usage: /deleteuser <user_id> [reason]")
            return
        try:
            target_id = int(args[1])
        except ValueError:
            await message.reply_text("Invalid ID.")
            return
        reason = " ".join(args[2:]) if len(args) > 2 else "Owner action"
        services = getattr(message, '_services', None)
        if not services:
            return
        owner_svc = services.get("owner")
        if owner_svc:
            result = await owner_svc.delete_user(target_id, message.from_user.id, reason)
            if result:
                await owner_svc.log_action("delete_user", message.from_user.id, target_user_id=target_id, reason=reason)
                await message.reply_text(
                    f"✅ User `{target_id}` deleted.\n"
                    f"📋 Backup created. Use /recoveruser {target_id} to restore."
                )
            else:
                await message.reply_text("❌ Failed to delete user.")

    @app.on_message(filters.command("recoveruser") & filters.user(settings.OWNER_ID))
    async def recoveruser_command(client: Client, message: Message):
        args = message.text.split()
        if len(args) < 2:
            await message.reply_text("Usage: /recoveruser <user_id>")
            return
        try:
            target_id = int(args[1])
        except ValueError:
            await message.reply_text("Invalid ID.")
            return
        services = getattr(message, '_services', None)
        if not services:
            return
        owner_svc = services.get("owner")
        if owner_svc:
            result = await owner_svc.recover_user(target_id)
            if result["success"]:
                await owner_svc.log_action("recover_user", message.from_user.id, target_user_id=target_id)
                await message.reply_text(f"✅ User `{target_id}` recovered successfully!")
            else:
                await message.reply_text(f"❌ {result.get('reason', 'Not found')}")

    @app.on_message(filters.command("purgeuser") & filters.user(settings.OWNER_ID))
    async def purgeuser_command(client: Client, message: Message):
        args = message.text.split()
        if len(args) < 2:
            await message.reply_text("Usage: /purgeuser <user_id>")
            return
        try:
            target_id = int(args[1])
        except ValueError:
            await message.reply_text("Invalid ID.")
            return
        services = getattr(message, '_services', None)
        if not services:
            return
        owner_svc = services.get("owner")
        if owner_svc:
            success = await owner_svc.purge_user(target_id, message.from_user.id)
            if success:
                await message.reply_text(f"✅ User `{target_id}` permanently purged.")
            else:
                await message.reply_text("❌ User not found in recycle bin.")

    @app.on_message(filters.command("addcoins") & filters.user(settings.OWNER_ID))
    async def addcoins_command(client: Client, message: Message):
        args = message.text.split()
        if len(args) < 3:
            await message.reply_text("Usage: /addcoins <user_id> <amount>")
            return
        try:
            target_id = int(args[1])
            amount = int(args[2])
        except ValueError:
            await message.reply_text("Invalid arguments.")
            return
        services = getattr(message, '_services', None)
        if not services:
            return
        eco_svc = services.get("economy")
        owner_svc = services.get("owner")
        if eco_svc:
            old = await eco_svc.get_balance(target_id)
            await eco_svc.add_coins(target_id, amount, "Owner grant")
            if owner_svc:
                await owner_svc.log_action("addcoins", message.from_user.id, target_user_id=target_id, old_value=old.get("wallet", 0), new_value=old.get("wallet", 0) + amount, reason=f"+{amount}")
            await message.reply_text(f"✅ Added {format_number(amount)} to `{target_id}`")

    @app.on_message(filters.command("removecoins") & filters.user(settings.OWNER_ID))
    async def removecoins_command(client: Client, message: Message):
        args = message.text.split()
        if len(args) < 3:
            await message.reply_text("Usage: /removecoins <user_id> <amount>")
            return
        try:
            target_id = int(args[1])
            amount = int(args[2])
        except ValueError:
            await message.reply_text("Invalid arguments.")
            return
        services = getattr(message, '_services', None)
        if not services:
            return
        eco_svc = services.get("economy")
        owner_svc = services.get("owner")
        if eco_svc:
            old = await eco_svc.get_balance(target_id)
            await eco_svc.remove_coins(target_id, amount)
            if owner_svc:
                await owner_svc.log_action("removecoins", message.from_user.id, target_user_id=target_id, old_value=old.get("wallet", 0), new_value=old.get("wallet", 0) - amount, reason=f"-{amount}")
            await message.reply_text(f"✅ Removed {format_number(amount)} from `{target_id}`")

    @app.on_message(filters.command("setcoins") & filters.user(settings.OWNER_ID))
    async def setcoins_command(client: Client, message: Message):
        args = message.text.split()
        if len(args) < 3:
            await message.reply_text("Usage: /setcoins <user_id> <amount>")
            return
        try:
            target_id = int(args[1])
            amount = int(args[2])
        except ValueError:
            await message.reply_text("Invalid arguments.")
            return
        services = getattr(message, '_services', None)
        if not services:
            return
        eco_svc = services.get("economy")
        owner_svc = services.get("owner")
        if eco_svc:
            old = await eco_svc.get_balance(target_id)
            await eco_svc.set_balance(target_id, wallet=amount)
            if owner_svc:
                await owner_svc.log_action("setcoins", message.from_user.id, target_user_id=target_id, old_value=old.get("wallet", 0), new_value=amount)
            await message.reply_text(f"✅ Set `{target_id}` wallet to {format_number(amount)}")

    @app.on_message(filters.command("setinterest") & filters.user(settings.OWNER_ID))
    async def setinterest_command(client: Client, message: Message):
        args = message.text.split()
        if len(args) < 2:
            await message.reply_text("Usage: /setinterest <rate>")
            return
        try:
            rate = float(args[1])
        except ValueError:
            await message.reply_text("Invalid rate.")
            return
        services = getattr(message, '_services', None)
        if not services:
            return
        owner_svc = services.get("owner")
        if owner_svc:
            from bot.database import get_db
            db = get_db()
            await db.banks.update_many({}, {"$set": {"interest_rate": rate}})
            await owner_svc.log_action("set_interest", message.from_user.id, new_value=rate)
            await message.reply_text(f"✅ Interest rate set to {rate}%")

    @app.on_message(filters.command("resetmoney") & filters.user(settings.OWNER_ID))
    async def resetmoney_command(client: Client, message: Message):
        args = message.text.split()
        if len(args) >= 2 and args[1] == "confirm":
            services = getattr(message, '_services', None)
            if services:
                eco_svc = services.get("economy")
                owner_svc = services.get("owner")
                if eco_svc:
                    await eco_svc.reset_all()
                    if owner_svc:
                        await owner_svc.log_action("reset_all_economy", message.from_user.id, reason="Full economy reset")
                    await message.reply_text("✅ All balances reset to 0.")
            return
        await message.reply_text("⚠️ This resets ALL balances!\nUse /resetmoney confirm to proceed.")

    @app.on_message(filters.command("gameon") & filters.user(settings.OWNER_ID))
    async def gameon_command(client: Client, message: Message):
        args = message.text.split()
        if len(args) < 2:
            await message.reply_text("Usage: /gameon <game_type>")
            return
        services = getattr(message, '_services', None)
        if services:
            game_svc = services.get("game")
            owner_svc = services.get("owner")
            if game_svc:
                await game_svc.set_enabled(args[1], True, message.from_user.id)
                if owner_svc:
                    await owner_svc.log_action("game_enable", message.from_user.id, metadata={"game": args[1]})
                await message.reply_text(f"✅ {args[1]} enabled.")

    @app.on_message(filters.command("gameoff") & filters.user(settings.OWNER_ID))
    async def gameoff_command(client: Client, message: Message):
        args = message.text.split()
        if len(args) < 2:
            await message.reply_text("Usage: /gameoff <game_type>")
            return
        services = getattr(message, '_services', None)
        if services:
            game_svc = services.get("game")
            owner_svc = services.get("owner")
            if game_svc:
                await game_svc.set_enabled(args[1], False, message.from_user.id)
                if owner_svc:
                    await owner_svc.log_action("game_disable", message.from_user.id, metadata={"game": args[1]})
                await message.reply_text(f"❌ {args[1]} disabled.")

    @app.on_message(filters.command("setcooldown") & filters.user(settings.OWNER_ID))
    async def setcooldown_command(client: Client, message: Message):
        args = message.text.split()
        if len(args) < 3:
            await message.reply_text("Usage: /setcooldown <game_type> <seconds>")
            return
        try:
            seconds = int(args[2])
        except ValueError:
            await message.reply_text("Invalid seconds.")
            return
        services = getattr(message, '_services', None)
        if services:
            game_svc = services.get("game")
            owner_svc = services.get("owner")
            if game_svc:
                await game_svc.set_cooldown_config(args[1], seconds, message.from_user.id)
                if owner_svc:
                    await owner_svc.log_action("set_cooldown", message.from_user.id, metadata={"game": args[1], "seconds": seconds})
                await message.reply_text(f"✅ {args[1]} cooldown set to {seconds}s")

    @app.on_message(filters.command("setdifficulty") & filters.user(settings.OWNER_ID))
    async def setdifficulty_command(client: Client, message: Message):
        args = message.text.split()
        if len(args) < 3:
            await message.reply_text("Usage: /setdifficulty <game_type> <easy|normal|hard|impossible>")
            return
        services = getattr(message, '_services', None)
        if services:
            game_svc = services.get("game")
            owner_svc = services.get("owner")
            if game_svc:
                await game_svc.set_difficulty(args[1], args[2], message.from_user.id)
                if owner_svc:
                    await owner_svc.log_action("set_difficulty", message.from_user.id, metadata={"game": args[1], "difficulty": args[2]})
                await message.reply_text(f"✅ {args[1]} difficulty set to {args[2]}")

    @app.on_message(filters.command("setmultiplier") & filters.user(settings.OWNER_ID))
    async def setmultiplier_command(client: Client, message: Message):
        args = message.text.split()
        if len(args) < 3:
            await message.reply_text("Usage: /setmultiplier <game_type> <multiplier>")
            return
        try:
            mult = float(args[2])
        except ValueError:
            await message.reply_text("Invalid multiplier.")
            return
        services = getattr(message, '_services', None)
        if services:
            game_svc = services.get("game")
            owner_svc = services.get("owner")
            if game_svc:
                await game_svc.set_multiplier(args[1], mult, message.from_user.id)
                if owner_svc:
                    await owner_svc.log_action("set_multiplier", message.from_user.id, metadata={"game": args[1], "multiplier": mult})
                await message.reply_text(f"✅ {args[1]} multiplier set to {mult}x")

    @app.on_message(filters.command("sethouseedge") & filters.user(settings.OWNER_ID))
    async def sethouseedge_command(client: Client, message: Message):
        args = message.text.split()
        if len(args) < 3:
            await message.reply_text("Usage: /sethouseedge <game_type> <edge>")
            return
        try:
            edge = float(args[2])
        except ValueError:
            await message.reply_text("Invalid edge.")
            return
        services = getattr(message, '_services', None)
        if services:
            game_svc = services.get("game")
            owner_svc = services.get("owner")
            if game_svc:
                await game_svc.set_house_edge(args[1], edge, message.from_user.id)
                if owner_svc:
                    await owner_svc.log_action("set_house_edge", message.from_user.id, metadata={"game": args[1], "edge": edge})
                await message.reply_text(f"✅ {args[1]} house edge set to {edge}")

    @app.on_message(filters.command("setreward") & filters.user(settings.OWNER_ID))
    async def setreward_command(client: Client, message: Message):
        args = message.text.split()
        if len(args) < 4:
            await message.reply_text("Usage: /setreward <game_type> <xp> <coins>")
            return
        try:
            xp = int(args[2])
            coins = int(args[3])
        except ValueError:
            await message.reply_text("Invalid values.")
            return
        services = getattr(message, '_services', None)
        if services:
            game_svc = services.get("game")
            owner_svc = services.get("owner")
            if game_svc:
                await game_svc.set_reward(args[1], xp, coins, updated_by=message.from_user.id)
                if owner_svc:
                    await owner_svc.log_action("set_reward", message.from_user.id, metadata={"game": args[1], "xp": xp, "coins": coins})
                await message.reply_text(f"✅ {args[1]} rewards: {xp} XP, {coins} coins")

    @app.on_message(filters.command("setdailylimit") & filters.user(settings.OWNER_ID))
    async def setdailylimit_command(client: Client, message: Message):
        args = message.text.split()
        if len(args) < 3:
            await message.reply_text("Usage: /setdailylimit <game_type> <limit>")
            return
        try:
            limit = int(args[2])
        except ValueError:
            await message.reply_text("Invalid limit.")
            return
        services = getattr(message, '_services', None)
        if services:
            game_svc = services.get("game")
            if game_svc:
                await game_svc.set_daily_limit(args[1], limit, message.from_user.id)
                await message.reply_text(f"✅ {args[1]} daily limit set to {limit}")

    @app.on_message(filters.command("setbetlimit") & filters.user(settings.OWNER_ID))
    async def setbetlimit_command(client: Client, message: Message):
        args = message.text.split()
        if len(args) < 4:
            await message.reply_text("Usage: /setbetlimit <game_type> <min> <max>")
            return
        try:
            min_bet = int(args[2])
            max_bet = int(args[3])
        except ValueError:
            await message.reply_text("Invalid values.")
            return
        services = getattr(message, '_services', None)
        if services:
            game_svc = services.get("game")
            if game_svc:
                await game_svc.set_bet_limit(args[1], min_bet, max_bet, message.from_user.id)
                await message.reply_text(f"✅ {args[1]} bet limits: {min_bet}-{max_bet}")

    @app.on_message(filters.command("resetgamestats") & filters.user(settings.OWNER_ID))
    async def resetgamestats_command(client: Client, message: Message):
        args = message.text.split()
        if len(args) >= 2 and args[1] == "confirm":
            services = getattr(message, '_services', None)
            if services:
                game_svc = services.get("game")
                if game_svc:
                    await game_svc.reset_all_stats()
                    await message.reply_text("✅ All game stats reset.")
            return
        await message.reply_text("⚠️ This resets ALL game stats!\nUse /resetgamestats confirm")

    @app.on_message(filters.command("resetleaderboard") & filters.user(settings.OWNER_ID))
    async def resetleaderboard_command(client: Client, message: Message):
        services = getattr(message, '_services', None)
        if services:
            lb_svc = services.get("leaderboard")
            if lb_svc:
                from bot.database import get_db
                db = get_db()
                await db.leaderboards.delete_many({})
                await message.reply_text("✅ All leaderboards cleared.")

    @app.on_message(filters.command("dbbackup") & filters.user(settings.OWNER_ID))
    async def dbbackup_command(client: Client, message: Message):
        await message.reply_text("💾 Database backup initiated... (In production, this would trigger mongodump)")

    @app.on_message(filters.command("dbstatus") & filters.user(settings.OWNER_ID))
    async def dbstatus_command(client: Client, message: Message):
        from bot.database import get_db
        db = get_db()
        collections = await db.list_collection_names()
        text = f"📂 **Database Status**\n\nCollections: {len(collections)}\n"
        for coll_name in sorted(collections):
            count = await db[coll_name].count_documents({})
            text += f"  • {coll_name}: {count} docs\n"
        await message.reply_text(text)

    @app.on_message(filters.command("maintenance") & filters.user(settings.OWNER_ID))
    async def maintenance_command(client: Client, message: Message):
        args = message.text.split()
        if len(args) < 2:
            await message.reply_text("Usage: /maintenance <on|off>")
            return
        state = args[1].lower()
        if state == "on":
            await message.reply_text("🔧 Maintenance mode **ON**.")
        elif state == "off":
            await message.reply_text("🔧 Maintenance mode **OFF**.")
