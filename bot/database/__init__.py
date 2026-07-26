from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase

_client: AsyncIOMotorClient | None = None
_db: AsyncIOMotorDatabase | None = None


async def connect_db(uri: str, db_name: str) -> AsyncIOMotorDatabase:
    global _client, _db
    _client = AsyncIOMotorClient(uri)
    _db = _client[db_name]
    return _db


async def disconnect_db() -> None:
    global _client, _db
    if _client:
        _client.close()
        _client = None
    _db = None


def get_db() -> AsyncIOMotorDatabase:
    if _db is None:
        raise RuntimeError("Database not connected")
    return _db
