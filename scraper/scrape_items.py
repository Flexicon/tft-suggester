import logging
from typing import List

from pymongo.collection import Collection

from common.models import CompositeItem
from common.db import DB, replace_collection
from cdragon.items import get_composite_items
from scraper.logging_utils import configure_logging

logger = logging.getLogger(__name__)


def scrape_items() -> List[CompositeItem]:
    """Fetch composite TFT items from Community Dragon API.

    Returns a list of CompositeItem objects with their components.
    Names are already properly formatted from the official data source.
    """
    logger.info("Fetching items from Community Dragon API...")
    return get_composite_items()


def persist(collection: Collection, items: List[CompositeItem]) -> None:
    if not items:
        logger.warning("Found 0 items, leaving the existing collection untouched.")
        return

    logger.info("Found %s items", len(items))

    for item in items:
        components = ", ".join(component.name for component in item.components)
        logger.info(
            "Name: %s | Image: %s | Components: %s",
            item.name,
            item.image,
            components,
        )

    replace_collection(collection, [item.model_dump() for item in items])
    logger.info("Saved latest items to db successfully!")


def scrape_and_persist(collection: Collection):
    persist(collection, scrape_items())


if __name__ == "__main__":
    configure_logging()
    logger.info("Scraping Items 🕷️")
    db = DB().connect()
    try:
        scrape_and_persist(db.get_items_collection())
    finally:
        db.disconnect()
