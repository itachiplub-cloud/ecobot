from __future__ import annotations

from pyrogram import Client, filters
from pyrogram.types import Message, CallbackQuery

from bot.core import loc
from bot.keyboards.inline import InlineKeyboards
from bot.utils.helpers import format_number

TIER_REWARDS = {
    1: 100, 2: 200, 3: 500, 4: 750, 5: 1000,
    6: 1500, 7: 2000, 8: 3000, 9: 4000, 10: 5000,
}
PREMIUM_MULTIPLIER = 2
SEASON_NUMBER = 1


def register(app: Client):

    @app.on_message(filters.command("gamepass"))
    async def gamepass_command(client: Client, message: Message):
        services = getattr(message, '_services', None)
        if not services:
            return
        bp_svc = services.get("battle_pass")
        eco_svc = services.get("economy")
        if not bp_svc:
            return
        bp = await bp_svc.get_battle_pass(message.from_user.id, SEASON_NUMBER)
        xp_for_next = (bp.tier * 500) + 500
        progress = min(bp.xp / xp_for_next * 100, 100) if xp_for_next > 0 else 0
        bar = "█" * int(progress / 10) + "░" * (10 - int(progress / 10))
        text = (
            f"🎫 **Game Pass** — Season {SEASON_NUMBER}\n\n"
            f"⭐ Tier: **{bp.tier}**\n"
            f"📊 XP: {bp.xp}/{xp_for_next}\n"
            f"Progress: [{bar}] {progress:.0f}%\n"
        )
        if bp.is_premium:
            text += "👑 Premium Pass Active!\n"
        else:
            text += "🆓 Free Pass\n"

        text += "\n📋 **Missions:**\n"
        for m in bp.daily_missions:
            status = "✅" if m["completed"] else "⬜"
            text += f"  {status} {m['name']}: {m['progress']}/{m['required']}\n"

        text += "\n🎁 **Tier Rewards:**\n"
        for t in range(1, min(bp.tier + 3, 11)):
            reward = TIER_REWARDS.get(t, 0)
            claimed = t in (bp.claimed_rewards or [])
            claimed_str = "✅" if claimed else "⬜"
            prem = " 👑" if bp.is_premium else ""
            text += f"  {claimed_str} Tier {t}: {format_number(reward)} coins{prem}\n"

        kb = InlineKeyboards.game_pass_keyboard(bp.tier, bp.is_premium)
        await message.reply_text(text, reply_markup=kb)

    @app.on_callback_query(filters.regex(r"^gamepass_claim_(\d+)$"))
    async def gamepass_claim_callback(client: Client, callback: CallbackQuery):
        tier = int(callback.data.split("_")[-1])
        services = getattr(callback, '_services', None) or getattr(callback.message, '_services', None)
        if not services:
            return
        bp_svc = services.get("battle_pass")
        eco_svc = services.get("economy")
        if bp_svc and eco_svc:
            bp = await bp_svc.get_battle_pass(callback.from_user.id, SEASON_NUMBER)
            if bp.tier >= tier and tier not in (bp.claimed_rewards or []):
                reward = TIER_REWARDS.get(tier, 0)
                await bp_svc.claim_reward(callback.from_user.id, tier, SEASON_NUMBER)
                await eco_svc.add_coins(callback.from_user.id, reward, f"Game Pass tier {tier}")
                await callback.answer(f"✅ Claimed tier {tier} reward: {reward} coins!")
            else:
                await callback.answer("❌ Cannot claim this tier.", show_alert=True)

    @app.on_callback_query(filters.regex(r"^gamepass_premium$"))
    async def gamepass_premium_callback(client: Client, callback: CallbackQuery):
        services = getattr(callback, '_services', None) or getattr(callback.message, '_services', None)
        if not services:
            return
        bp_svc = services.get("battle_pass")
        eco_svc = services.get("economy")
        if bp_svc and eco_svc:
            premium_cost = 10000
            balance = await eco_svc.get_balance(callback.from_user.id)
            if balance["wallet"] < premium_cost:
                await callback.answer(f"❌ Need {format_number(premium_cost)} coins.", show_alert=True)
                return
            await eco_svc.remove_coins(callback.from_user.id, premium_cost, "Game Pass Premium")
            await bp_svc.upgrade_premium(callback.from_user.id, SEASON_NUMBER)
            await callback.answer("✅ Premium Pass activated!")
            await callback.message.edit_text("✅ **Premium Pass activated!** You now earn double rewards from all tiers.")
