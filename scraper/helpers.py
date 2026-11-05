import os
import re
from typing import cast

import requests
from bs4 import BeautifulSoup
from bs4.element import Tag

from common.models import Champion
from scraper.constants import TFTBaseURL

# Labels used by tftactics.gg for ability descriptions. Every other section on a
# champion page (e.g. Origin, Class) describes a trait.
NON_TRAIT_SECTION_LABELS = {"active", "passive"}
TRAIT_ICON_CLASS = "misc-image"

traits_cache = {}


def clear_traits_cache() -> None:
    """Clear the in-process traits cache. Intended for tests and long-lived processes."""
    traits_cache.clear()


def build_champion_from_character(character: Tag) -> Champion:
    traits = _scrape_traits_for_character(character)
    img_tag = require_tag(character, "img")
    name = str(img_tag["alt"])
    icon = str(img_tag["src"])
    cost = _price_from_character_class(" ".join(character["class"]))

    return Champion(name=name, image=icon, cost=cost, traits=traits)


def _scrape_traits_for_character(character: Tag) -> list[str]:
    href = str(character["href"])
    url = f"{TFTBaseURL}{href}" if href.startswith("/") else href

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
    soup = BeautifulSoup(html, "html.parser")

    # Trait sections carry an icon; ability descriptions carry no `misc-image`.
    trait_blocks = [
        block
        for block in soup.select(".character-ability")
        if block.find("img", class_=TRAIT_ICON_CLASS)
        and _section_label(block) not in NON_TRAIT_SECTION_LABELS
    ]
    if trait_blocks:
        return [require_tag(block, "h2").get_text(strip=True) for block in trait_blocks]

    # Fallback for pages that do not render trait icons.
    return _extract_traits_by_label(soup)


def _section_label(block: Tag) -> str:
    label_tag = block.select_one(".ability-description-name h4")
    return label_tag.get_text(strip=True).lower() if label_tag else ""


def _extract_traits_by_label(soup: BeautifulSoup) -> list[str]:
    return [
        require_tag(tag, "h2").get_text(strip=True)
        for tag in soup.select(".ability-description-name")
        if require_tag(tag, "h4").get_text(strip=True).lower()
        not in NON_TRAIT_SECTION_LABELS
    ]


def _price_from_character_class(classes: str) -> int:
    pattern = re.compile(r"\bc(\d+)\b")
    matches = pattern.findall(classes)
    return int(matches[0]) if matches else 0


def require_tag(tag: Tag, tag_name: str) -> Tag:
    """Find the first child tag with the given name. Raises ValueError if not found."""
    if not (found := tag.find(tag_name)):
        raise ValueError(f"Tag '{tag_name}' not found")
    return cast(Tag, found)


def require_tag_by_class(tag: Tag, class_name: str) -> Tag:
    """Find the first child tag with the given class name. Raises ValueError if not found."""
    if not (found := tag.find(class_=class_name)):
        raise ValueError(f"Tag with class '{class_name}' not found")
    return cast(Tag, found)


def trigger_webhook_if_set():
    data_fetched_webhook = os.getenv("DATA_FETCHED_WEBHOOK")
    if not data_fetched_webhook:
        return

    response = requests.post(data_fetched_webhook)
    response.raise_for_status()

    print("Webhook triggered")
