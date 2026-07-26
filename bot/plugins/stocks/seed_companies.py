from __future__ import annotations

from bot.services.stock_market_service import StockMarketService

SEED_COMPANIES = [
    {"ticker": "DGN", "name": "Dragon Industries", "sector": "conglomerate", "price": 245.50, "shares": 800000, "volatility": "high", "popularity": 75},
    {"ticker": "NEO", "name": "Neo Bank", "sector": "finance", "price": 189.30, "shares": 1200000, "volatility": "medium", "popularity": 80},
    {"ticker": "PXG", "name": "Pixel Games", "sector": "technology", "price": 312.75, "shares": 500000, "volatility": "high", "popularity": 85},
    {"ticker": "CYT", "name": "Cyber Tech", "sector": "technology", "price": 456.00, "shares": 600000, "volatility": "high", "popularity": 90},
    {"ticker": "MMI", "name": "Moon Mining", "sector": "mining", "price": 78.25, "shares": 2000000, "volatility": "extreme", "popularity": 60},
    {"ticker": "AQE", "name": "Aqua Energy", "sector": "energy", "price": 134.80, "shares": 900000, "volatility": "medium", "popularity": 70},
    {"ticker": "SKY", "name": "Sky Airlines", "sector": "transport", "price": 92.15, "shares": 1500000, "volatility": "high", "popularity": 65},
    {"ticker": "FFD", "name": "Food Factory", "sector": "food", "price": 56.40, "shares": 3000000, "volatility": "low", "popularity": 55},
    {"ticker": "GLX", "name": "Galaxy Media", "sector": "media", "price": 201.90, "shares": 700000, "volatility": "medium", "popularity": 72},
    {"ticker": "TTR", "name": "Titan Robotics", "sector": "technology", "price": 567.25, "shares": 400000, "volatility": "extreme", "popularity": 88},
    {"ticker": "VLT", "name": "Volt Electric", "sector": "energy", "price": 167.30, "shares": 800000, "volatility": "medium", "popularity": 68},
    {"ticker": "BLZ", "name": "Blaze Gaming", "sector": "entertainment", "price": 289.60, "shares": 550000, "volatility": "high", "popularity": 82},
    {"ticker": "NVA", "name": "Nova Pharmaceuticals", "sector": "healthcare", "price": 412.10, "shares": 450000, "volatility": "extreme", "popularity": 78},
    {"ticker": "TNK", "name": "Tanker Corp", "sector": "transport", "price": 45.90, "shares": 5000000, "volatility": "low", "popularity": 40},
    {"ticker": "ZEN", "name": "Zen Wellness", "sector": "healthcare", "price": 123.70, "shares": 1000000, "volatility": "medium", "popularity": 62},
    {"ticker": "ARC", "name": "Arctic Mining", "sector": "mining", "price": 98.45, "shares": 1800000, "volatility": "high", "popularity": 55},
    {"ticker": "BLU", "name": "Blue Ocean Tech", "sector": "technology", "price": 345.00, "shares": 600000, "volatility": "high", "popularity": 76},
    {"ticker": "CPX", "name": "Capitol Foods", "sector": "food", "price": 34.20, "shares": 4000000, "volatility": "low", "popularity": 45},
    {"ticker": "DRM", "name": "DreamWorks Animation", "sector": "entertainment", "price": 178.55, "shares": 750000, "volatility": "medium", "popularity": 70},
    {"ticker": "ELC", "name": "ElectroVolt", "sector": "technology", "price": 267.80, "shares": 500000, "volatility": "high", "popularity": 73},
    {"ticker": "FRC", "name": "Force Security", "sector": "technology", "price": 198.40, "shares": 650000, "volatility": "medium", "popularity": 65},
    {"ticker": "GEM", "name": "Gemini Finance", "sector": "finance", "price": 423.15, "shares": 350000, "volatility": "medium", "popularity": 77},
    {"ticker": "HVK", "name": "Havoc Motors", "sector": "automotive", "price": 156.90, "shares": 850000, "volatility": "medium", "popularity": 68},
    {"ticker": "ION", "name": "Ion Systems", "sector": "technology", "price": 389.25, "shares": 420000, "volatility": "high", "popularity": 80},
    {"ticker": "JET", "name": "JetStream Airways", "sector": "transport", "price": 67.30, "shares": 2500000, "volatility": "high", "popularity": 58},
    {"ticker": "KNG", "name": "Kingdom Properties", "sector": "real_estate", "price": 234.60, "shares": 600000, "volatility": "low", "popularity": 62},
    {"ticker": "LUX", "name": "Luxury Brands", "sector": "retail", "price": 512.00, "shares": 300000, "volatility": "medium", "popularity": 85},
    {"ticker": "MRN", "name": "Marine Harvest", "sector": "food", "price": 87.45, "shares": 1600000, "volatility": "low", "popularity": 50},
    {"ticker": "NEX", "name": "Nexus Cloud", "sector": "technology", "price": 678.90, "shares": 250000, "volatility": "extreme", "popularity": 92},
    {"ticker": "ORC", "name": "Oracle Dynamics", "sector": "technology", "price": 345.70, "shares": 500000, "volatility": "medium", "popularity": 75},
    {"ticker": "PRX", "name": "Praxis Biotech", "sector": "healthcare", "price": 289.30, "shares": 550000, "volatility": "high", "popularity": 72},
    {"ticker": "QNT", "name": "Quantum Labs", "sector": "technology", "price": 890.15, "shares": 200000, "volatility": "extreme", "popularity": 95},
    {"ticker": "RDX", "name": "Redox Energy", "sector": "energy", "price": 112.60, "shares": 1200000, "volatility": "medium", "popularity": 60},
    {"ticker": "SPR", "name": "Sprite Beverages", "sector": "food", "price": 43.80, "shares": 3500000, "volatility": "low", "popularity": 48},
    {"ticker": "THX", "name": "Thunder Works", "sector": "manufacturing", "price": 167.90, "shares": 700000, "volatility": "medium", "popularity": 58},
    {"ticker": "ULT", "name": "Ultimate Sports", "sector": "entertainment", "price": 145.25, "shares": 900000, "volatility": "medium", "popularity": 66},
    {"ticker": "VRX", "name": "Vertex Mining", "sector": "mining", "price": 76.40, "shares": 2200000, "volatility": "high", "popularity": 52},
    {"ticker": "WPR", "name": "Warp Transport", "sector": "transport", "price": 234.50, "shares": 600000, "volatility": "high", "popularity": 70},
    {"ticker": "XON", "name": "Xonex Industries", "sector": "conglomerate", "price": 178.30, "shares": 800000, "volatility": "medium", "popularity": 63},
    {"ticker": "YZR", "name": "Yzer Defense", "sector": "technology", "price": 567.80, "shares": 300000, "volatility": "high", "popularity": 78},
    {"ticker": "ZAP", "name": "Zap Power", "sector": "energy", "price": 198.70, "shares": 750000, "volatility": "medium", "popularity": 72},
    {"ticker": "BTR", "name": "Butterfly Robotics", "sector": "technology", "price": 445.20, "shares": 350000, "volatility": "high", "popularity": 82},
    {"ticker": "CRN", "name": "Crown Finance", "sector": "finance", "price": 312.45, "shares": 450000, "volatility": "low", "popularity": 70},
    {"ticker": "DUS", "name": "Dust Storm Mining", "sector": "mining", "price": 54.30, "shares": 3000000, "volatility": "extreme", "popularity": 42},
    {"ticker": "EPX", "name": "Epic Entertainment", "sector": "entertainment", "price": 267.15, "shares": 550000, "volatility": "high", "popularity": 80},
    {"ticker": "FLR", "name": "Flare Electronics", "sector": "technology", "price": 189.90, "shares": 700000, "volatility": "medium", "popularity": 65},
    {"ticker": "GRV", "name": "Gravity Dynamics", "sector": "technology", "price": 723.40, "shares": 220000, "volatility": "extreme", "popularity": 88},
    {"ticker": "HLP", "name": "HealthPlus Labs", "sector": "healthcare", "price": 156.25, "shares": 900000, "volatility": "medium", "popularity": 64},
    {"ticker": "IFR", "name": "Inferno Motors", "sector": "automotive", "price": 234.80, "shares": 600000, "volatility": "high", "popularity": 74},
    {"ticker": "JNX", "name": "Junex Energy", "sector": "energy", "price": 89.60, "shares": 2000000, "volatility": "medium", "popularity": 55},
    {"ticker": "KZR", "name": "Keizer Pharma", "sector": "healthcare", "price": 345.10, "shares": 400000, "volatility": "high", "popularity": 76},
    {"ticker": "LMR", "name": "Lemur Logistics", "sector": "transport", "price": 123.45, "shares": 1000000, "volatility": "medium", "popularity": 52},
    {"ticker": "MGC", "name": "Magic Cloud", "sector": "technology", "price": 567.30, "shares": 300000, "volatility": "extreme", "popularity": 90},
    {"ticker": "NVX", "name": "NoveX Solar", "sector": "energy", "price": 201.75, "shares": 700000, "volatility": "medium", "popularity": 68},
    {"ticker": "OPX", "name": "OpenX Systems", "sector": "technology", "price": 412.60, "shares": 400000, "volatility": "high", "popularity": 80},
    {"ticker": "PLX", "name": "Pulse Fitness", "sector": "entertainment", "price": 98.30, "shares": 1500000, "volatility": "low", "popularity": 58},
    {"ticker": "QRY", "name": "Query Data", "sector": "technology", "price": 378.90, "shares": 450000, "volatility": "high", "popularity": 77},
    {"ticker": "RZN", "name": "Razan Textiles", "sector": "manufacturing", "price": 67.40, "shares": 2500000, "volatility": "low", "popularity": 42},
    {"ticker": "SKR", "name": "Skor Energy", "sector": "energy", "price": 145.80, "shares": 900000, "volatility": "medium", "popularity": 60},
    {"ticker": "TRX", "name": "Trident Shipping", "sector": "transport", "price": 112.20, "shares": 1200000, "volatility": "medium", "popularity": 55},
    {"ticker": "UNX", "name": "UnX Finance", "sector": "finance", "price": 289.50, "shares": 500000, "volatility": "medium", "popularity": 72},
    {"ticker": "VNX", "name": "Vinex Media", "sector": "media", "price": 178.90, "shares": 800000, "volatility": "medium", "popularity": 65},
    {"ticker": "WLF", "name": "Wolf Pack Gaming", "sector": "entertainment", "price": 234.15, "shares": 600000, "volatility": "high", "popularity": 78},
    {"ticker": "XLR", "name": "Xceleron Tech", "sector": "technology", "price": 456.80, "shares": 350000, "volatility": "high", "popularity": 82},
    {"ticker": "YPR", "name": "Ypper Foods", "sector": "food", "price": 78.90, "shares": 2000000, "volatility": "low", "popularity": 50},
]


async def seed_stocks(stock_svc: StockMarketService) -> int:
    existing = await stock_svc.get_all_stocks()
    existing_tickers = {s.ticker for s in existing}
    count = 0
    for company in SEED_COMPANIES:
        if company["ticker"] not in existing_tickers:
            try:
                await stock_svc.create_stock(
                    ticker=company["ticker"],
                    name=company["name"],
                    sector=company["sector"],
                    price=company["price"],
                    shares=company["shares"],
                    volatility=company["volatility"],
                )
                if hasattr(stock_svc.stock_repo, 'collection'):
                    await stock_svc.stock_repo.collection.update_one(
                        {"ticker": company["ticker"]},
                        {"$set": {"popularity": company["popularity"]}},
                    )
                count += 1
            except Exception:
                pass
    return count
