from __future__ import annotations

from motor.motor_asyncio import AsyncIOMotorDatabase

from bot.database.repositories.admin_repo import AdminRepository
from bot.database.models.admin import AdminModel


class AdminService:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.admin_repo = AdminRepository(db)

    async def is_sudo(self, user_id: int) -> bool:
        from config import settings
        if user_id == settings.OWNER_ID:
            return True
        admin = await self.admin_repo.get_admin(user_id)
        return admin is not None and admin.role == "sudo"

    async def is_admin(self, user_id: int) -> bool:
        from config import settings
        if user_id == settings.OWNER_ID:
            return True
        return await self.admin_repo.is_admin(user_id)

    async def add_sudo(self, user_id: int, added_by: int) -> AdminModel:
        return await self.admin_repo.set_sudo(user_id, added_by)

    async def remove_sudo(self, user_id: int) -> bool:
        return await self.admin_repo.remove_admin(user_id)

    async def get_all_admins(self):
        return await self.admin_repo.get_all_admins()

    async def get_admin(self, user_id: int):
        return await self.admin_repo.get_admin(user_id)
