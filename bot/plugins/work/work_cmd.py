from __future__ import annotations

import random
from pyrogram import Client, filters
from pyrogram.types import CallbackQuery, Message

from bot.core import loc
from bot.keyboards.inline import InlineKeyboards
from bot.utils.helpers import format_number

JOBS = {
    "police": {"name": "Police Officer", "min_earn": 50, "max_earn": 200, "fail_chance": 0.1},
    "doctor": {"name": "Doctor", "min_earn": 100, "max_earn": 400, "fail_chance": 0.05},
    "programmer": {"name": "Programmer", "min_earn": 80, "max_earn": 350, "fail_chance": 0.15},
    "chef": {"name": "Chef", "min_earn": 40, "max_earn": 180, "fail_chance": 0.1},
    "pilot": {"name": "Pilot", "min_earn": 150, "max_earn": 600, "fail_chance": 0.2},
    "teacher": {"name": "Teacher", "min_earn": 60, "max_earn": 250, "fail_chance": 0.05},
    "businessman": {"name": "Businessman", "min_earn": 120, "max_earn": 500, "fail_chance": 0.25},
    "streamer": {"name": "Streamer", "min_earn": 30, "max_earn": 800, "fail_chance": 0.3},
    "developer": {"name": "Developer", "min_earn": 90, "max_earn": 400, "fail_chance": 0.1},
}


def register(app: Client):
    @app.on_message(filters.command("work"))
    async def work_command(client: Client, message: Message):
        user = message.from_user
        lang = "en"
        if message._services:
            cd_svc = message._services.get("cooldown")
            eco_svc = message._services.get("economy")
            user_svc = message._services.get("user")
            ach_svc = message._services.get("achievement")
            if cd_svc:
                on_cd, remaining = await cd_svc.is_on_cooldown(user.id, "work")
                if on_cd:
                    time_str = cd_svc.format_time(remaining)
                    await message.reply_text(loc.t("cooldown.work", lang, time=time_str))
                    return
            if eco_svc:
                job = random.choice(list(JOBS.keys()))
                job_data = JOBS[job]
                if random.random() < job_data["fail_chance"]:
                    await message.reply_text(loc.t("work.failed", lang))
                else:
                    amount = random.randint(job_data["min_earn"], job_data["max_earn"])
                    await eco_svc.add_coins(user.id, amount, f"Work: {job_data['name']}")
                    if user_svc:
                        await user_svc.increment_field(user.id, "commands_used")
                    if ach_svc:
                        await ach_svc.check_achievement(user.id, "first_work")
                    text = loc.t("work.success", lang, job=job_data["name"], amount=format_number(amount))
                    await message.reply_text(text)
                if cd_svc:
                    await cd_svc.set_cooldown(user.id, "work", 300)
                return
        await message.reply_text(loc.t("error.general", lang))

    @app.on_message(filters.command("jobs"))
    async def jobs_command(client: Client, message: Message):
        lang = "en"
        text = loc.t("work.title", lang) + "\n\n"
        for job_id, job_data in JOBS.items():
            text += f"💼 {job_data['name']}: {format_number(job_data['min_earn'])}-{format_number(job_data['max_earn'])} coins\n"
        await message.reply_text(text)

    @app.on_callback_query(filters.regex("^work$"))
    async def work_callback(client: Client, callback_query: CallbackQuery):
        user = callback_query.from_user
        lang = "en"
        if callback_query._services:
            cd_svc = callback_query._services.get("cooldown")
            eco_svc = callback_query._services.get("economy")
            user_svc = callback_query._services.get("user")
            ach_svc = callback_query._services.get("achievement")
            if cd_svc:
                on_cd, remaining = await cd_svc.is_on_cooldown(user.id, "work")
                if on_cd:
                    time_str = cd_svc.format_time(remaining)
                    await callback_query.answer(loc.t("cooldown.work", lang, time=time_str), show_alert=True)
                    return
            if eco_svc:
                job = random.choice(list(JOBS.keys()))
                job_data = JOBS[job]
                if random.random() < job_data["fail_chance"]:
                    await callback_query.answer(loc.t("work.failed", lang), show_alert=True)
                else:
                    amount = random.randint(job_data["min_earn"], job_data["max_earn"])
                    await eco_svc.add_coins(user.id, amount, f"Work: {job_data['name']}")
                    if ach_svc:
                        await ach_svc.check_achievement(user.id, "first_work")
                    await callback_query.answer(loc.t("work.success", lang, job=job_data["name"], amount=format_number(amount)), show_alert=True)
                if cd_svc:
                    await cd_svc.set_cooldown(user.id, "work", 300)
                return
        await callback_query.answer()

    @app.on_callback_query(filters.regex("^jobs_list$"))
    async def jobs_list_callback(client: Client, callback_query: CallbackQuery):
        lang = "en"
        text = loc.t("work.title", lang) + "\n\n"
        for job_id, job_data in JOBS.items():
            text += f"💼 {job_data['name']}: {format_number(job_data['min_earn'])}-{format_number(job_data['max_earn'])} coins\n"
        await callback_query.message.edit_text(text, reply_markup=InlineKeyboards.back_button("main_menu", lang))
        await callback_query.answer()
