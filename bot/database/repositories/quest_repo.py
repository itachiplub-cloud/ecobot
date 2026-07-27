from __future__ import annotations

from datetime import datetime, timezone
from typing import Optional

from motor.motor_asyncio import AsyncIOMotorDatabase

from bot.database.models.quest import QuestModel


class QuestRepository:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.collection = db.quests

    async def add_quest(self, quest: QuestModel) -> QuestModel:
        await self.collection.insert_one(quest.to_dict())
        return quest

    async def get_quest(self, user_id: int, quest_id: str) -> Optional[QuestModel]:
        doc = await self.collection.find_one({"user_id": user_id, "quest_id": quest_id})
        return QuestModel.from_doc(doc)

    async def get_user_quests(self, user_id: int, quest_type: Optional[str] = None) -> list[QuestModel]:
        query = {"user_id": user_id, "completed": False}
        if quest_type:
            query["quest_type"] = quest_type
        cursor = self.collection.find(query)
        docs = await cursor.to_list(length=None)
        return [QuestModel.from_doc(d) for d in docs]

    async def update_quest_progress(self, user_id: int, quest_id: str, objective: str, amount: int = 1) -> dict:
        quest = await self.get_quest(user_id, quest_id)
        if not quest or quest.completed:
            return {"completed": False, "objective_completed": False}
        current = quest.progress.get(objective, 0)
        new_val = current + amount
        await self.collection.update_one(
            {"user_id": user_id, "quest_id": quest_id},
            {"$set": {f"progress.{objective}": new_val}},
        )
        all_done = all(
            quest.progress.get(obj, 0) + (amount if obj == objective else 0) >= target
            for obj, target in zip(
                [o.get("id", "") for o in quest.objectives],
                [o.get("target", 0) for o in quest.objectives],
            )
        )
        if all_done:
            await self.collection.update_one(
                {"user_id": user_id, "quest_id": quest_id},
                {"$set": {"completed": True}},
            )
        return {"completed": all_done, "objective_completed": new_val >= target if quest.objectives else False}

    async def complete_quest(self, user_id: int, quest_id: str) -> bool:
        result = await self.collection.update_one(
            {"user_id": user_id, "quest_id": quest_id},
            {"$set": {"completed": True}},
        )
        return result.modified_count > 0

    async def claim_quest(self, user_id: int, quest_id: str) -> bool:
        result = await self.collection.update_one(
            {"user_id": user_id, "quest_id": quest_id},
            {"$set": {"claimed": True}},
        )
        return result.modified_count > 0

    async def delete_quest(self, user_id: int, quest_id: str) -> None:
        await self.collection.delete_one({"user_id": user_id, "quest_id": quest_id})

    async def cleanup_expired(self) -> int:
        result = await self.collection.delete_many({
            "expires_at": {"$lt": datetime.now(timezone.utc)},
            "completed": False,
        })
        return result.deleted_count

    async def count_active(self, user_id: int) -> int:
        return await self.collection.count_documents({"user_id": user_id, "completed": False})

    async def get_completed_count(self, user_id: int) -> int:
        return await self.collection.count_documents({"user_id": user_id, "completed": True})
