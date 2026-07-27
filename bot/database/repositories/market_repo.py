from __future__ import annotations

from datetime import datetime, timezone
from typing import Optional

from motor.motor_asyncio import AsyncIOMotorDatabase

from bot.database.models.market import MarketModel, AuctionModel


class MarketRepository:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.market = db.market
        self.auction = db.auction

    async def create_listing(self, listing: MarketModel) -> MarketModel:
        await self.market.insert_one(listing.to_dict())
        return listing

    async def get_listing(self, listing_id: str) -> Optional[MarketModel]:
        doc = await self.market.find_one({"listing_id": listing_id})
        return MarketModel.from_doc(doc)

    async def get_listings(self, item_id: Optional[str] = None, limit: int = 50) -> list[MarketModel]:
        query = {"sold": False}
        if item_id:
            query["item_id"] = item_id
        cursor = self.market.find(query).sort("price", 1).limit(limit)
        docs = await cursor.to_list(length=limit)
        return [MarketModel.from_doc(d) for d in docs]

    async def buy_listing(self, listing_id: str, buyer_id: int) -> Optional[MarketModel]:
        listing = await self.get_listing(listing_id)
        if not listing or listing.sold:
            return None
        await self.market.update_one(
            {"listing_id": listing_id},
            {"$set": {"sold": True, "buyer_id": buyer_id}},
        )
        listing.sold = True
        listing.buyer_id = buyer_id
        return listing

    async def remove_listing(self, listing_id: str) -> bool:
        result = await self.market.delete_one({"listing_id": listing_id})
        return result.deleted_count > 0

    async def get_user_listings(self, user_id: int) -> list[MarketModel]:
        cursor = self.market.find({"seller_id": user_id, "sold": False})
        docs = await cursor.to_list(length=None)
        return [MarketModel.from_doc(d) for d in docs]

    async def create_auction(self, auction: AuctionModel) -> AuctionModel:
        await self.auction.insert_one(auction.to_dict())
        return auction

    async def get_auction(self, auction_id: str) -> Optional[AuctionModel]:
        doc = await self.auction.find_one({"auction_id": auction_id})
        return AuctionModel.from_doc(doc)

    async def place_bid(self, auction_id: str, bidder_id: int, amount: int) -> Optional[AuctionModel]:
        auction = await self.get_auction(auction_id)
        if not auction or auction.ended or amount <= auction.current_bid:
            return None
        await self.auction.update_one(
            {"auction_id": auction_id},
            {"$set": {"current_bid": amount, "current_bidder": bidder_id}, "$inc": {"bid_count": 1}},
        )
        auction.current_bid = amount
        auction.current_bidder = bidder_id
        auction.bid_count += 1
        return auction

    async def buyout_auction(self, auction_id: str, buyer_id: int) -> Optional[AuctionModel]:
        auction = await self.get_auction(auction_id)
        if not auction or auction.ended:
            return None
        if not auction.buyout_price:
            return None
        await self.auction.update_one(
            {"auction_id": auction_id},
            {"$set": {"ended": True, "winner_id": buyer_id, "current_bid": auction.buyout_price, "current_bidder": buyer_id}},
        )
        auction.ended = True
        auction.winner_id = buyer_id
        return auction

    async def end_auction(self, auction_id: str) -> Optional[AuctionModel]:
        auction = await self.get_auction(auction_id)
        if not auction or auction.ended:
            return None
        winner = auction.current_bidder
        await self.auction.update_one(
            {"auction_id": auction_id},
            {"$set": {"ended": True, "winner_id": winner}},
        )
        auction.ended = True
        auction.winner_id = winner
        return auction

    async def get_active_auctions(self, limit: int = 50) -> list[AuctionModel]:
        cursor = self.auction.find({"ended": False}).sort("expires_at", 1).limit(limit)
        docs = await cursor.to_list(length=limit)
        return [AuctionModel.from_doc(d) for d in docs]

    async def cleanup_expired(self) -> int:
        now = datetime.now(timezone.utc)
        market_result = await self.market.delete_many({"expires_at": {"$lt": now}, "sold": False})
        return market_result.deleted_count
