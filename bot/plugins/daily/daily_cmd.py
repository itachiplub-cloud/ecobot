from __future__ import annotations

from pyrogram import Client, filters
from pyrogram.types import CallbackQuery, Message

from bot.core import loc
from bot.keyboards.inline import InlineKeyboards
from bot.utils.helpers import format_number, seconds_to_human


def register(app: Client):
    @app.on_message(filters.command("daily"))
    async def daily_command(client: Client, message: Message):
        user = message.from_user
        lang = "en"
        if message._services:
            daily_svc = message._services.get("daily")
            eco_svc = message._services.get("economy")
            ach_svc = message._services.get("achievement")
            if daily_svc and eco_svc:
                result = await daily_svc.claim_daily(user.id)
                if result["claimed"]:
                    amount = result.get("amount", 100)
                    await eco_svc.add_coins(user.id, amount, "Daily reward")
                    if ach_svc:
                        await ach_svc.check_achievement(user.id, "daily_7")
                    streak = result.get("streak", 1)
                    bonus = result.get("streak_bonus", 0)
                    text = loc.t("daily.claimed", lang, amount=format_number(amount), streak=streak)
                    if bonus > 0:
                        text += f"\n{loc.t('daily.streak_bonus', lang, bonus=format_number(bonus))}"
                    await message.reply_text(text)
                else:
                    hours = result.get("hours", 0)
                    minutes = result.get("minutes", 0)
                    time_str = f"{hours}h {minutes}m"
                    await message.reply_text(loc.t("daily.already_claimed", lang, time=time_str))
                return
        await message.reply_text(loc.t("error.general", lang))

    @app.on_message(filters.command("weekly"))
    async def weekly_command(client: Client, message: Message):
        user = message.from_user
        lang = "en"
        if message._services:
            daily_svc = message._services.get("daily")
            eco_svc = message._services.get("economy")
            if daily_svc and eco_svc:
                result = await daily_svc.claim_weekly(user.id)
                if result["claimed"]:
                    amount = result.get("amount", 500)
                    await eco_svc.add_coins(user.id, amount, "Weekly reward")
                    await message.reply_text(loc.t("daily.weekly_claimed", lang, amount=format_number(amount)))
                else:
                    days = result.get("days", 0)
                    hours = result.get("hours", 0)
                    await message.reply_text(loc.t("daily.already_claimed", lang, time=f"{days}d {hours}h"))
                return
        await message.reply_text(loc.t("error.general", lang))

    @app.on_message(filters.command("monthly"))
    async def monthly_command(client: Client, message: Message):
        user = message.from_user
        lang = "en"
        if message._services:
            daily_svc = message._services.get("daily")
            eco_svc = message._services.get("economy")
            if daily_svc and eco_svc:
                result = await daily_svc.claim_monthly(user.id)
                if result["claimed"]:
                    amount = result.get("amount", 2000)
                    await eco_svc.add_coins(user.id, amount, "Monthly reward")
                    await message.reply_text(loc.t("daily.monthly_claimed", lang, amount=format_number(amount)))
                else:
                    days = result.get("days", 0)
                    await message.reply_text(loc.t("daily.already_claimed", lang, time=f"{days} days"))
                return
        await message.reply_text(loc.t("error.general", lang))

    @app.on_message(filters.command("yearly"))
    async def yearly_command(client: Client, message: Message):
        user = message.from_user
        lang = "en"
        if message._services:
            daily_svc = message._services.get("daily")
            eco_svc = message._services.get("economy")
            if daily_svc and eco_svc:
                result = await daily_svc.claim_yearly(user.id)
                if result["claimed"]:
                    amount = result.get("amount", 10000)
                    await eco_svc.add_coins(user.id, amount, "Yearly reward")
                    await message.reply_text(loc.t("daily.yearly_claimed", lang, amount=format_number(amount)))
                else:
                    days = result.get("days", 0)
                    await message.reply_text(loc.t("daily.already_claimed", lang, time=f"{days} days"))
                return
        await message.reply_text(loc.t("error.general", lang))
