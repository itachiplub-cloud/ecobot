from __future__ import annotations

from datetime import datetime
from typing import Any, Optional

from motor.motor_asyncio import AsyncIOMotorDatabase

from bot.database.models.audit_log import AuditLogModel


class AuditLogRepository:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.collection = db.audit_logs

    async def log_action(self, action: str, admin_id: int, **kwargs) -> AuditLogModel:
        log = AuditLogModel(action=action, admin_id=admin_id, **kwargs)
        await self.collection.insert_one(log.to_dict())
        return log

    async def get_logs(self, admin_id: int = None, action: str = None, limit: int = 100) -> list[AuditLogModel]:
        query = {}
        if admin_id:
            query["admin_id"] = admin_id
        if action:
            query["action"] = action
        cursor = self.collection.find(query).sort("created_at", -1).limit(limit)
        docs = await cursor.to_list(length=limit)
        return [AuditLogModel.from_doc(d) for d in docs]

    async def get_user_audit(self, target_user_id: int, limit: int = 50) -> list[AuditLogModel]:
        cursor = self.collection.find({"target_user_id": target_user_id}).sort("created_at", -1).limit(limit)
        docs = await cursor.to_list(length=limit)
        return [AuditLogModel.from_doc(d) for d in docs]

    async def get_recent(self, hours: int = 24, limit: int = 100) -> list[AuditLogModel]:
        from datetime import timedelta
        cutoff = datetime.utcnow() - timedelta(hours=hours)
        cursor = self.collection.find({"created_at": {"$gte": cutoff}}).sort("created_at", -1).limit(limit)
        docs = await cursor.to_list(length=limit)
        return [AuditLogModel.from_doc(d) for d in docs]

    async def cleanup_old(self, days: int = 90) -> int:
        from datetime import timedelta
        cutoff = datetime.utcnow() - timedelta(days=days)
        result = await self.collection.delete_many({"created_at": {"$lt": cutoff}})
        return result.deleted_count
