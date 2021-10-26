from __future__ import annotations
from typing import List

from pydantic.main import BaseModel
import requests

from cdragon.base import BASE_URL, asset_url

ITEMS_URL = f"{BASE_URL}/v1/tftitems.json"


class Color(BaseModel):
    R: int
    B: int
    G: int
    A: int


class Item(BaseModel):
    guid: str
    name: str
    id: int
    color: Color
    loadoutsIcon: str


def get_items() -> List[Item]:
    """Fetch all current items available in game. Results are cached for a time."""
    res = requests.get(ITEMS_URL)
    res.raise_for_status()  # raises an error for 4xx or 5xx responses

    return [Item(**item) for item in map(_map_item_dict, res.json())]


def _map_item_dict(item) -> dict:
    return {**item, 'loadoutsIcon': asset_url(item['loadoutsIcon'])}
