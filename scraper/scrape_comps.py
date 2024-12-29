from typing import List, Optional

from bs4 import BeautifulSoup
from bs4.element import Tag
from pymongo.collection import Collection

from common.models import Champion, Comp, Item, ItemRecommendation
from common.db import DB
from .helpers import ScraperWebDriver, _build_champion_from_character

TFTCompsURL = r"https://tftactics.gg/tierlist/team-comps"


def scrape_comps() -> List[Comp]:
    with ScraperWebDriver() as driver:
        html = driver.fetch_content_html(TFTCompsURL)
        teams = BeautifulSoup(html, "html.parser").find_all(
            "div", class_="team-portrait"
        )
        comps = list(map(_build_comp_from_team, teams))
    return comps


def _build_comp_from_team(driver: ScraperWebDriver, team: Tag) -> Comp:
    playstyle = team.find_next(class_="team-playstyle").get_text()
    name = team.find_next(class_="team-name-elipsis").get_text().replace(playstyle, "")

    tier = team.find_next(class_="team-rank").get_text()
    characters = team.select(".team-characters > .characters-item")
    champions = [_build_champion_from_character(driver, c) for c in characters]
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
    img_tag = tag.find("img")
    name = img_tag["alt"]
    icon = img_tag["src"]
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
