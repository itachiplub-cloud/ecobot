from __future__ import annotations

from pyrogram import Client
from pyrogram.types import Message

from bot.database import get_db
from bot.database.repositories.statistics_repo import StatisticsRepository


class StatisticsMiddleware:
    def __init__(self):
        self._repo = None

    def _get_repo(self):
        if self._repo is None:
            self._repo = StatisticsRepository(get_db())
        return self._repo

    async def __call__(self, client: Client, update):
        repo = self._get_repo()
        await repo.increment("commands_executed")
        return
