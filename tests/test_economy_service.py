import pytest
from unittest.mock import AsyncMock, MagicMock, patch


@pytest.fixture
def mock_db():
    db = MagicMock()
    db.economy = AsyncMock()
    db.transactions = AsyncMock()
    return db


@pytest.mark.asyncio
async def test_add_coins(mock_db):
    from bot.services.economy_service import EconomyService
    with patch("bot.services.economy_service.EconomyRepository") as mock_repo:
        mock_econ = MagicMock()
        mock_econ.wallet = 100
        mock_repo.return_value.add_coins = AsyncMock(return_value=mock_econ)
        mock_repo.return_value.get_or_create = AsyncMock(return_value=mock_econ)
        with patch("bot.services.economy_service.TransactionRepository") as mock_tx:
            mock_tx.return_value.add_transaction = AsyncMock()
            mock_tx.return_value.check_duplicate = AsyncMock(return_value=False)
            svc = EconomyService(mock_db)
            result = await svc.add_coins(123, 50, "test")
            assert result["success"] is True


@pytest.mark.asyncio
async def test_remove_coins_insufficient(mock_db):
    from bot.services.economy_service import EconomyService
    with patch("bot.services.economy_service.EconomyRepository") as mock_repo:
        mock_econ = MagicMock()
        mock_econ.wallet = 10
        mock_repo.return_value.get_economy = AsyncMock(return_value=mock_econ)
        with patch("bot.services.economy_service.TransactionRepository"):
            svc = EconomyService(mock_db)
            result = await svc.remove_coins(123, 100, "test")
            assert result["success"] is False
            assert result["reason"] == "insufficient_funds"


@pytest.mark.asyncio
async def test_transfer(mock_db):
    from bot.services.economy_service import EconomyService
    with patch("bot.services.economy_service.EconomyRepository") as mock_repo:
        sender = MagicMock()
        sender.wallet = 500
        receiver = MagicMock()
        receiver.wallet = 100
        mock_repo.return_value.transfer = AsyncMock(return_value=(sender, receiver))
        with patch("bot.services.economy_service.TransactionRepository") as mock_tx:
            mock_tx.return_value.add_transaction = AsyncMock()
            mock_tx.return_value.check_duplicate = AsyncMock(return_value=False)
            svc = EconomyService(mock_db)
            result = await svc.transfer(1, 2, 100)
            assert result["success"] is True
