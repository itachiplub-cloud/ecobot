from __future__ import annotations

from motor.motor_asyncio import AsyncIOMotorDatabase

from bot.database.repositories.mail_repo import MailRepository
from bot.database.models.mail import MailModel


class MailService:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.mail_repo = MailRepository(db)

    async def get_mail(self, user_id: int, limit: int = 50):
        return await self.mail_repo.get_mail(user_id, limit)

    async def get_unread_count(self, user_id: int) -> int:
        return await self.mail_repo.get_unread_count(user_id)

    async def mark_read(self, user_id: int, mail_id: str = None) -> None:
        await self.mail_repo.mark_read(user_id, mail_id)

    async def delete_mail(self, user_id: int, mail_id: str = None) -> None:
        await self.mail_repo.delete_mail(user_id, mail_id)

    async def send_system_mail(self, user_id: int, subject: str, body: str, **kwargs) -> MailModel:
        return await self.mail_repo.send_system_mail(user_id, subject, body, **kwargs)

    async def send_bulk_mail(self, user_ids: list[int], subject: str, body: str) -> int:
        return await self.mail_repo.send_bulk_mail(user_ids, subject, body)
