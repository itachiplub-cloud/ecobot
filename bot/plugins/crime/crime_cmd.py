from __future__ import annotations

import random
from pyrogram import Client, filters
from pyrogram.types import CallbackQuery, Message

from bot.core import loc
from bot.keyboards.inline import InlineKeyboards
from bot.utils.helpers import format_number


def register(app: Client):
    @app.on_message(filters.command("crime") | filters.command("beg"))
    async def crime_command(client: Client, message: Message):
        user = message.from_user
        lang = "en"
        args = message.text.split()
        action = args[0].lstrip("/").lower()
        if message._services:
            cd_svc = message._services.get("cooldown")
            eco_svc = message._services.get("economy")
            user_svc = message._services.get("user")
            if cd_svc:
                on_cd, remaining = await cd_svc.is_on_cooldown(user.id, "crime")
                if on_cd:
                    time_str = cd_svc.format_time(remaining)
                    await message.reply_text(loc.t("cooldown.crime", lang, time=time_str))
                    return
            if eco_svc:
                await _handle_crime(action, user, eco_svc, user_svc, lang, message)
                if cd_svc:
                    await cd_svc.set_cooldown(user.id, "crime", 120)
                return
        await message.reply_text(loc.t("error.general", lang))

    @app.on_callback_query(filters.regex("^beg$"))
    async def beg_callback(client: Client, callback_query: CallbackQuery):
        user = callback_query.from_user
        lang = "en"
        if callback_query._services:
            cd_svc = callback_query._services.get("cooldown")
            eco_svc = callback_query._services.get("economy")
            if cd_svc:
                on_cd, remaining = await cd_svc.is_on_cooldown(user.id, "crime")
                if on_cd:
                    time_str = cd_svc.format_time(remaining)
                    await callback_query.answer(loc.t("cooldown.crime", lang, time=time_str), show_alert=True)
                    return
            if eco_svc:
                if random.random() < 0.5:
                    amount = random.randint(5, 50)
                    await eco_svc.add_coins(user.id, amount, "Begging")
                    await callback_query.answer(loc.t("crime.beg_success", lang, amount=format_number(amount)), show_alert=True)
                else:
                    await callback_query.answer(loc.t("crime.beg_failed", lang), show_alert=True)
                if cd_svc:
                    await cd_svc.set_cooldown(user.id, "crime", 120)
                return
        await callback_query.answer()

    @app.on_callback_query(filters.regex("^steal$"))
    async def steal_callback(client: Client, callback_query: CallbackQuery):
        user = callback_query.from_user
        lang = "en"
        if callback_query._services:
            cd_svc = callback_query._services.get("cooldown")
            eco_svc = callback_query._services.get("economy")
            if cd_svc:
                on_cd, remaining = await cd_svc.is_on_cooldown(user.id, "crime")
                if on_cd:
                    time_str = cd_svc.format_time(remaining)
                    await callback_query.answer(loc.t("cooldown.crime", lang, time=time_str), show_alert=True)
                    return
            if eco_svc:
                if random.random() < 0.4:
                    amount = random.randint(10, 100)
                    await eco_svc.add_coins(user.id, amount, "Stealing")
                    await callback_query.answer(loc.t("crime.steal_success", lang, amount=format_number(amount)), show_alert=True)
                else:
                    fine = random.randint(5, 30)
                    await eco_svc.remove_coins(user.id, fine, "Steal fine")
                    await callback_query.answer(loc.t("crime.steal_failed", lang), show_alert=True)
                if cd_svc:
                    await cd_svc.set_cooldown(user.id, "crime", 120)
                return
        await callback_query.answer()

    @app.on_callback_query(filters.regex("^rob$"))
    async def rob_callback(client: Client, callback_query: CallbackQuery):
        lang = "en"
        await callback_query.answer(loc.t("misc.not_enough", lang, resource="targets"), show_alert=True)

    @app.on_callback_query(filters.regex("^heist$"))
    async def heist_callback(client: Client, callback_query: CallbackQuery):
        user = callback_query.from_user
        lang = "en"
        if callback_query._services:
            cd_svc = callback_query._services.get("cooldown")
            eco_svc = callback_query._services.get("economy")
            if cd_svc:
                on_cd, remaining = await cd_svc.is_on_cooldown(user.id, "crime")
                if on_cd:
                    time_str = cd_svc.format_time(remaining)
                    await callback_query.answer(loc.t("cooldown.crime", lang, time=time_str), show_alert=True)
                    return
            if eco_svc:
                roll = random.random()
                if roll < 0.25:
                    amount = random.randint(200, 1000)
                    await eco_svc.add_coins(user.id, amount, "Heist")
                    await callback_query.answer(loc.t("crime.heist_success", lang, amount=format_number(amount)), show_alert=True)
                elif roll < 0.5:
                    await callback_query.answer(loc.t("crime.heist_jailed", lang), show_alert=True)
                else:
                    fine = random.randint(50, 200)
                    await eco_svc.remove_coins(user.id, fine, "Heist fine")
                    await callback_query.answer(loc.t("crime.heist_failed", lang), show_alert=True)
                if cd_svc:
                    await cd_svc.set_cooldown(user.id, "crime", 300)
                return
        await callback_query.answer()

    @app.on_callback_query(filters.regex("^hack$"))
    async def hack_callback(client: Client, callback_query: CallbackQuery):
        user = callback_query.from_user
        lang = "en"
        if callback_query._services:
            cd_svc = callback_query._services.get("cooldown")
            eco_svc = callback_query._services.get("economy")
            if cd_svc:
                on_cd, remaining = await cd_svc.is_on_cooldown(user.id, "crime")
                if on_cd:
                    time_str = cd_svc.format_time(remaining)
                    await callback_query.answer(loc.t("cooldown.crime", lang, time=time_str), show_alert=True)
                    return
            if eco_svc:
                if random.random() < 0.3:
                    amount = random.randint(100, 500)
                    await eco_svc.add_coins(user.id, amount, "Hacking")
                    await callback_query.answer(loc.t("crime.hack_success", lang, user="server", amount=format_number(amount)), show_alert=True)
                else:
                    fine = random.randint(30, 150)
                    await eco_svc.remove_coins(user.id, fine, "Hack fine")
                    await callback_query.answer(loc.t("crime.hack_failed", lang), show_alert=True)
                if cd_svc:
                    await cd_svc.set_cooldown(user.id, "crime", 180)
                return
        await callback_query.answer()

    @app.on_callback_query(filters.regex("^crime$"))
    async def crime_menu_callback(client: Client, callback_query: CallbackQuery):
        lang = "en"
        text = loc.t("crime.title", lang)
        await callback_query.message.edit_text(text, reply_markup=InlineKeyboards.crime_menu(lang))
        await callback_query.answer()


async def _handle_crime(action: str, user, eco_svc, user_svc, lang: str, message: Message):
    if action == "beg":
        if random.random() < 0.5:
            amount = random.randint(5, 50)
            await eco_svc.add_coins(user.id, amount, "Begging")
            await message.reply_text(loc.t("crime.beg_success", lang, amount=format_number(amount)))
        else:
            await message.reply_text(loc.t("crime.beg_failed", lang))
    else:
        await message.reply_text(loc.t("crime.title", lang))
