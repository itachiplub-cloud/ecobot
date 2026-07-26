from __future__ import annotations

import random
import string
from motor.motor_asyncio import AsyncIOMotorDatabase

from bot.database.repositories.event_repo import EventRepository
from bot.database.models.event import EventModel


class EventService:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.event_repo = EventRepository(db)

    async def create_event(self, name: str, event_type: str, description: str = "", **kwargs) -> EventModel:
        event_id = "EVT-" + "".join(random.choices(string.ascii_uppercase + string.digits, k=8))
        event = EventModel(event_id=event_id, name=name, event_type=event_type, description=description, **kwargs)
        return await self.event_repo.create_event(event)

    async def get_event(self, event_id: str):
        return await self.event_repo.get_event(event_id)

    async def get_active_events(self):
        return await self.event_repo.get_active_events()

    async def join_event(self, event_id: str, user_id: int) -> bool:
        return await self.event_repo.add_participant(event_id, user_id)

    async def end_event(self, event_id: str) -> None:
        await self.event_repo.end_event(event_id)

    async def get_user_events(self, user_id: int):
        return await self.event_repo.get_user_events(user_id)

    async def delete_event(self, event_id: str) -> None:
        await self.event_repo.delete_event(event_id)
