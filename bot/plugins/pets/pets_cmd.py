from __future__ import annotations

from pyrogram import Client, filters
from pyrogram.types import CallbackQuery, Message

from bot.core import loc
from bot.keyboards.inline import InlineKeyboards
from bot.utils.formatting import format_pet


def register(app: Client):
    @app.on_message(filters.command("pets") | filters.command("pet"))
    async def pets_command(client: Client, message: Message):
        user = message.from_user
        lang = "en"
        if message._services:
            pet_svc = message._services.get("pet")
            if pet_svc:
                pets = await pet_svc.get_user_pets(user.id)
                if pets:
                    text = loc.t("pet.list", lang) + "\n\n"
                    for p in pets[:10]:
                        text += format_pet(p, lang) + "\n\n"
                else:
                    text = loc.t("pet.none", lang)
                await message.reply_text(text, reply_markup=InlineKeyboards.pets_menu(lang))
                return
        await message.reply_text(loc.t("error.general", lang))

    @app.on_callback_query(filters.regex("^pets_menu$"))
    async def pets_menu_callback(client: Client, callback_query: CallbackQuery):
        user = callback_query.from_user
        lang = "en"
        if callback_query._services:
            pet_svc = callback_query._services.get("pet")
            if pet_svc:
                equipped = await pet_svc.get_equipped_pet(user.id)
                text = loc.t("pet.title", lang)
                if equipped:
                    text += f"\n\n{loc.t('pet.equipped', lang, name=equipped.name)}"
                try:
                    await callback_query.message.edit_text(text, reply_markup=InlineKeyboards.pets_menu(lang))
                except Exception:
                    await callback_query.message.reply_text(text, reply_markup=InlineKeyboards.pets_menu(lang))
        await callback_query.answer()

    @app.on_callback_query(filters.regex("^pet_list$"))
    async def pet_list_callback(client: Client, callback_query: CallbackQuery):
        user = callback_query.from_user
        lang = "en"
        if callback_query._services:
            pet_svc = callback_query._services.get("pet")
            if pet_svc:
                pets = await pet_svc.get_user_pets(user.id)
                if pets:
                    text = loc.t("pet.list", lang) + "\n\n"
                    for p in pets:
                        text += format_pet(p, lang) + "\n\n"
                else:
                    text = loc.t("pet.none", lang)
                try:
                    await callback_query.message.edit_text(text, reply_markup=InlineKeyboards.pets_menu(lang))
                except Exception:
                    await callback_query.message.reply_text(text, reply_markup=InlineKeyboards.pets_menu(lang))
        await callback_query.answer()

    @app.on_callback_query(filters.regex("^pet_feed$"))
    async def pet_feed_callback(client: Client, callback_query: CallbackQuery):
        user = callback_query.from_user
        lang = "en"
        if callback_query._services:
            pet_svc = callback_query._services.get("pet")
            if pet_svc:
                equipped = await pet_svc.get_equipped_pet(user.id)
                if equipped:
                    await pet_svc.feed_pet(user.id, equipped.pet_id)
                    await callback_query.answer(loc.t("pet.feed_success", lang, name=equipped.name, hunger=min(100, equipped.hunger + 20)), show_alert=True)
                else:
                    await callback_query.answer(loc.t("pet.none", lang), show_alert=True)
        else:
            await callback_query.answer()

    @app.on_callback_query(filters.regex("^pet_play$"))
    async def pet_play_callback(client: Client, callback_query: CallbackQuery):
        user = callback_query.from_user
        lang = "en"
        if callback_query._services:
            pet_svc = callback_query._services.get("pet")
            if pet_svc:
                equipped = await pet_svc.get_equipped_pet(user.id)
                if equipped:
                    await pet_svc.play_pet(user.id, equipped.pet_id)
                    await callback_query.answer(loc.t("pet.play_success", lang, name=equipped.name, happiness=min(100, equipped.happiness + 20)), show_alert=True)
                else:
                    await callback_query.answer(loc.t("pet.none", lang), show_alert=True)
        else:
            await callback_query.answer()

    @app.on_callback_query(filters.regex("^pet_equip$"))
    async def pet_equip_callback(client: Client, callback_query: CallbackQuery):
        lang = "en"
        await callback_query.message.edit_text(
            "🐾 Reply with: /pet_equip <pet_id>",
            reply_markup=InlineKeyboards.back_button("pets_menu", lang),
        )
        await callback_query.answer()

    @app.on_message(filters.command("pet_equip"))
    async def pet_equip_command(client: Client, message: Message):
        args = message.text.split()
        if len(args) < 2:
            await message.reply_text("Usage: /pet_equip <pet_id>")
            return
        pet_id = args[1]
        if message._services:
            pet_svc = message._services.get("pet")
            if pet_svc:
                success = await pet_svc.equip_pet(message.from_user.id, pet_id)
                if success:
                    await message.reply_text(loc.t("pet.equip_success", "en", name=pet_id))
                else:
                    await message.reply_text(loc.t("error.general", "en"))

    @app.on_callback_query(filters.regex("^pet_evolve$"))
    async def pet_evolve_callback(client: Client, callback_query: CallbackQuery):
        user = callback_query.from_user
        lang = "en"
        if callback_query._services:
            pet_svc = callback_query._services.get("pet")
            if pet_svc:
                equipped = await pet_svc.get_equipped_pet(user.id)
                if equipped:
                    success = await pet_svc.evolve_pet(user.id, equipped.pet_id)
                    if success:
                        await callback_query.answer(loc.t("pet.evolve_success", lang, name=equipped.name, stage=equipped.evolution_level + 1), show_alert=True)
                    else:
                        await callback_query.answer(loc.t("pet.evolve_max", lang), show_alert=True)
                else:
                    await callback_query.answer(loc.t("pet.none", lang), show_alert=True)
        else:
            await callback_query.answer()
