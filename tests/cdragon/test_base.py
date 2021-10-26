import pytest

from cdragon.base import asset_url, BASE_URL


@pytest.mark.parametrize("path, expected", [
    ("FooBar/BaZ.png", f"{BASE_URL}/foobar/baz.png"),
    ("/lol-game-data/assets/SomeTestASSeT.pNg", f"{BASE_URL}/sometestasset.png"),
    ("/foo/lol-game-data/assets/SomeTestASSeT.pNg", f"{BASE_URL}/foo/lol-game-data/assets/sometestasset.png"),
    # real world example params
    ("/lol-game-data/assets/ASSETS/Maps/Particles/TFT/TFT_Item_BladeOfTheRuinedKing.png",
     f"{BASE_URL}/assets/maps/particles/tft/tft_item_bladeoftheruinedking.png"),
])
def test_asset_url(path, expected):
    assert asset_url(path) == expected, "result did not match expected value"
