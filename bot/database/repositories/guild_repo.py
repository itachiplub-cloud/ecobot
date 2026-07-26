from __future__ import annotations

from datetime import datetime
from typing import Optional

from motor.motor_asyncio import AsyncIOMotorDatabase

from bot.database.models.guild import GuildModel, GuildMemberModel


class GuildRepository:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.guilds = db.guilds
        self.members = db.guild_members

    async def create_guild(self, guild: GuildModel) -> GuildModel:
        await self.guilds.insert_one(guild.to_dict())
        return guild

    async def get_guild(self, guild_id: int) -> Optional[GuildModel]:
        doc = await self.guilds.find_one({"guild_id": guild_id})
        return GuildModel.from_doc(doc)

    async def get_guild_by_name(self, name: str) -> Optional[GuildModel]:
        doc = await self.guilds.find_one({"name": {"$regex": name, "$options": "i"}})
        return GuildModel.from_doc(doc)

    async def update_guild(self, guild_id: int, **update_data) -> None:
        update_data["updated_at"] = datetime.utcnow()
        await self.guilds.update_one(
            {"guild_id": guild_id},
            {"$set": update_data},
        )

    async def delete_guild(self, guild_id: int) -> None:
        await self.guilds.delete_one({"guild_id": guild_id})
        await self.members.delete_many({"guild_id": guild_id})

    async def get_all_guilds(self) -> list[GuildModel]:
        cursor = self.guilds.find({}).sort("level", -1)
        docs = await cursor.to_list(length=None)
        return [GuildModel.from_doc(d) for d in docs]

    async def add_member(self, member: GuildMemberModel) -> GuildMemberModel:
        await self.members.insert_one(member.to_dict())
        await self.guilds.update_one(
            {"guild_id": member.guild_id},
            {"$inc": {"member_count": 1}},
        )
        return member

    async def remove_member(self, guild_id: int, user_id: int) -> bool:
        result = await self.members.delete_one({"guild_id": guild_id, "user_id": user_id})
        if result.deleted_count > 0:
            await self.guilds.update_one(
                {"guild_id": guild_id},
                {"$inc": {"member_count": -1}},
            )
            return True
        return False

    async def get_member(self, guild_id: int, user_id: int) -> Optional[GuildMemberModel]:
        doc = await self.members.find_one({"guild_id": guild_id, "user_id": user_id})
        return GuildMemberModel.from_doc(doc)

    async def get_user_guild(self, user_id: int) -> Optional[GuildMemberModel]:
        doc = await self.members.find_one({"user_id": user_id})
        return GuildMemberModel.from_doc(doc)

    async def get_guild_members(self, guild_id: int) -> list[GuildMemberModel]:
        cursor = self.members.find({"guild_id": guild_id}).sort("role", 1)
        docs = await cursor.to_list(length=None)
        return [GuildMemberModel.from_doc(d) for d in docs]

    async def update_member(self, guild_id: int, user_id: int, **update_data) -> None:
        await self.members.update_one(
            {"guild_id": guild_id, "user_id": user_id},
            {"$set": update_data},
        )

    async def promote_member(self, guild_id: int, user_id: int) -> bool:
        result = await self.members.update_one(
            {"guild_id": guild_id, "user_id": user_id},
            {"$set": {"role": "officer"}},
        )
        return result.modified_count > 0

    async def demote_member(self, guild_id: int, user_id: int) -> bool:
        result = await self.members.update_one(
            {"guild_id": guild_id, "user_id": user_id},
            {"$set": {"role": "member"}},
        )
        return result.modified_count > 0

    async def add_treasury(self, guild_id: int, amount: int) -> None:
        await self.guilds.update_one(
            {"guild_id": guild_id},
            {"$inc": {"treasury": amount}},
        )

    async def get_top_guilds(self, field: str = "level", limit: int = 10) -> list[GuildModel]:
        cursor = self.guilds.find({}).sort(field, -1).limit(limit)
        docs = await cursor.to_list(length=limit)
        return [GuildModel.from_doc(d) for d in docs]

    async def guild_exists(self, name: str) -> bool:
        count = await self.guilds.count_documents({"name": {"$regex": f"^{name}$", "$options": "i"}})
        return count > 0
