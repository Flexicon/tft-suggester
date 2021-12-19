from typing import List

import pytest
import requests
import requests_cache
import responses

from cdragon.base import BASE_URL
from cdragon.items import ITEMS_URL, Item, get_items, _parse_item_name


@pytest.fixture(autouse=True)
def clear_cache():
    """Setup and clear the cdragon api cache before and after every test."""
    session = requests_cache.CachedSession('cdragon_cache', expire_after=0)
    session.remove_expired_responses(expire_after=0)
    yield
    session.remove_expired_responses(expire_after=0)


@responses.activate
def test_get_items_empty():
    responses.add(responses.GET, ITEMS_URL, json=[], status=200)
    assert get_items() == []


@responses.activate
def test_get_items_not_found():
    responses.add(responses.GET, ITEMS_URL, status=404)
    with pytest.raises(requests.exceptions.HTTPError):
        get_items()


@responses.activate
def test_get_items_ok():
    responses.add(responses.GET, ITEMS_URL,
                  json=_dummy_items_response(), status=200)
    expected_results = [
        Item(
            guid="fe3a63e6-cc62-4299-a52a-d65755cf6cff",
            name="Blade of the Ruined King",
            id=28,
            color={"R": 186, "B": 255, "G": 46, "A": 255},
            loadoutsIcon=f"{BASE_URL}/assets/maps/particles/tft/tft_item_bladeoftheruinedking.png"
        ),
        Item(
            guid="a56e667b-36c6-4f81-98f7-e79188ac1a5e",
            name="Berserker's Axe",
            id=89,
            color={"R": 0, "B": 0, "G": 0, "A": 255},
            loadoutsIcon=f"{BASE_URL}/assets/maps/particles/tft/tft_item_berserkeraxe.png"
        ),
    ]

    results = get_items()
    assert len(results) == len(expected_results)
    assert results == expected_results


@pytest.mark.parametrize("name, expected", [
    ("TFT_item_name_BladeOfTheRuinedKing", "Blade Of The Ruined King"),
    ("tft_item_name_Set5Abomination_RadiantSpat", "Set 5 Abomination Radiant Spat"),
])
def test_parse_item_name(name, expected):
    got = _parse_item_name(name)
    assert got == expected, "result did not match expected value"


def _dummy_items_response() -> List[dict]:
    return [
        {
            "guid": "fe3a63e6-cc62-4299-a52a-d65755cf6cff",
            "name": "Blade of the Ruined King",
            "id": 28,
            "color": {"R": 186, "B": 255, "G": 46, "A": 255},
            "loadoutsIcon": "/lol-game-data/assets/ASSETS/Maps/Particles/TFT/TFT_Item_BladeOfTheRuinedKing.png"
        },
        {
            "guid": "a56e667b-36c6-4f81-98f7-e79188ac1a5e",
            "name": "Berserker's Axe",
            "id": 89,
            "color": {"R": 0, "B": 0, "G": 0, "A": 255},
            "loadoutsIcon": "/lol-game-data/assets/ASSETS/Maps/Particles/TFT/TFT_Item_BerserkerAxe.png"
        }
    ]
