import responses
import json
import pytest
import requests_cache

from common.models.composite_item import CompositeItem
from common.models.comp import Item
from scraper.scrape_items import scrape_items
from cdragon.items import TFT_DATA_URL


@pytest.fixture(autouse=True)
def clear_cache():
    """Setup and clear the cdragon api cache before and after every test."""
    session = requests_cache.CachedSession("cdragon_cache", expire_after=0)
    session.cache.clear()
    yield
    session.cache.clear()


@responses.activate
def test_scrape_items_no_items():
    """Test when API returns no composite items"""
    mock_data = {"items": []}
    responses.add(
        responses.GET,
        TFT_DATA_URL,
        json=mock_data,
        status=200,
    )

    items = scrape_items()
    assert len(items) == 0, "Expected no items when the API returns empty items array"


@responses.activate
def test_scrape_items_with_valid_data():
    """Test scraping items from Community Dragon API with valid data"""
    mock_data = {
        "items": [
            # Base components
            {
                "apiName": "TFT_Item_BFSword",
                "name": "B.F. Sword",
                "icon": "ASSETS/Maps/TFT/Icons/Items/Hexcore/TFT_Item_BFSword.TFT_Set13.tex",
                "composition": [],
            },
            {
                "apiName": "TFT_Item_RecurveBow",
                "name": "Recurve Bow",
                "icon": "ASSETS/Maps/TFT/Icons/Items/Hexcore/TFT_Item_RecurveBow.TFT_Set13.tex",
                "composition": [],
            },
            # Composite items
            {
                "apiName": "TFT_Item_Deathblade",
                "name": "Deathblade",
                "icon": "ASSETS/Maps/TFT/Icons/Items/Hexcore/TFT_Item_Deathblade.TFT_Set13.tex",
                "composition": ["TFT_Item_BFSword", "TFT_Item_BFSword"],
            },
            {
                "apiName": "TFT_Item_GiantSlayer",
                "name": "Giant Slayer",
                "icon": "ASSETS/Maps/TFT/Icons/Items/Hexcore/TFT_Item_GiantSlayer.TFT_Set13.tex",
                "composition": ["TFT_Item_BFSword", "TFT_Item_RecurveBow"],
            },
            # Should be filtered out (augment)
            {
                "apiName": "TFT_Augment_SomeAugment",
                "name": "Some Augment",
                "icon": "ASSETS/Maps/TFT/Icons/Augments/Something.tex",
                "composition": ["TFT_Item_BFSword"],
            },
        ]
    }

    responses.add(
        responses.GET,
        TFT_DATA_URL,
        json=mock_data,
        status=200,
    )

    expected_items = [
        CompositeItem(
            name="Deathblade",
            image="https://raw.communitydragon.org/latest/plugins/rcp-be-lol-game-data/global/default/assets/maps/tft/icons/items/hexcore/tft_item_deathblade.tft_set13.png",
            components=[
                Item(
                    name="B.F. Sword",
                    image="https://raw.communitydragon.org/latest/plugins/rcp-be-lol-game-data/global/default/assets/maps/tft/icons/items/hexcore/tft_item_bfsword.tft_set13.png",
                ),
                Item(
                    name="B.F. Sword",
                    image="https://raw.communitydragon.org/latest/plugins/rcp-be-lol-game-data/global/default/assets/maps/tft/icons/items/hexcore/tft_item_bfsword.tft_set13.png",
                ),
            ],
        ),
        CompositeItem(
            name="Giant Slayer",
            image="https://raw.communitydragon.org/latest/plugins/rcp-be-lol-game-data/global/default/assets/maps/tft/icons/items/hexcore/tft_item_giantslayer.tft_set13.png",
            components=[
                Item(
                    name="B.F. Sword",
                    image="https://raw.communitydragon.org/latest/plugins/rcp-be-lol-game-data/global/default/assets/maps/tft/icons/items/hexcore/tft_item_bfsword.tft_set13.png",
                ),
                Item(
                    name="Recurve Bow",
                    image="https://raw.communitydragon.org/latest/plugins/rcp-be-lol-game-data/global/default/assets/maps/tft/icons/items/hexcore/tft_item_recurvebow.tft_set13.png",
                ),
            ],
        ),
    ]

    items = scrape_items()

    assert len(items) == len(expected_items), "Items length does not match expected"

    for i, item in enumerate(items):
        assert (
            item.name == expected_items[i].name
        ), f"Item name at index {i} does not match"
        assert (
            item.image == expected_items[i].image
        ), f"Item image at index {i} does not match"
        assert len(item.components) == len(
            expected_items[i].components
        ), f"Components length at index {i} does not match"

        for j, component in enumerate(item.components):
            assert (
                component.name == expected_items[i].components[j].name
            ), f"Component name at index {i},{j} does not match"
            assert (
                component.image == expected_items[i].components[j].image
            ), f"Component image at index {i},{j} does not match"


@responses.activate
def test_scrape_items_with_raw_item_names():
    """Test that raw item names (tft_item_name_*) are properly parsed"""
    mock_data = {
        "items": [
            # Base component with raw name
            {
                "apiName": "TFT_Item_TestComponent",
                "name": "tft_item_name_TestComponent",
                "icon": "ASSETS/Maps/TFT/Icons/Items/test.tex",
                "composition": [],
            },
            # Composite item with raw name
            {
                "apiName": "TFT_Item_CursedBlade",
                "name": "tft_item_name_CursedBlade",
                "icon": "ASSETS/Maps/Particles/TFT/tft_item_cursedblade.tex",
                "composition": ["TFT_Item_TestComponent", "TFT_Item_TestComponent"],
            },
        ]
    }

    responses.add(
        responses.GET,
        TFT_DATA_URL,
        json=mock_data,
        status=200,
    )

    items = scrape_items()

    assert len(items) == 1, "Expected 1 composite item"
    assert items[0].name == "Cursed Blade", "Raw item name should be parsed"
    assert (
        items[0].components[0].name == "Test Component"
    ), "Raw component name should be parsed"
