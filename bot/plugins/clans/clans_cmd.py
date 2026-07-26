from __future__ import annotations

from pyrogram import Client, filters
from pyrogram.types import CallbackQuery, Message

from bot.core import loc
from bot.keyboards.inline import InlineKeyboards
from bot.utils.formatting import format_guild
from bot.utils.helpers import format_number


def register(app: Client):
    @app.on_message(filters.command("clan"))
    async def clan_command(client: Client, message: Message):
        lang = "en"
        await message.reply_text(loc.t("guild.title", lang), reply_markup=InlineKeyboards.clan_menu(lang))

    @app.on_message(filters.command("clancreate") | filters.command("cc"))
    async def clan_create_command(client: Client, message: Message):
        args = message.text.split()
        if len(args) < 3:
            await message.reply_text("Usage: /clancreate <name> <tag>")
            return
        name = args[1]
        tag = args[2]
        user = message.from_user
        if message._services:
            guild_svc = message._services.get("guild")
            if guild_svc:
                result = await guild_svc.create_guild(user.id, name, tag)
                if result["success"]:
                    await message.reply_text(loc.t("guild.create_success", "en", name=name))
                else:
                    reason = result.get("reason", "unknown")
                    if reason == "already_in_guild":
                        await message.reply_text(loc.t("guild.already_in", "en"))
                    elif reason == "name_taken":
                        await message.reply_text("❌ Clan name already taken.")
                    else:
                        await message.reply_text(loc.t("guild.create_failed", "en"))

    @app.on_message(filters.command("clanjoin"))
    async def clan_join_command(client: Client, message: Message):
        args = message.text.split()
        if len(args) < 2:
            await message.reply_text("Usage: /clanjoin <guild_id>")
            return
        try:
            guild_id = int(args[1])
        except ValueError:
            await message.reply_text("Invalid guild ID.")
            return
        if message._services:
            guild_svc = message._services.get("guild")
            if guild_svc:
                result = await guild_svc.join_guild(message.from_user.id, guild_id)
                if result["success"]:
                    await message.reply_text(loc.t("guild.join_success", "en", name=str(guild_id)))
                else:
                    await message.reply_text(loc.t("guild.join_failed", "en"))

    @app.on_message(filters.command("clanleave"))
    async def clan_leave_command(client: Client, message: Message):
        if message._services:
            guild_svc = message._services.get("guild")
            if guild_svc:
                result = await guild_svc.leave_guild(message.from_user.id)
                if result["success"]:
                    await message.reply_text(loc.t("guild.leave_success", "en"))
                else:
                    reason = result.get("reason", "unknown")
                    if reason == "owner_cannot_leave":
                        await message.reply_text(loc.t("guild.leave_owner", "en"))
                    else:
                        await message.reply_text(loc.t("guild.not_in", "en"))

    @app.on_message(filters.command("clandeposit") | filters.command("cd"))
    async def clan_deposit_command(client: Client, message: Message):
        args = message.text.split()
        if len(args) < 2:
            await message.reply_text("Usage: /clandeposit <amount>")
            return
        try:
            amount = int(args[1])
        except ValueError:
            await message.reply_text("Invalid amount.")
            return
        if message._services:
            guild_svc = message._services.get("guild")
            eco_svc = message._services.get("economy")
            if guild_svc and eco_svc:
                result = await eco_svc.remove_coins(message.from_user.id, amount, "Guild deposit")
                if result["success"]:
                    await guild_svc.deposit_guild(message.from_user.id, amount)
                    await message.reply_text(loc.t("guild.deposit_success", "en", amount=format_number(amount)))
                else:
                    await message.reply_text(loc.t("error.insufficient_funds", "en"))

    @app.on_callback_query(filters.regex("^clans_menu$"))
    async def clans_menu_callback(client: Client, callback_query: CallbackQuery):
        lang = "en"
        text = loc.t("guild.title", lang)
        try:
            await callback_query.message.edit_text(text, reply_markup=InlineKeyboards.clan_menu(lang))
        except Exception:
            await callback_query.message.reply_text(text, reply_markup=InlineKeyboards.clan_menu(lang))
        await callback_query.answer()

    @app.on_callback_query(filters.regex("^clan_info$"))
    async def clan_info_callback(client: Client, callback_query: CallbackQuery):
        user = callback_query.from_user
        lang = "en"
        if callback_query._services:
            guild_svc = callback_query._services.get("guild")
            if guild_svc:
                member = await guild_svc.get_user_guild(user.id)
                if member:
                    guild = await guild_svc.get_guild(member.guild_id)
                    if guild:
                        text = format_guild(guild, lang)
                    else:
                        text = loc.t("guild.not_in", lang)
                else:
                    text = loc.t("guild.not_in", lang)
                try:
                    await callback_query.message.edit_text(text, reply_markup=InlineKeyboards.back_button("clans_menu", lang))
                except Exception:
                    await callback_query.message.reply_text(text, reply_markup=InlineKeyboards.back_button("clans_menu", lang))
        await callback_query.answer()

    @app.on_callback_query(filters.regex("^clan_members$"))
    async def clan_members_callback(client: Client, callback_query: CallbackQuery):
        user = callback_query.from_user
        lang = "en"
        if callback_query._services:
            guild_svc = callback_query._services.get("guild")
            if guild_svc:
                member = await guild_svc.get_user_guild(user.id)
                if member:
                    members = await guild_svc.get_guild_members(member.guild_id)
                    text = "👥 **Clan Members**\n\n"
                    for m in members:
                        role_icon = "👑" if m.role == "leader" else "⭐" if m.role == "officer" else "👤"
                        text += f"  {role_icon} `{m.user_id}` - {m.role}\n"
                else:
                    text = loc.t("guild.not_in", lang)
                try:
                    await callback_query.message.edit_text(text, reply_markup=InlineKeyboards.back_button("clans_menu", lang))
                except Exception:
                    await callback_query.message.reply_text(text, reply_markup=InlineKeyboards.back_button("clans_menu", lang))
        await callback_query.answer()
