import pytest

from scraper.helpers import _price_from_character_class


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
