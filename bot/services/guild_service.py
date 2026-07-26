from __future__ import annotations

from motor.motor_asyncio import AsyncIOMotorDatabase

from bot.database.repositories.guild_repo import GuildRepository
from bot.database.models.guild import GuildModel, GuildMemberModel


class GuildService:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.guild_repo = GuildRepository(db)

    async def create_guild(self, user_id: int, name: str, tag: str) -> dict:
        member = await self.guild_repo.get_user_guild(user_id)
        if member:
            return {"success": False, "reason": "already_in_guild"}
        if await self.guild_repo.guild_exists(name):
            return {"success": False, "reason": "name_taken"}
        import random
        guild_id = random.randint(100000, 999999)
        guild = GuildModel(guild_id=guild_id, name=name, tag=tag, owner_id=user_id)
        await self.guild_repo.create_guild(guild)
        member = GuildMemberModel(guild_id=guild_id, user_id=user_id, role="leader")
        await self.guild_repo.add_member(member)
        return {"success": True, "guild_id": guild_id}

    async def get_guild(self, guild_id: int):
        return await self.guild_repo.get_guild(guild_id)

    async def get_user_guild(self, user_id: int):
        return await self.guild_repo.get_user_guild(user_id)

    async def join_guild(self, user_id: int, guild_id: int) -> dict:
        member = await self.guild_repo.get_user_guild(user_id)
        if member:
            return {"success": False, "reason": "already_in_guild"}
        guild = await self.guild_repo.get_guild(guild_id)
        if not guild:
            return {"success": False, "reason": "guild_not_found"}
        if guild.member_count >= guild.max_members:
            return {"success": False, "reason": "guild_full"}
        new_member = GuildMemberModel(guild_id=guild_id, user_id=user_id)
        await self.guild_repo.add_member(new_member)
        return {"success": True}

    async def leave_guild(self, user_id: int) -> dict:
        member = await self.guild_repo.get_user_guild(user_id)
        if not member:
            return {"success": False, "reason": "not_in_guild"}
        if member.role == "leader":
            return {"success": False, "reason": "owner_cannot_leave"}
        await self.guild_repo.remove_member(member.guild_id, user_id)
        return {"success": True}

    async def disband_guild(self, user_id: int, guild_id: int) -> dict:
        guild = await self.guild_repo.get_guild(guild_id)
        if not guild or guild.owner_id != user_id:
            return {"success": False, "reason": "not_owner"}
        await self.guild_repo.delete_guild(guild_id)
        return {"success": True}

    async def deposit_guild(self, user_id: int, amount: int) -> dict:
        member = await self.guild_repo.get_user_guild(user_id)
        if not member:
            return {"success": False, "reason": "not_in_guild"}
        await self.guild_repo.add_treasury(member.guild_id, amount)
        await self.guild_repo.update_member(member.guild_id, user_id, contribution=member.contribution + amount)
        return {"success": True}

    async def get_guild_members(self, guild_id: int):
        return await self.guild_repo.get_guild_members(guild_id)

    async def promote_member(self, guild_id: int, user_id: int) -> bool:
        return await self.guild_repo.promote_member(guild_id, user_id)

    async def demote_member(self, guild_id: int, user_id: int) -> bool:
        return await self.guild_repo.demote_member(guild_id, user_id)

    async def get_top_guilds(self, field: str = "level", limit: int = 10):
        return await self.guild_repo.get_top_guilds(field, limit)
