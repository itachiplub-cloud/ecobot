from __future__ import annotations

from motor.motor_asyncio import AsyncIOMotorDatabase

from bot.database.repositories.soft_delete_repo import SoftDeleteRepository
from bot.database.repositories.audit_log_repo import AuditLogRepository


class OwnerService:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.soft_delete_repo = SoftDeleteRepository(db)
        self.audit_repo = AuditLogRepository(db)

    async def delete_user(self, user_id: int, admin_id: int, reason: str = "") -> dict:
        return await self.soft_delete_repo.backup_and_delete(user_id, admin_id, reason)

    async def recover_user(self, user_id: int) -> dict:
        return await self.soft_delete_repo.restore_user(user_id)

    async def purge_user(self, user_id: int, admin_id: int) -> bool:
        await self.audit_repo.log_action("purge_user", admin_id, target_user_id=user_id, reason="Permanent purge")
        return await self.soft_delete_repo.purge_user(user_id)

    async def get_deleted_users(self, limit: int = 50):
        return await self.soft_delete_repo.get_deleted_users(limit)

    async def log_action(self, action: str, admin_id: int, **kwargs):
        return await self.audit_repo.log_action(action, admin_id, **kwargs)

    async def get_audit_logs(self, admin_id: int = None, action: str = None, limit: int = 100):
        return await self.audit_repo.get_logs(admin_id, action, limit)

    async def get_user_audit(self, user_id: int, limit: int = 50):
        return await self.audit_repo.get_user_audit(user_id, limit)
