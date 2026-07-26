from __future__ import annotations

import random
import time
from typing import Any


def generate_id(length: int = 8) -> str:
    import string
    return "".join(random.choices(string.ascii_uppercase + string.digits, k=length))


def clamp(value: int, min_val: int, max_val: int) -> int:
    return max(min_val, min(value, max_val))


def percentage(part: int, whole: int) -> float:
    if whole == 0:
        return 0.0
    return (part / whole) * 100


def xp_for_level(level: int) -> int:
    return int(100 * (1.5 ** (level - 1)))


def calc_damage(attacker_atk: int, defender_def: int, luck: int = 0) -> int:
    base = max(1, attacker_atk - defender_def // 2)
    crit_mult = 2.0 if random.randint(1, 100) <= luck else 1.0
    variance = random.uniform(0.85, 1.15)
    return max(1, int(base * crit_mult * variance))


def calc_drop_rate(base_rate: float, luck: int = 0) -> bool:
    adjusted = base_rate + (luck * 0.001)
    return random.random() < min(adjusted, 1.0)


def format_number(n: int) -> str:
    if n >= 1_000_000_000:
        return f"{n / 1_000_000_000:.1f}B"
    if n >= 1_000_000:
        return f"{n / 1_000_000:.1f}M"
    if n >= 1_000:
        return f"{n / 1_000:.1f}K"
    return str(n)


def timestamp_now() -> int:
    return int(time.time())


def seconds_to_human(seconds: int) -> str:
    days = seconds // 86400
    hours = (seconds % 86400) // 3600
    minutes = (seconds % 3600) // 60
    secs = seconds % 60
    parts = []
    if days:
        parts.append(f"{days}d")
    if hours:
        parts.append(f"{hours}h")
    if minutes:
        parts.append(f"{minutes}m")
    if secs or not parts:
        parts.append(f"{secs}s")
    return " ".join(parts)


def progress_bar(current: int, maximum: int, length: int = 10) -> str:
    filled = int(length * current / maximum) if maximum > 0 else 0
    filled = min(filled, length)
    return "█" * filled + "░" * (length - filled)


def escape_html(text: str) -> str:
    return text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


RARITY_COLORS = {
    "common": "⚪",
    "uncommon": "🟢",
    "rare": "🔵",
    "epic": "🟣",
    "legendary": "🟠",
    "mythic": "🔴",
    "divine": "✨",
}


def rarity_emoji(rarity: str) -> str:
    return RARITY_COLORS.get(rarity.lower(), "⚪")
