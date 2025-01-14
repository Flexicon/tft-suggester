import os
import re

import requests
from bs4 import BeautifulSoup
from bs4.element import Tag

from common.models import Champion

traits_cache = {}


def _build_champion_from_character(character: Tag) -> Champion:
    traits = _scrape_traits_for_character(character)
    img_tag = character.find("img")
    name = img_tag["alt"]
    icon = img_tag["src"]
    cost = _price_from_character_class(" ".join(character["class"]))
    return Champion(name=name, image=icon, cost=cost, traits=traits)


def _scrape_traits_for_character(character: Tag) -> list[str]:
    href = character["href"]
    url = f"https://tftactics.gg{href}" if href.startswith("/") else href

    if url in traits_cache:
        print(f"Using cached traits for: {url}")
        return traits_cache[url]

    print(f"Fetching champion traits from: {url}")
    response = requests.get(url)
    if response.status_code != 200:
        print(f"Failed to fetch champion traits from: {url}")
        return []

    html = response.text
    traits = traits_cache[url] = _extract_traits_from_character_html(html)
    return traits


def _extract_traits_from_character_html(html: str) -> list[str]:
    selector = ".ability-description-name"
    ability_tags = BeautifulSoup(html, "html.parser").select(selector)
    return [
        tag.find("h2").get_text()
        for tag in ability_tags
        if tag.find("h4").get_text().lower() not in ["active", "passive"]
    ]


def _price_from_character_class(classes: str) -> int:
    pattern = re.compile(r"\bc(\d+)\b")
    matches = pattern.findall(classes)
    return int(matches[0]) if matches else 0


def _trigger_webhook_if_set():
    data_fetched_webhook = os.getenv("DATA_FETCHED_WEBHOOK")
    if not data_fetched_webhook:
        return

    response = requests.post(data_fetched_webhook)
    response.raise_for_status()

    print("Webhook triggered")
