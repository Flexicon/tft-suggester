from typing import List

from bs4 import BeautifulSoup
from bs4.element import Tag

from common.models import Comp, Champion
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
    characters = team.select('.team-characters > .characters-item')
    champions = list(map(_build_champion_from_character, characters))
    return Comp(name, champions)


def _build_champion_from_character(character: Tag) -> Champion:
    name = character['href'].split('/').pop().replace('_', ' ').title()
    icon = character.find('img')['src']
    return Champion(name, icon)


if __name__ == '__main__':
    result = scrape_comps()
    for comp in result:
        championsLine = ', '.join([champion.name for champion in comp.champions])
        print(f'Name: {comp.name}\nChampions: {championsLine}\n')
