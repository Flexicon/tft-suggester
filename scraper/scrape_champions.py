from typing import List

from bs4 import BeautifulSoup
from pymongo.collection import Collection

from common.models import Champion
from common.db import DB
from .helpers import ScraperWebDriver, _build_champion_from_character

TFTChampionsURL = r'https://tftactics.gg/tierlist/champions'


def scrape_champions() -> List[Champion]:
    with ScraperWebDriver() as driver:
        html = driver.fetch_content_html(TFTChampionsURL)
        characters = BeautifulSoup(html, 'html.parser').select('.characters-list > .characters-item')
        champions = [_build_champion_from_character(driver, c) for c in characters]
    return champions


def scrape_and_persist(collection: Collection):
    result = scrape_champions()
    print('Found {count} champions\n{separator}\n'.format(count=len(result), separator="-" * 15))

    for champion in result:
        print(f'Name: {champion.name}\nImage: {champion.image}\nCost: {champion.cost}\nTraits: {champion.traits}\n')

    collection.drop()
    collection.insert_many([comp.dict() for comp in result])
    print('Saved latest champions to db successfully!')


if __name__ == '__main__':
    print("Scraping Champions 🕷️")
    db = DB().connect()
    scrape_and_persist(db.get_champions_collection())
    db.disconnect()
