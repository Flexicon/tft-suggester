from typing import List

from bs4 import BeautifulSoup
from bs4.element import Tag
from pymongo.collection import Collection

from common.models import Comp
from common.db import DB
from .helpers import ScraperWebDriver, _build_champion_from_character

TFTCompsURL = r'https://tftactics.gg/tierlist/team-comps'


def scrape_comps() -> List[Comp]:
    with ScraperWebDriver() as driver:
        html = driver.fetch_content_html(TFTCompsURL)
        teams = BeautifulSoup(html, 'html.parser').find_all('div', class_='team-portrait')
        comps = list(map(_build_comp_from_team, teams))
        return comps


def _build_comp_from_team(team: Tag) -> Comp:
    name = team.find_next(class_='team-name-elipsis').get_text()
    tier = team.find_next(class_='team-rank').get_text()
    characters = team.select('.team-characters > .characters-item')
    champions = list(map(_build_champion_from_character, characters))
    return Comp(name, champions, tier)


def _scrape_and_persist(collection: Collection):
    result = scrape_comps()
    print('Found {count} comps\n{separator}\n'.format(count=len(result), separator="-" * 15))

    for comp in result:
        champions_line = ', '.join([champion.name for champion in comp.champions])
        print(f'Tier: {comp.tier}\nName: {comp.name}\nChampions: {champions_line}\n')

    collection.drop()
    collection.insert_many([comp.dict() for comp in result])
    print('Saved latest ranking to db successfully!')


if __name__ == '__main__':
    _scrape_and_persist(DB.get_instance().get_comps_collection())
