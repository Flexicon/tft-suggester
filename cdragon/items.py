from __future__ import annotations
from typing import List
import re

from pydantic.main import BaseModel

from cdragon.base import BASE_URL, asset_url, cached_session

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
    with cached_session() as session:
        res = session.get(ITEMS_URL)
    res.raise_for_status()  # raises an error for 4xx or 5xx responses

    return [Item(**item) for item in map(_map_item_dict, res.json())]


def _map_item_dict(item) -> dict:
    return {
        **item,
        'name': _parse_item_name(item['name']),
        'loadoutsIcon': asset_url(item['loadoutsIcon'])
    }


def _parse_item_name(name: str) -> str:
    prefix = "item_name_"
    prefix_index = name.find(prefix)

    if prefix_index == -1:
        return name
    
    name_without_prefix = name[prefix_index+len(prefix):]
    words = re.split('([A-Z][a-z]+)', name_without_prefix)
    words = [word for word in words if word and word not in ['_', '-']]

    return ' '.join(words)
