from __future__ import annotations

from datetime import datetime
from typing import Optional

from motor.motor_asyncio import AsyncIOMotorDatabase

from bot.database.models.pet import PetModel


class PetRepository:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.collection = db.pets

    async def add_pet(self, pet: PetModel) -> PetModel:
        await self.collection.insert_one(pet.to_dict())
        return pet

    async def get_pet(self, user_id: int, pet_id: str) -> Optional[PetModel]:
        doc = await self.collection.find_one({"user_id": user_id, "pet_id": pet_id})
        return PetModel.from_doc(doc)

    async def get_user_pets(self, user_id: int) -> list[PetModel]:
        cursor = self.collection.find({"user_id": user_id})
        docs = await cursor.to_list(length=None)
        return [PetModel.from_doc(d) for d in docs]

    async def get_equipped_pet(self, user_id: int) -> Optional[PetModel]:
        doc = await self.collection.find_one({"user_id": user_id, "equipped": True})
        return PetModel.from_doc(doc)

    async def equip_pet(self, user_id: int, pet_id: str) -> bool:
        await self.collection.update_many(
            {"user_id": user_id},
            {"$set": {"equipped": False}},
        )
        result = await self.collection.update_one(
            {"user_id": user_id, "pet_id": pet_id},
            {"$set": {"equipped": True}},
        )
        return result.modified_count > 0

    async def update_pet(self, user_id: int, pet_id: str, **update_data) -> None:
        await self.collection.update_one(
            {"user_id": user_id, "pet_id": pet_id},
            {"$set": update_data},
        )

    async def add_pet_xp(self, user_id: int, pet_id: str, xp: int) -> dict:
        pet = await self.get_pet(user_id, pet_id)
        if not pet:
            return {"leveled_up": False}
        pet.xp += xp
        leveled_up = False
        while pet.xp >= pet.xp_needed:
            pet.xp -= pet.xp_needed
            pet.level += 1
            pet.xp_needed = int(pet.xp_needed * 1.5)
            pet.attack += 2
            pet.defense += 2
            pet.speed += 1
            leveled_up = True
        await self.collection.update_one(
            {"user_id": user_id, "pet_id": pet_id},
            {"$set": {
                "xp": pet.xp,
                "level": pet.level,
                "xp_needed": pet.xp_needed,
                "attack": pet.attack,
                "defense": pet.defense,
                "speed": pet.speed,
            }},
        )
        return {"leveled_up": leveled_up, "new_level": pet.level}

    async def remove_pet(self, user_id: int, pet_id: str) -> bool:
        result = await self.collection.delete_one({"user_id": user_id, "pet_id": pet_id})
        return result.deleted_count > 0

    async def count_pets(self, user_id: int) -> int:
        return await self.collection.count_documents({"user_id": user_id})

    async def feed_pet(self, user_id: int, pet_id: str, amount: int = 20) -> bool:
        result = await self.collection.update_one(
            {"user_id": user_id, "pet_id": pet_id},
            {"$inc": {"hunger": amount}, "$set": {"last_fed": datetime.utcnow()}},
        )
        return result.modified_count > 0

    async def play_pet(self, user_id: int, pet_id: str, amount: int = 20) -> bool:
        result = await self.collection.update_one(
            {"user_id": user_id, "pet_id": pet_id},
            {"$inc": {"happiness": amount}, "$set": {"last_played": datetime.utcnow()}},
        )
        return result.modified_count > 0

    async def evolve_pet(self, user_id: int, pet_id: str) -> bool:
        pet = await self.get_pet(user_id, pet_id)
        if not pet or pet.evolution_level >= pet.max_evolution:
            return False
        await self.collection.update_one(
            {"user_id": user_id, "pet_id": pet_id},
            {"$inc": {"evolution_level": 1}, "$set": {
                "attack": pet.attack + 20,
                "defense": pet.defense + 20,
                "speed": pet.speed + 10,
            }},
        )
        return True

    async def get_top_pets(self, field: str = "level", limit: int = 10) -> list[PetModel]:
        cursor = self.collection.find({}).sort(field, -1).limit(limit)
        docs = await cursor.to_list(length=limit)
        return [PetModel.from_doc(d) for d in docs]
