import pytest

from scraper.helpers import (
    _extract_traits_from_character_html,
    _price_from_character_class,
)


@pytest.mark.parametrize(
    "classes, expected",
    [
        ("characters-item c1 s75", 1),
        ("characters-item c2 s75", 2),
        ("characters-item c3 s75", 3),
        ("characters-item c4 s75", 4),
        ("random-class and another-one d99 c5 s2512 foobar", 5),
        ("characters-item c10 s75", 10),
        ("characters-item c420 s75", 420),
        ("class-missing oh-no", 0),
    ],
)
def test_price_from_character_class(classes, expected):
    result = _price_from_character_class(classes)
    assert result == expected, "result did not match expected value"


def test_extract_traits_from_character_html(request):
    html = load_mock_file(request, "mock_alistar.html")

    traits = _extract_traits_from_character_html(html)

    assert traits == ["Golden Ox", "Bruiser"]


def test_extract_traits_falls_back_to_section_labels():
    html = """
    <div class="character-ability">
      <div class="ability-description-name">
        <h2>Golden Ox</h2>
        <h4>Origin</h4>
      </div>
    </div>
    <div class="character-ability">
      <div class="ability-description-name">
        <h2>Gilded Endurance</h2>
        <h4>Active</h4>
      </div>
    </div>
    """

    traits = _extract_traits_from_character_html(html)

    assert traits == ["Golden Ox"]


def load_mock_file(request, filename):
    with open(f"{request.fspath.dirname}/mocks/{filename}", encoding="utf-8") as f:
        return f.read()
