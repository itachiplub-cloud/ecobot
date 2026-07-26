import pytest
from datetime import datetime
from bot.database.models.user import UserModel
from bot.database.models.economy import EconomyModel
from bot.database.models.inventory import InventoryModel
from bot.database.models.item import ItemModel


def test_user_model():
    user = UserModel(user_id=123)
    assert user.user_id == 123
    assert user.level == 1
    assert user.xp == 0
    assert user.is_banned is False
    d = user.to_dict()
    assert d["user_id"] == 123


def test_user_from_doc():
    doc = {"user_id": 456, "level": 5, "xp": 200}
    user = UserModel.from_doc(doc)
    assert user.user_id == 456
    assert user.level == 5


def test_user_from_doc_none():
    assert UserModel.from_doc(None) is None


def test_economy_model():
    eco = EconomyModel(user_id=123, wallet=500, bank=1000)
    assert eco.wallet == 500
    assert eco.bank == 1000
    d = eco.to_dict()
    assert d["wallet"] == 500


def test_inventory_model():
    inv = InventoryModel(user_id=123, item_id="sword_01", quantity=1)
    assert inv.item_id == "sword_01"
    assert inv.quantity == 1
    assert inv.equipped is False


def test_item_model():
    item = ItemModel(item_id="sword_01", name="Iron Sword", price=100)
    assert item.item_id == "sword_01"
    assert item.name == "Iron Sword"
    assert item.price == 100
    assert item.rarity == "common"
