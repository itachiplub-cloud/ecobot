from __future__ import annotations

from motor.motor_asyncio import AsyncIOMotorDatabase

from bot.database.repositories.log_repo import LogRepository
from bot.database.models.log import LogModel


class LogService:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.log_repo = LogRepository(db)

    async def log(self, level: str, message: str, user_id: int = None, command: str = None, error: str = None) -> LogModel:
        log_entry = LogModel(level=level, message=message, user_id=user_id, command=command, error=error)
        return await self.log_repo.add_log(log_entry)

    async def info(self, message: str, **kwargs) -> LogModel:
        return await self.log("INFO", message, **kwargs)

    async def warning(self, message: str, **kwargs) -> LogModel:
        return await self.log("WARNING", message, **kwargs)

    async def error(self, message: str, **kwargs) -> LogModel:
        return await self.log("ERROR", message, **kwargs)

    async def get_logs(self, level: str = None, limit: int = 100):
        return await self.log_repo.get_logs(level, limit)

    async def get_user_logs(self, user_id: int, limit: int = 50):
        return await self.log_repo.get_user_logs(user_id, limit)

    async def cleanup(self, days: int = 30) -> int:
        return await self.log_repo.cleanup_old(days)

    async def count_errors(self, hours: int = 24) -> int:
        return await self.log_repo.count_errors(hours)
