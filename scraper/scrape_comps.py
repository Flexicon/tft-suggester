from typing import List

from bs4 import BeautifulSoup
from bs4.element import Tag

from common.models import Comp, Champion
from common.db import connect_comps_collection
from .helpers import _prepare_driver

TFTCompsURL = r'https://tftactics.gg/tierlist/team-comps'


def scrape_comps() -> List[Comp]:
    driver = _prepare_driver()
    driver.get(TFTCompsURL)
    html = driver.find_element_by_class_name('main').get_attribute('innerHTML')
    teams = BeautifulSoup(html, 'html.parser').find_all('div', class_='team-portrait')
    comps = list(map(_build_comp_from_team, teams))
    driver.close()
    return comps


def _build_comp_from_team(team: Tag) -> Comp:
    name = team.find_next(class_='team-name-elipsis').get_text()
    tier = team.find_next(class_='team-rank').get_text()
    characters = team.select('.team-characters > .characters-item')
    champions = list(map(_build_champion_from_character, characters))
    return Comp(name, champions, tier)


def _build_champion_from_character(character: Tag) -> Champion:
    name = character['href'].split('/').pop().replace('_', ' ').title()
    icon = character.find('img')['src']
    return Champion(name, icon)


def _scrape_and_persist():
    comps_collection = connect_comps_collection()
    result = scrape_comps()
    print('Found {count} comps\n{separator}\n'.format(count=len(result), separator="-" * 15))

    for comp in result:
        champions_line = ', '.join([champion.name for champion in comp.champions])
        print(f'Tier: {comp.tier}\nName: {comp.name}\nChampions: {champions_line}\n')

    comps_collection.drop()
    comps_collection.insert_many([comp.to_dict() for comp in result])
    print('Saved latest ranking to db successfully!')


if __name__ == '__main__':
    _scrape_and_persist()
