import requests

from typing import List

from bs4 import BeautifulSoup
from bs4.element import Tag
from pymongo.collection import Collection

from common.models import Champion, Comp, Item, ItemRecommendation
from common.db import DB
from .helpers import build_champion_from_character, require_tag, require_tag_by_class

TFTCompsURL = r"https://tftactics.gg/tierlist/team-comps"


def scrape_comps() -> List[Comp]:
    print(f"Fetching comps from: {TFTCompsURL}")
    res = requests.get(TFTCompsURL)
    res.raise_for_status()

    teams = BeautifulSoup(res.text, "html.parser").find_all(
        "div", class_="team-portrait"
    )
    return [_build_comp_from_team(t) for t in teams]


def _build_comp_from_team(team: Tag) -> Comp:
    playstyle = require_tag_by_class(team, "team-playstyle").get_text(strip=True)
    tier = require_tag_by_class(team, "team-rank").get_text(strip=True)
    name = (
        require_tag_by_class(team, "team-name-elipsis")
        .get_text(strip=True)
        .replace(playstyle, "")
    )

    characters = team.select(".team-characters > .characters-item")
    champions = [build_champion_from_character(c) for c in characters]
    items = list(map(_build_item_recommendation, characters, champions))

    return Comp(
        name=name,
        champions=champions,
        tier=tier,
        playstyle=playstyle,
        item_recommendations=items,
    )


def _build_item_recommendation(
    character: Tag, champion: Champion
) -> ItemRecommendation:
    item_tags = character.find_all(class_="characters-item")
    items = [_build_item(t) for t in item_tags]
    return ItemRecommendation(champion=champion.name, items=items)


def _build_item(tag: Tag) -> Item:
    img_tag = require_tag(tag, "img")
    name = str(img_tag["alt"])
    icon = str(img_tag["src"])

    return Item(name=name, image=icon)


def scrape_and_persist(collection: Collection):
    result = scrape_comps()
    print(f"Found {len(result)} comps\n{'-' * 15}\n")

    for comp in result:
        champions_line = ", ".join([c.name for c in comp.champions])
        print(f"Tier: {comp.tier}\nName: {comp.name}\nChampions: {champions_line}")
        print("Recommendations:")

        for recommendation in comp.item_recommendations:
            if not recommendation.items:
                continue
            print(f"\tFor {recommendation.champion}:")
            print("\n".join([f"\t\t- {i.name}" for i in recommendation.items]))

        print("\n")

    collection.drop()
    collection.insert_many([comp.dict() for comp in result])
    print("Saved latest ranking to db successfully!")


if __name__ == "__main__":
    print("Scraping Comps 🕷️")
    db = DB().connect()
    scrape_and_persist(db.get_comps_collection())
    db.disconnect()
