from __future__ import annotations

from motor.motor_asyncio import AsyncIOMotorDatabase

from bot.database.repositories.pet_repo import PetRepository


class PetService:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.pet_repo = PetRepository(db)

    async def get_user_pets(self, user_id: int):
        return await self.pet_repo.get_user_pets(user_id)

    async def get_equipped_pet(self, user_id: int):
        return await self.pet_repo.get_equipped_pet(user_id)

    async def equip_pet(self, user_id: int, pet_id: str) -> bool:
        return await self.pet_repo.equip_pet(user_id, pet_id)

    async def feed_pet(self, user_id: int, pet_id: str, amount: int = 20) -> bool:
        return await self.pet_repo.feed_pet(user_id, pet_id, amount)

    async def play_pet(self, user_id: int, pet_id: str, amount: int = 20) -> bool:
        return await self.pet_repo.play_pet(user_id, pet_id, amount)

    async def add_pet_xp(self, user_id: int, pet_id: str, xp: int) -> dict:
        return await self.pet_repo.add_pet_xp(user_id, pet_id, xp)

    async def evolve_pet(self, user_id: int, pet_id: str) -> bool:
        return await self.pet_repo.evolve_pet(user_id, pet_id)

    async def remove_pet(self, user_id: int, pet_id: str) -> bool:
        return await self.pet_repo.remove_pet(user_id, pet_id)

    async def count_pets(self, user_id: int) -> int:
        return await self.pet_repo.count_pets(user_id)

    async def get_top_pets(self, field: str = "level", limit: int = 10):
        return await self.pet_repo.get_top_pets(field, limit)
