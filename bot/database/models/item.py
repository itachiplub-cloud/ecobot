from __future__ import annotations

from typing import Optional

from pydantic import BaseModel, Field


class ItemModel(BaseModel):
    item_id: str
    name: str
    description: str = ""
    category: str = "misc"
    subcategory: Optional[str] = None
    rarity: str = "common"
    price: int = 0
    sell_price: int = 0
    buyable: bool = True
    sellable: bool = True
    tradeable: bool = True
    stackable: bool = True
    max_stack: int = 999
    emoji: str = "📦"
    icon: Optional[str] = None
    stats: dict = Field(default_factory=dict)
    effects: dict = Field(default_factory=dict)
    requirements: dict = Field(default_factory=dict)
    quest_id: Optional[str] = None
    event_id: Optional[str] = None
    limited: bool = False
    limited_quantity: int = 0
    level_required: int = 1
    job_required: Optional[str] = None
    craftable: bool = False
    recipe: dict = Field(default_factory=dict)
    drop_rate: float = 0.0
    is_active: bool = True

    class Config:
        arbitrary_types_allowed = True

    def to_dict(self) -> dict:
        return self.model_dump(exclude_unset=True)

    @classmethod
    def from_doc(cls, doc: dict) -> ItemModel:
        if doc is None:
            return None
        doc.pop("_id", None)
        return cls(**doc)
