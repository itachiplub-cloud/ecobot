from __future__ import annotations

from bot.core import loc
from bot.utils.helpers import format_number, progress_bar, rarity_emoji


def format_balance(wallet: int, bank: int, lang: str = "en") -> str:
    return (
        f"💰 {loc.t('economy.wallet', lang)}: {format_number(wallet)}\n"
        f"🏦 {loc.t('economy.bank', lang)}: {format_number(bank)}\n"
        f"💎 {loc.t('economy.total', lang)}: {format_number(wallet + bank)}"
    )


def format_user_profile(user, economy=None, lang: str = "en") -> str:
    lines = [
        f"👤 {loc.t('profile.user', lang)}: {user.first_name or 'Unknown'}",
        f"🆔 ID: `{user.user_id}`",
        f"⭐ {loc.t('profile.level', lang)}: {user.level}",
        f"📊 {loc.t('profile.xp', lang)}: {progress_bar(user.xp, user.xp_needed)} {user.xp}/{user.xp_needed}",
        f"🏆 {loc.t('profile.title', lang)}: {user.title}",
    ]
    if user.bio:
        lines.append(f"📝 {user.bio}")
    if economy:
        lines.append(f"\n{format_balance(economy.wallet, economy.bank, lang)}")
    stats = user.stats
    lines.append(
        f"\n⚔️ {loc.t('stats.strength', lang)}: {stats.get('strength', 0)} | "
        f"🛡️ {loc.t('stats.defense', lang)}: {stats.get('defense', 0)}\n"
        f"🍀 {loc.t('stats.luck', lang)}: {stats.get('luck', 0)} | "
        f"💨 {loc.t('stats.speed', lang)}: {stats.get('speed', 0)}\n"
        f"💥 {loc.t('stats.critical', lang)}: {stats.get('critical', 0)}"
    )
    if user.guild_id:
        lines.append(f"\n🏰 {loc.t('profile.guild', lang)}: {user.guild_id}")
    lines.append(f"\n📅 {loc.t('profile.joined', lang)}: {user.joined_at.strftime('%Y-%m-%d')}")
    return "\n".join(lines)


def format_item(item, quantity: int = 1, lang: str = "en") -> str:
    return (
        f"{item.emoji} **{item.name}** {rarity_emoji(item.rarity)}\n"
        f"📝 {item.description}\n"
        f"💰 {loc.t('shop.price', lang)}: {format_number(item.price)} | "
        f"x{quantity}"
    )


def format_pet(pet, lang: str = "en") -> str:
    return (
        f"🐾 **{pet.name}** (Lvl {pet.level})\n"
        f"❤️ HP: {pet.health} | 😊 Happy: {pet.happiness} | 🍖 Hunger: {pet.hunger}\n"
        f"⚔️ ATK: {pet.attack} | 🛡️ DEF: {pet.defense} | 💨 SPD: {pet.speed}\n"
        f"⭐ Evolution: {pet.evolution_level}/{pet.max_evolution}"
    )


def format_guild(guild, lang: str = "en") -> str:
    return (
        f"🏰 **{guild.name}** [{guild.tag}]\n"
        f"⭐ {loc.t('guild.level', lang)}: {guild.level}\n"
        f"👥 {loc.t('guild.members', lang)}: {guild.member_count}/{guild.max_members}\n"
        f"💰 {loc.t('guild.treasury', lang)}: {format_number(guild.treasury)}\n"
        f"⚔️ {loc.t('guild.wars', lang)}: {guild.war_wins}W / {guild.war_losses}L"
    )


def format_quest(quest, lang: str = "en") -> str:
    objectives = ""
    for obj in quest.objectives:
        current = quest.progress.get(obj["id"], 0)
        target = obj["target"]
        objectives += f"  • {obj.get('id', '')}: {progress_bar(current, target)} {current}/{target}\n"
    status = "✅" if quest.completed else "⏳"
    return (
        f"{status} **{quest.title}**\n"
        f"📝 {quest.description}\n"
        f"{objectives}"
        f"🎁 {loc.t('quest.reward', lang)}: {format_number(quest.reward_coins)} coins, {quest.reward_xp} XP"
    )


def format_leaderboard(entries: list, category: str, lang: str = "en") -> str:
    medals = ["🥇", "🥈", "🥉"]
    lines = [f"🏆 **{loc.t(f'leaderboard.{category}', lang)}**\n"]
    for i, entry in enumerate(entries):
        medal = medals[i] if i < 3 else f"#{i + 1}"
        lines.append(f"{medal} User `{entry.user_id}` - Score: {format_number(entry.score)}")
    return "\n".join(lines)
