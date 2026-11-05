import logging
from typing import List, Mapping, Optional

from bs4 import BeautifulSoup
from bs4.element import Tag
from pymongo.collection import Collection

from common.models import Comp, Item, ItemRecommendation
from common.db import DB, replace_collection
from scraper.constants import TFTBaseURL
from scraper.helpers import (
    build_champion_from_character,
    require_tag,
    require_tag_by_class,
)
from scraper.http_client import get
from scraper.logging_utils import configure_logging

logger = logging.getLogger(__name__)

TFTCompsURL = f"{TFTBaseURL}/tierlist/team-comps"
TEAM_NAME_CLASS = "team-name-elipsis"
TEAM_PLAYSTYLE_CLASS = "team-playstyle"


def scrape_comps(
    traits_lookup: Optional[Mapping[str, list[str]]] = None,
) -> List[Comp]:
    logger.info("Fetching comps from: %s", TFTCompsURL)
    res = get(TFTCompsURL)
    res.raise_for_status()

    teams = BeautifulSoup(res.text, "html.parser").find_all(
        "div", class_="team-portrait"
    )
    return [_build_comp_from_team(t, traits_lookup) for t in teams]


def _build_comp_from_team(
    team: Tag, traits_lookup: Optional[Mapping[str, list[str]]] = None
) -> Comp:
    playstyle = require_tag_by_class(team, TEAM_PLAYSTYLE_CLASS).get_text(strip=True)
    tier = require_tag_by_class(team, "team-rank").get_text(strip=True)
    name = _comp_name(team, playstyle)

    characters = team.select(".team-characters > .characters-item")
    champions = [
        build_champion_from_character(character, traits_lookup)
        for character in characters
    ]
    items = [
        _build_item_recommendation(character, champion.name)
        for character, champion in zip(characters, champions)
    ]

    return Comp(
        name=name,
        champions=champions,
        tier=tier,
        playstyle=playstyle,
        item_recommendations=items,
    )


def _comp_name(team: Tag, playstyle: str) -> str:
    """Read the comp name without the playstyle text nested inside the same tag."""
    name_tag = require_tag_by_class(team, TEAM_NAME_CLASS)
    name = " ".join(
        text.strip() for text in name_tag.find_all(string=True, recursive=False)
    ).strip()

    if name:
        return name

    # Fallback for markup changes: the playstyle is nested inside the name tag.
    return name_tag.get_text(strip=True).replace(playstyle, "").strip()


def _build_item_recommendation(
    character: Tag, champion_name: str
) -> ItemRecommendation:
    item_tags = character.select(".character-items > .characters-item")
    items = [_build_item(t) for t in item_tags]
    return ItemRecommendation(champion=champion_name, items=items)


def _build_item(tag: Tag) -> Item:
    img_tag = require_tag(tag, "img")
    name = str(img_tag["alt"])
    icon = str(img_tag["src"])

    return Item(name=name, image=icon)


def load_traits_lookup(champions_collection: Collection) -> dict[str, list[str]]:
    """Reuse the traits persisted by the champions scraper."""
    return {
        document["name"]: document.get("traits", [])
        for document in champions_collection.find({}, {"name": 1, "traits": 1})
        if "name" in document
    }


def persist(collection: Collection, comps: List[Comp]) -> None:
    if not comps:
        logger.warning("Found 0 comps, leaving the existing collection untouched.")
        return

    logger.info("Found %s comps", len(comps))

    for comp in comps:
        champions_line = ", ".join([c.name for c in comp.champions])
        logger.info(
            "Tier: %s | Name: %s | Champions: %s",
            comp.tier,
            comp.name,
            champions_line,
        )

        for recommendation in comp.item_recommendations:
            if not recommendation.items:
                continue
            item_names = ", ".join(item.name for item in recommendation.items)
            logger.info("  %s: %s", recommendation.champion, item_names)

    replace_collection(collection, [comp.model_dump() for comp in comps])
    logger.info("Saved latest ranking to db successfully!")


def scrape_and_persist(
    collection: Collection, champions_collection: Optional[Collection] = None
):
    traits_lookup = (
        load_traits_lookup(champions_collection)
        if champions_collection is not None
        else None
    )
    if traits_lookup is not None:
        logger.info(
            "Loaded traits for %s champions from the champions collection",
            len(traits_lookup),
        )
    persist(collection, scrape_comps(traits_lookup=traits_lookup))


if __name__ == "__main__":
    configure_logging()
    logger.info("Scraping Comps 🕷️")
    db = DB().connect()
    try:
        scrape_and_persist(db.get_comps_collection(), db.get_champions_collection())
    finally:
        db.disconnect()
