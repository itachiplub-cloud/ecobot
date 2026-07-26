from __future__ import annotations

import random
import string
from motor.motor_asyncio import AsyncIOMotorDatabase

from bot.database.repositories.market_repo import MarketRepository
from bot.database.models.market import MarketModel, AuctionModel


class MarketService:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.market_repo = MarketRepository(db)

    async def create_listing(self, seller_id: int, item_id: str, quantity: int, price: int) -> dict:
        listing_id = "MKT-" + "".join(random.choices(string.ascii_uppercase + string.digits, k=8))
        listing = MarketModel(
            listing_id=listing_id, seller_id=seller_id, item_id=item_id,
            quantity=quantity, price=price,
        )
        await self.market_repo.create_listing(listing)
        return {"success": True, "listing_id": listing_id}

    async def get_listings(self, item_id: str = None, limit: int = 50):
        return await self.market_repo.get_listings(item_id, limit)

    async def buy_listing(self, listing_id: str, buyer_id: int) -> dict:
        listing = await self.market_repo.buy_listing(listing_id, buyer_id)
        if not listing:
            return {"success": False, "reason": "not_found_or_sold"}
        return {"success": True, "price": listing.price * listing.quantity}

    async def remove_listing(self, listing_id: str) -> bool:
        return await self.market_repo.remove_listing(listing_id)

    async def get_user_listings(self, user_id: int):
        return await self.market_repo.get_user_listings(user_id)

    async def create_auction(self, seller_id: int, item_id: str, quantity: int, starting_bid: int, buyout: int = None) -> dict:
        auction_id = "AUC-" + "".join(random.choices(string.ascii_uppercase + string.digits, k=8))
        auction = AuctionModel(
            auction_id=auction_id, seller_id=seller_id, item_id=item_id,
            quantity=quantity, starting_bid=starting_bid, current_bid=starting_bid,
            buyout_price=buyout,
        )
        await self.market_repo.create_auction(auction)
        return {"success": True, "auction_id": auction_id}

    async def place_bid(self, auction_id: str, bidder_id: int, amount: int) -> dict:
        result = await self.market_repo.place_bid(auction_id, bidder_id, amount)
        if not result:
            return {"success": False, "reason": "invalid_bid"}
        return {"success": True, "new_bid": amount}

    async def buyout_auction(self, auction_id: str, buyer_id: int) -> dict:
        result = await self.market_repo.buyout_auction(auction_id, buyer_id)
        if not result:
            return {"success": False, "reason": "no_buyout"}
        return {"success": True, "price": result.buyout_price}

    async def get_active_auctions(self, limit: int = 50):
        return await self.market_repo.get_active_auctions(limit)
