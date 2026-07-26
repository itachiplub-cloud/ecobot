from __future__ import annotations

from datetime import datetime
from typing import Optional

from motor.motor_asyncio import AsyncIOMotorDatabase

from bot.database.models.stock_portfolio import StockPortfolioModel


class StockPortfolioRepository:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.collection = db.stock_portfolios

    async def get_holding(self, user_id: int, ticker: str) -> Optional[StockPortfolioModel]:
        doc = await self.collection.find_one({"user_id": user_id, "ticker": ticker.upper()})
        return StockPortfolioModel.from_doc(doc)

    async def get_user_portfolio(self, user_id: int) -> list[StockPortfolioModel]:
        cursor = self.collection.find({"user_id": user_id, "shares": {"$gt": 0}})
        docs = await cursor.to_list(length=None)
        return [StockPortfolioModel.from_doc(d) for d in docs]

    async def upsert_holding(self, holding: StockPortfolioModel) -> StockPortfolioModel:
        await self.collection.update_one(
            {"user_id": holding.user_id, "ticker": holding.ticker},
            {"$set": holding.to_dict()},
            upsert=True,
        )
        return holding

    async def update_holding(self, user_id: int, ticker: str, **data) -> None:
        data["last_updated"] = datetime.utcnow()
        await self.collection.update_one(
            {"user_id": user_id, "ticker": ticker.upper()},
            {"$set": data},
        )

    async def remove_holding(self, user_id: int, ticker: str) -> bool:
        result = await self.collection.update_one(
            {"user_id": user_id, "ticker": ticker.upper()},
            {"$set": {"shares": 0, "last_updated": datetime.utcnow()}},
        )
        return result.modified_count > 0

    async def get_top_investors(self, limit: int = 10) -> list[dict]:
        pipeline = [
            {"$match": {"shares": {"$gt": 0}}},
            {"$group": {
                "_id": "$user_id",
                "total_value": {"$sum": {"$multiply": ["$shares", "$avg_buy_price"]}},
                "total_shares": {"$sum": "$shares"},
                "stocks_count": {"$sum": 1},
            }},
            {"$sort": {"total_value": -1}},
            {"$limit": limit},
        ]
        cursor = self.collection.aggregate(pipeline)
        return await cursor.to_list(length=limit)

    async def get_highest_portfolio_value(self, limit: int = 10) -> list[dict]:
        pipeline = [
            {"$match": {"shares": {"$gt": 0}}},
            {"$group": {
                "_id": "$user_id",
                "total_invested": {"$sum": "$total_invested"},
                "lifetime_profit": {"$sum": "$lifetime_profit"},
                "lifetime_loss": {"$sum": "$lifetime_loss"},
            }},
            {"$addFields": {
                "net_value": {"$subtract": [
                    {"$add": ["$total_invested", "$lifetime_profit"]},
                    "$lifetime_loss"
                ]}
            }},
            {"$sort": {"net_value": -1}},
            {"$limit": limit},
        ]
        cursor = self.collection.aggregate(pipeline)
        return await cursor.to_list(length=limit)

    async def get_highest_profit(self, limit: int = 10) -> list[dict]:
        pipeline = [
            {"$match": {"lifetime_profit": {"$gt": 0}}},
            {"$group": {
                "_id": "$user_id",
                "total_profit": {"$sum": "$lifetime_profit"},
            }},
            {"$sort": {"total_profit": -1}},
            {"$limit": limit},
        ]
        cursor = self.collection.aggregate(pipeline)
        return await cursor.to_list(length=limit)

    async def get_highest_loss(self, limit: int = 10) -> list[dict]:
        pipeline = [
            {"$match": {"lifetime_loss": {"$gt": 0}}},
            {"$group": {
                "_id": "$user_id",
                "total_loss": {"$sum": "$lifetime_loss"},
            }},
            {"$sort": {"total_loss": -1}},
            {"$limit": limit},
        ]
        cursor = self.collection.aggregate(pipeline)
        return await cursor.to_list(length=limit)

    async def get_most_stocks_owned(self, limit: int = 10) -> list[dict]:
        pipeline = [
            {"$match": {"shares": {"$gt": 0}}},
            {"$group": {
                "_id": "$user_id",
                "total_shares": {"$sum": "$shares"},
                "stocks_count": {"$sum": 1},
            }},
            {"$sort": {"total_shares": -1}},
            {"$limit": limit},
        ]
        cursor = self.collection.aggregate(pipeline)
        return await cursor.to_list(length=limit)

    async def get_best_roi(self, limit: int = 10) -> list[dict]:
        pipeline = [
            {"$match": {"total_invested": {"$gt": 0}, "shares": {"$gt": 0}}},
            {"$addFields": {
                "roi": {"$multiply": [
                    {"$divide": ["$lifetime_profit", "$total_invested"]},
                    100
                ]}
            }},
            {"$sort": {"roi": -1}},
            {"$limit": limit},
        ]
        cursor = self.collection.aggregate(pipeline)
        return await cursor.to_list(length=limit)

    async def get_stop_loss_triggers(self) -> list[StockPortfolioModel]:
        pipeline = [
            {"$match": {
                "stop_loss_pct": {"$ne": None},
                "shares": {"$gt": 0},
            }},
        ]
        cursor = self.collection.aggregate(pipeline)
        docs = await cursor.to_list(length=None)
        return [StockPortfolioModel.from_doc(d) for d in docs]

    async def get_take_profit_triggers(self) -> list[StockPortfolioModel]:
        pipeline = [
            {"$match": {
                "take_profit_pct": {"$ne": None},
                "shares": {"$gt": 0},
            }},
        ]
        cursor = self.collection.aggregate(pipeline)
        docs = await cursor.to_list(length=None)
        return [StockPortfolioModel.from_doc(d) for d in docs]
