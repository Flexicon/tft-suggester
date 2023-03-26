from typing import List

from bs4 import BeautifulSoup, Tag
from pymongo.collection import Collection

from common.models import CompositeItem, Item
from common.db import DB
from .helpers import ScraperWebDriver

ScrapeURL = r"https://www.mobafire.com/teamfight-tactics/items-cheatsheet"
Selector = ".mobile-items .item"

NameReplacements = {
    "A D M I N": "A.D.M.I.N.",
    "Zzrot": "Zz'Rot",
}
NameApostrophes = [
    "Archangels",
    "Bulwarks",
    "Deaths",
    "Dragons",
    "Giants",
    "Guinsoos",
    "Protectors",
    "Rabadons",
    "Randuins",
    "Rascals",
    "Runaans",
    "Tacticians",
    "Thiefs",
    "Titans",
    "Warmogs",
    "Zekes",
]


def scrape_items() -> List[CompositeItem]:
    with ScraperWebDriver() as driver:
        html = driver.fetch_content_html(ScrapeURL, selector="#content")
        items = BeautifulSoup(html, "html.parser").select(Selector)
        return list(map(_build_composite_item, items))


def _build_composite_item(div: Tag) -> CompositeItem:
    image = div.find(class_="final")["src"]

    return CompositeItem(
        name=_name_from_image_url(image),
        image=image,
        components=[
            _build_item_from_component(c) for c in div.find_all(class_="component")
        ],
    )


def _build_item_from_component(img: Tag) -> Item:
    url = img["src"]
    return Item(name=_name_from_image_url(url), image=url)


def _name_from_image_url(url: str) -> str:
    name = url.split("/")[-1].split(".")[0].replace("-", " ").title()

    for k, v in NameReplacements.items():
        name = name.replace(k, v)

    for v in NameApostrophes:
        name = name.replace(v, v[:-1] + "'s")

    return name


def scrape_and_persist(collection: Collection):
    result = scrape_items()
    if not result:
        print("Found 0 items, exiting.")
        return

    print(
        "Found {count} items\n{separator}\n".format(
            count=len(result), separator="-" * 15
        )
    )

    for item in result:
        print(f"Name: {item.name}\nImage: {item.image}\nComponents:")
        print(
            "\n".join(
                [f"\t- Name: {c.name}\n\t  Image: {c.image}" for c in item.components]
            )
        )
        print("\n")

    collection.drop()
    collection.insert_many([item.dict() for item in result])
    print("Saved latest items to db successfully!")


if __name__ == "__main__":
    db = DB().connect()
    scrape_and_persist(db.get_items_collection())
    db.disconnect()
