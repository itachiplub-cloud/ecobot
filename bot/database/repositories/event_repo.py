from __future__ import annotations

from datetime import datetime, timezone
from typing import Optional

from motor.motor_asyncio import AsyncIOMotorDatabase

from bot.database.models.event import EventModel


class EventRepository:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.collection = db.events

    async def create_event(self, event: EventModel) -> EventModel:
        await self.collection.insert_one(event.to_dict())
        return event

    async def get_event(self, event_id: str) -> Optional[EventModel]:
        doc = await self.collection.find_one({"event_id": event_id})
        return EventModel.from_doc(doc)

    async def get_active_events(self) -> list[EventModel]:
        now = datetime.now(timezone.utc)
        cursor = self.collection.find({
            "is_active": True,
            "$or": [
                {"start_at": {"$lte": now}, "end_at": {"$gte": now}},
                {"start_at": None, "end_at": None},
            ],
        })
        docs = await cursor.to_list(length=None)
        return [EventModel.from_doc(d) for d in docs]

    async def update_event(self, event_id: str, **update_data) -> None:
        await self.collection.update_one(
            {"event_id": event_id},
            {"$set": update_data},
        )

    async def add_participant(self, event_id: str, user_id: int) -> bool:
        result = await self.collection.update_one(
            {"event_id": event_id},
            {"$addToSet": {"participants": user_id}},
        )
        return result.modified_count > 0

    async def end_event(self, event_id: str) -> None:
        await self.collection.update_one(
            {"event_id": event_id},
            {"$set": {"is_active": False}},
        )

    async def delete_event(self, event_id: str) -> None:
        await self.collection.delete_one({"event_id": event_id})

    async def get_user_events(self, user_id: int) -> list[EventModel]:
        cursor = self.collection.find({"participants": user_id, "is_active": True})
        docs = await cursor.to_list(length=None)
        return [EventModel.from_doc(d) for d in docs]
