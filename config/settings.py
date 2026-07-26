from __future__ import annotations

import os
from pathlib import Path
from typing import List

from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")


def _int(key: str, default: int = 0) -> int:
    return int(os.getenv(key, str(default)))


def _float(key: str, default: float = 0.0) -> float:
    return float(os.getenv(key, str(default)))


def _str(key: str, default: str = "") -> str:
    return os.getenv(key, default)


def _bool(key: str, default: bool = False) -> bool:
    return os.getenv(key, str(default)).lower() in ("true", "1", "yes")


def _list(key: str, default: List[int] | None = None) -> List[int]:
    raw = os.getenv(key, "")
    if not raw:
        return default or []
    return [int(x.strip()) for x in raw.split(",") if x.strip().isdigit()]


class Settings:
    APP_NAME: str = _str("APP_NAME", "TelegramEconomyRPG")
    APP_ENV: str = _str("APP_ENV", "production")
    DEBUG: bool = _bool("DEBUG", False)

    API_ID: int = _int("API_ID")
    API_HASH: str = _str("API_HASH")
    BOT_TOKEN: str = _str("BOT_TOKEN")

    MONGO_URI: str = _str("MONGO_URI", "mongodb://localhost:27017")
    MONGO_DB_NAME: str = _str("MONGO_DB_NAME", "economy_rpg_bot")

    OWNER_ID: int = _int("OWNER_ID")

    DEFAULT_BALANCE: int = _int("DEFAULT_BALANCE", 500)
    TAX_RATE: float = _float("TAX_RATE", 0.05)
    BANK_INTEREST_RATE: float = _float("BANK_INTEREST_RATE", 0.02)
    DAILY_REWARD: int = _int("DAILY_REWARD", 100)

    SPAM_LIMIT: int = _int("SPAM_LIMIT", 3)
    FLOOD_LIMIT: int = _int("FLOOD_LIMIT", 5)
    COOLDOWN_SECONDS: int = _int("COOLDOWN_SECONDS", 5)

    LOG_LEVEL: str = _str("LOG_LEVEL", "INFO")
    LOG_FILE: str = _str("LOG_FILE", "logs/bot.log")
