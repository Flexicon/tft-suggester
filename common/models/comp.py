from typing import List, Optional

from common.models import Champion


from pydantic import BaseModel, Field


class Item(BaseModel):
    name: str
    image: str


class ItemRecommendation(BaseModel):
    champion: str
    items: List[Item] = Field(default_factory=list)


class Comp(BaseModel):
    name: str
    champions: List[Champion] = Field(default_factory=list)
    tier: Optional[str] = None
    playstyle: Optional[str] = None
    item_recommendations: List[ItemRecommendation] = Field(default_factory=list)
