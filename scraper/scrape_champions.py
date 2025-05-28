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


def scrape_and_persist(collection: Collection):
    result = scrape_champions()
    print(f'Found {len(result)} champions\n{"-" * 15}\n')

    for champion in result:
        print(
            f"Name: {champion.name}\nImage: {champion.image}\nCost: {champion.cost}\nTraits: {champion.traits}\n"
        )

    collection.drop()
    collection.insert_many([comp.dict() for comp in result])
    print("Saved latest champions to db successfully!")


if __name__ == "__main__":
    print("Scraping Champions 🕷️")
    db = DB().connect()
    scrape_and_persist(db.get_champions_collection())
    db.disconnect()
