from typing import List

from common.models import Champion


from pydantic import BaseModel


class Item(BaseModel):
    name: str
    image: str


class ItemRecommendation(BaseModel):
    champion_name: str
    items: List[Item] = None


class Comp(BaseModel):
    name: str
    champions: List[Champion] = []
    tier: str = None
    playstyle: str = None
    item_recommendations: List[ItemRecommendation] = []
