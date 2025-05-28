import responses

from common.models.champion import Champion
from scraper.constants import TFTBaseURL
from scraper.scrape_champions import TFTChampionsURL, scrape_champions

from tests.scraper.test_helpers import load_mock_file


@responses.activate
def test_scrape_champions_no_content():
    responses.add(responses.GET, TFTChampionsURL, body="", status=200)

    champions = scrape_champions()
    assert len(champions) == 0, "Expected no champions when the content is empty"


@responses.activate
def test_scrape_champions(request):
    responses.add(
        responses.GET,
        TFTChampionsURL,
        body=load_mock_file(request, "mock_champions.html"),
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
    expected_champions = [
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
    ]

    champions = scrape_champions()
    assert champions == expected_champions, "Champions do not match expected values"
