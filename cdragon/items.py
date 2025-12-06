from __future__ import annotations
from typing import List, Dict
import re

from pydantic.main import BaseModel

from cdragon.base import BASE_URL, CDRAGON_CDN, asset_url, cached_session
from common.models import CompositeItem, Item as SimpleItem

ITEMS_URL = f"{BASE_URL}/v1/tftitems.json"
TFT_DATA_URL = f"{CDRAGON_CDN}/cdragon/tft/en_us.json"


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
        "name": _parse_item_name(item["name"]),
        "loadoutsIcon": asset_url(item["loadoutsIcon"]),
    }


def _parse_item_name(name: str) -> str:
    prefix = "item_name_"
    prefix_index = name.find(prefix)

    if prefix_index == -1:
        return name

    name_without_prefix = name[prefix_index + len(prefix) :]
    words = re.split("([A-Z][a-z]+)", name_without_prefix)
    words = [word for word in words if word and word not in ["_", "-"]]

    return " ".join(words)


def get_composite_items() -> List[CompositeItem]:
    """Fetch all composite TFT items with their components from Community Dragon.

    Returns a list of CompositeItem objects, each containing the item name, image URL,
    and a list of component Items. Results are cached for a time.
    """
    with cached_session() as session:
        res = session.get(TFT_DATA_URL)
    res.raise_for_status()

    data = res.json()
    all_items = data.get("items", [])

    # Filter for actual TFT items (not augments or special items)
    tft_items = [
        item for item in all_items
        if item.get("apiName", "").startswith("TFT_Item_")
        and "Augment" not in item.get("apiName", "")
    ]

    # Create a mapping of apiName to item data for looking up components
    items_by_api_name: Dict[str, dict] = {
        item["apiName"]: item for item in tft_items
    }

    # Filter for composite items (items with components)
    composite_items_data = [
        item for item in tft_items
        if item.get("composition") and len(item.get("composition", [])) > 0
    ]

    # Build CompositeItem objects
    composite_items = []
    for item_data in composite_items_data:
        try:
            composite_item = _build_composite_item(item_data, items_by_api_name)
            composite_items.append(composite_item)
        except Exception as e:
            # Log but continue if we can't parse a specific item
            print(f"Warning: Could not parse item {item_data.get('name', 'unknown')}: {e}")
            continue

    return composite_items


def _build_composite_item(item_data: dict, items_lookup: Dict[str, dict]) -> CompositeItem:
    """Build a CompositeItem from raw item data and a lookup dict for components."""
    name = item_data["name"]
    # Parse name if it's in raw format (e.g., "tft_item_name_CursedBlade")
    if "tft_item_name_" in name.lower() or "_" in name:
        name = _parse_item_name(name)

    icon_path = item_data["icon"]
    image_url = asset_url(icon_path)

    # Build component Items
    components = []
    for component_api_name in item_data["composition"]:
        component_data = items_lookup.get(component_api_name)
        if component_data:
            component_name = component_data["name"]
            # Parse component name if needed
            if "tft_item_name_" in component_name.lower() or "_" in component_name:
                component_name = _parse_item_name(component_name)

            component_item = SimpleItem(
                name=component_name,
                image=asset_url(component_data["icon"])
            )
            components.append(component_item)

    return CompositeItem(
        name=name,
        image=image_url,
        components=components
    )
