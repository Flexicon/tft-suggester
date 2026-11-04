from unittest.mock import Mock, patch

import responses

from common.models.champion import Champion
from common.models.comp import Comp, Item, ItemRecommendation
from scraper.constants import TFTBaseURL
from scraper.scrape_comps import TFTCompsURL, scrape_and_persist, scrape_comps

from tests.scraper.test_helpers import load_mock_file


@responses.activate
def test_scrape_comps_no_content():
    responses.add(responses.GET, TFTCompsURL, body="", status=200)

    comps = scrape_comps()
    assert len(comps) == 0, "Expected no comps when the content is empty"


@responses.activate
def test_scrape_comps(request):
    responses.add(
        responses.GET,
        TFTCompsURL,
        body=load_mock_file(request, "mock_comps.html"),
        status=200,
    )
    responses.add(
        responses.GET,
        f"{TFTBaseURL}/champions/alistar/",
        body=load_mock_file(request, "mock_alistar.html"),
        status=200,
    )
    responses.add(
        responses.GET,
        f"{TFTBaseURL}/champions/annie/",
        body=load_mock_file(request, "mock_annie.html"),
        status=200,
    )
    expected_comps = [
        Comp(
            name="Reroll Strategists",
            champions=[
                Champion(
                    name="Alistar",
                    image="https://sunderarmor.com/characters/Skin/14/Alistar.png",
                    cost=1,
                    traits=["Golden Ox", "Bruiser"],
                ),
                Champion(
                    name="Annie",
                    image="https://sunderarmor.com/characters/Skin/14/Annie.png",
                    cost=4,
                    traits=["Golden Ox", "A.M.P."],
                ),
            ],
            tier="B",
            playstyle="Slow Roll (6)",
            item_recommendations=[
                ItemRecommendation(
                    champion="Alistar",
                    items=[
                        Item(
                            name="Gargoyle Stoneplate",
                            image="https://sunderarmor.com/items/GargoyleStoneplate.png",
                        ),
                        Item(
                            name="Sunfire Cape",
                            image="https://sunderarmor.com/items/SunfireCape.png",
                        ),
                        Item(
                            name="Warmog's Armor",
                            image="https://sunderarmor.com/items/WarmogsArmor.png",
                        ),
                    ],
                ),
                ItemRecommendation(champion="Annie", items=[]),
            ],
        )
    ]

    comps = scrape_comps()

    assert len(comps) == len(
        expected_comps
    ), "Scraped comp count does not match expected values"

    for i, comp in enumerate(comps):
        expected_comp = expected_comps[i]
        assert comp.name == expected_comp.name, f"Comp name mismatch at index {i}"
        assert comp.tier == expected_comp.tier, f"Comp tier mismatch at index {i}"
        assert (
            comp.playstyle == expected_comp.playstyle
        ), f"Comp playstyle mismatch at index {i}"
        assert len(comp.champions) == len(
            expected_comp.champions
        ), f"Champion count mismatch at index {i}"

        for j, champion in enumerate(comp.champions):
            assert (
                champion == expected_comp.champions[j]
            ), f"Champion mismatch at index {i}, champion {j}"

        assert len(comp.item_recommendations) == len(
            expected_comp.item_recommendations
        ), f"Item recommendations count mismatch at index {i}"

        for j, item_rec in enumerate(comp.item_recommendations):
            expected_rec = expected_comp.item_recommendations[j]
            assert (
                item_rec.champion == expected_rec.champion
            ), f"Item recommendation champion mismatch at index {i}, recommendation {j}"
            assert len(item_rec.items) == len(
                expected_rec.items
            ), f"Item count mismatch at index {i}, recommendation {j}"

            for k, item in enumerate(item_rec.items):
                assert (
                    item == expected_rec.items[k]
                ), f"Item mismatch at index {i}, recommendation {j}, item {k}"


def test_scrape_and_persist_leaves_collection_untouched_when_empty():
    collection = Mock()

    with patch("scraper.scrape_comps.scrape_comps", return_value=[]):
        scrape_and_persist(collection)

    collection.drop.assert_not_called()
    collection.insert_many.assert_not_called()


@responses.activate
def test_scrape_comps_reuses_traits_lookup(request):
    responses.add(
        responses.GET,
        TFTCompsURL,
        body=load_mock_file(request, "mock_comps.html"),
        status=200,
    )
    traits_lookup = {
        "Alistar": ["Golden Ox", "Bruiser"],
        "Annie": ["Golden Ox", "A.M.P."],
    }

    comps = scrape_comps(traits_lookup=traits_lookup)

    assert [champion.traits for champion in comps[0].champions] == [
        ["Golden Ox", "Bruiser"],
        ["Golden Ox", "A.M.P."],
    ]
    assert len(responses.calls) == 1, "Expected no champion detail page requests"


@responses.activate
def test_scrape_comps_fetches_traits_missing_from_lookup(request):
    responses.add(
        responses.GET,
        TFTCompsURL,
        body=load_mock_file(request, "mock_comps.html"),
        status=200,
    )
    responses.add(
        responses.GET,
        f"{TFTBaseURL}/champions/annie/",
        body=load_mock_file(request, "mock_annie.html"),
        status=200,
    )

    comps = scrape_comps(traits_lookup={"Alistar": ["Golden Ox", "Bruiser"]})

    assert comps[0].champions[0].traits == ["Golden Ox", "Bruiser"]
    assert comps[0].champions[1].traits == ["Golden Ox", "A.M.P."]
