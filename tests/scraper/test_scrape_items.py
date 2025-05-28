import responses

from common.models.composite_item import CompositeItem
from common.models.comp import Item
from scraper.scrape_items import ScrapeURL, scrape_items

from tests.scraper.test_helpers import load_mock_file


@responses.activate
def test_scrape_items_no_content():
    responses.add(responses.GET, ScrapeURL, body="", status=200)

    items = scrape_items()
    assert len(items) == 0, "Expected no items when the content is empty"


@responses.activate
def test_scrape_items(request):
    responses.add(
        responses.GET,
        ScrapeURL,
        body=load_mock_file(request, "mock_items.html"),
        status=200,
    )
    expected_items = [
        CompositeItem(
            name="Deathblade",
            image="https://www.mobafire.com/images/tft/set14/item/icon/deathblade.png",
            components=[
                Item(
                    name="B F Sword",
                    image="https://www.mobafire.com/images/tft/set14/item/icon/b-f-sword.png",
                ),
                Item(
                    name="B F Sword",
                    image="https://www.mobafire.com/images/tft/set14/item/icon/b-f-sword.png",
                ),
            ],
        ),
        CompositeItem(
            name="Giant Slayer",
            image="https://www.mobafire.com/images/tft/set14/item/icon/giant-slayer.png",
            components=[
                Item(
                    name="B F Sword",
                    image="https://www.mobafire.com/images/tft/set14/item/icon/b-f-sword.png",
                ),
                Item(
                    name="Recurve Bow",
                    image="https://www.mobafire.com/images/tft/set14/item/icon/recurve-bow.png",
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
