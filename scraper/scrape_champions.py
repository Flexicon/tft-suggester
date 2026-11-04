import requests

from typing import List

from bs4 import BeautifulSoup
from pymongo.collection import Collection

from common.models import Champion
from common.db import DB
from scraper.constants import TFTBaseURL
from scraper.helpers import build_champion_from_character

TFTChampionsURL = f"{TFTBaseURL}/champions/"
ChampionsSelector = ".characters-list > .characters-item"


def scrape_champions() -> List[Champion]:
    print(f"Fetching champions from: {TFTChampionsURL}")
    res = requests.get(TFTChampionsURL)
    res.raise_for_status()

    characters = BeautifulSoup(res.text, "html.parser").select(ChampionsSelector)
    champions = [build_champion_from_character(c) for c in characters]
    return champions


def persist(collection: Collection, champions: List[Champion]) -> None:
    if not champions:
        print("Found 0 champions, leaving the existing collection untouched.")
        return

    print(f'Found {len(champions)} champions\n{"-" * 15}\n')

    for champion in champions:
        print(
            f"Name: {champion.name}\nImage: {champion.image}\nCost: {champion.cost}\nTraits: {champion.traits}\n"
        )

    collection.drop()
    collection.insert_many([champion.model_dump() for champion in champions])
    print("Saved latest champions to db successfully!")


def scrape_and_persist(collection: Collection):
    persist(collection, scrape_champions())


if __name__ == "__main__":
    print("Scraping Champions 🕷️")
    db = DB().connect()
    scrape_and_persist(db.get_champions_collection())
    db.disconnect()
