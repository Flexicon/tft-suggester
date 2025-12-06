from typing import List

from pymongo.collection import Collection

from common.models import CompositeItem
from common.db import DB
from cdragon.items import get_composite_items


def scrape_items() -> List[CompositeItem]:
    """Fetch composite TFT items from Community Dragon API.

    Returns a list of CompositeItem objects with their components.
    Names are already properly formatted from the official data source.
    """
    print("Fetching items from Community Dragon API...")
    return get_composite_items()


def scrape_and_persist(collection: Collection):
    result = scrape_items()
    if not result:
        print("Found 0 items, exiting.")
        return

    print(
        "Found {count} items\n{separator}\n".format(
            count=len(result), separator="-" * 15
        )
    )

    for item in result:
        print(f"Name: {item.name}\nImage: {item.image}\nComponents:")
        print(
            "\n".join(
                [f"\t- Name: {c.name}\n\t  Image: {c.image}" for c in item.components]
            )
        )
        print("\n")

    collection.drop()
    collection.insert_many([item.dict() for item in result])
    print("Saved latest items to db successfully!")


if __name__ == "__main__":
    print("Scraping Items 🕷️")
    db = DB().connect()
    scrape_and_persist(db.get_items_collection())
    db.disconnect()
