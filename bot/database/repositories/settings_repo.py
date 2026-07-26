from __future__ import annotations

from typing import Any, Optional

from motor.motor_asyncio import AsyncIOMotorDatabase

from bot.database.models.settings import BotSettingsModel


class SettingsRepository:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.collection = db.settings

    async def get_setting(self, key: str) -> Any:
        doc = await self.collection.find_one({"key": key})
        if doc:
            return doc.get("value")
        return None

    async def set_setting(self, key: str, value: Any, updated_by: Optional[int] = None) -> None:
        await self.collection.update_one(
            {"key": key},
            {"$set": {"value": value, "updated_by": updated_by}},
            upsert=True,
        )

    async def get_all_settings(self) -> dict:
        cursor = self.collection.find({})
        docs = await cursor.to_list(length=None)
        return {d["key"]: d.get("value") for d in docs}

    async def delete_setting(self, key: str) -> None:
        await self.collection.delete_one({"key": key})

    async def get_or_default(self, key: str, default: Any = None) -> Any:
        val = await self.get_setting(key)
        return val if val is not None else default
