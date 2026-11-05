import logging
from typing import List

from bs4 import BeautifulSoup
from pymongo.collection import Collection

from common.models import Champion
from common.db import DB, replace_collection
from scraper.constants import TFTBaseURL
from scraper.helpers import build_champion_from_character
from scraper.http_client import get
from scraper.logging_utils import configure_logging

logger = logging.getLogger(__name__)

TFTChampionsURL = f"{TFTBaseURL}/champions/"
ChampionsSelector = ".characters-list > .characters-item"


def scrape_champions() -> List[Champion]:
    logger.info("Fetching champions from: %s", TFTChampionsURL)
    res = get(TFTChampionsURL)
    res.raise_for_status()

    characters = BeautifulSoup(res.text, "html.parser").select(ChampionsSelector)
    champions = [build_champion_from_character(c) for c in characters]
    return champions


def persist(collection: Collection, champions: List[Champion]) -> None:
    if not champions:
        logger.warning("Found 0 champions, leaving the existing collection untouched.")
        return

    logger.info("Found %s champions", len(champions))

    for champion in champions:
        logger.info(
            "Name: %s | Image: %s | Cost: %s | Traits: %s",
            champion.name,
            champion.image,
            champion.cost,
            champion.traits,
        )

    replace_collection(collection, [champion.model_dump() for champion in champions])
    logger.info("Saved latest champions to db successfully!")


def scrape_and_persist(collection: Collection):
    persist(collection, scrape_champions())


if __name__ == "__main__":
    configure_logging()
    logger.info("Scraping Champions 🕷️")
    db = DB().connect()
    try:
        scrape_and_persist(db.get_champions_collection())
    finally:
        db.disconnect()
