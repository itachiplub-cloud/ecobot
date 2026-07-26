from __future__ import annotations

from pyrogram import Client, filters
from pyrogram.types import CallbackQuery, Message

from bot.core import loc
from bot.keyboards.inline import InlineKeyboards


def register(app: Client):
    @app.on_message(filters.command("equip"))
    async def equip_command(client: Client, message: Message):
        args = message.text.split()
        if len(args) < 2:
            await message.reply_text("Usage: /equip <item_id>")
            return
        item_id = args[1]
        if message._services:
            inv_svc = message._services.get("inventory")
            if inv_svc:
                success = await inv_svc.equip_item(message.from_user.id, item_id, "weapon")
                if success:
                    await message.reply_text(loc.t("rpg.equip_success", "en", item=item_id))
                else:
                    await message.reply_text(loc.t("error.general", "en"))

    @app.on_message(filters.command("unequip"))
    async def unequip_command(client: Client, message: Message):
        args = message.text.split()
        if len(args) < 2:
            await message.reply_text("Usage: /unequip <item_id>")
            return
        item_id = args[1]
        if message._services:
            inv_svc = message._services.get("inventory")
            if inv_svc:
                success = await inv_svc.unequip_item(message.from_user.id, item_id)
                if success:
                    await message.reply_text(loc.t("rpg.unequip_success", "en", item=item_id))
                else:
                    await message.reply_text(loc.t("error.general", "en"))

    @app.on_callback_query(filters.regex("^equipment$"))
    async def equipment_callback(client: Client, callback_query: CallbackQuery):
        user = callback_query.from_user
        lang = "en"
        if callback_query._services:
            inv_svc = callback_query._services.get("inventory")
            if inv_svc:
                equipped = await inv_svc.get_equipped(user.id)
                if equipped:
                    text = loc.t("rpg.equipment_title", lang) + "\n\n"
                    for item in equipped:
                        text += f"  ⚔️ {item.item_id} (x{item.quantity})\n"
                else:
                    text = loc.t("rpg.no_equipped", lang)
                try:
                    await callback_query.message.edit_text(text, reply_markup=InlineKeyboards.back_button("rpg_menu", lang))
                except Exception:
                    await callback_query.message.reply_text(text, reply_markup=InlineKeyboards.back_button("rpg_menu", lang))
        await callback_query.answer()
