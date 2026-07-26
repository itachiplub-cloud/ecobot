from __future__ import annotations

from datetime import datetime
from typing import Optional

from motor.motor_asyncio import AsyncIOMotorDatabase

from bot.database.models.mail import MailModel


class MailRepository:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.collection = db.mail

    async def send_mail(self, mail: MailModel) -> MailModel:
        await self.collection.insert_one(mail.to_dict())
        return mail

    async def get_mail(self, user_id: int, limit: int = 50) -> list[MailModel]:
        cursor = self.collection.find({"recipient_id": user_id}).sort("created_at", -1).limit(limit)
        docs = await cursor.to_list(length=limit)
        return [MailModel.from_doc(d) for d in docs]

    async def get_unread_count(self, user_id: int) -> int:
        return await self.collection.count_documents({"recipient_id": user_id, "read": False})

    async def mark_read(self, user_id: int, mail_id: Optional[str] = None) -> None:
        query = {"recipient_id": user_id, "read": False}
        if mail_id:
            from bson import ObjectId
            query["_id"] = ObjectId(mail_id)
        await self.collection.update_many(query, {"$set": {"read": True}})

    async def delete_mail(self, user_id: int, mail_id: Optional[str] = None) -> None:
        query = {"recipient_id": user_id}
        if mail_id:
            from bson import ObjectId
            query["_id"] = ObjectId(mail_id)
            await self.collection.delete_one(query)
        else:
            await self.collection.delete_many(query)

    async def send_system_mail(self, user_id: int, subject: str, body: str, **kwargs) -> MailModel:
        mail = MailModel(
            recipient_id=user_id,
            sender_name="System",
            subject=subject,
            body=body,
            **kwargs,
        )
        return await self.send_mail(mail)

    async def send_bulk_mail(self, user_ids: list[int], subject: str, body: str) -> int:
        mails = [
            MailModel(recipient_id=uid, sender_name="System", subject=subject, body=body).to_dict()
            for uid in user_ids
        ]
        if mails:
            result = await self.collection.insert_many(mails)
            return len(result.inserted_ids)
        return 0
