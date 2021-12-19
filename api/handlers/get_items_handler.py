from typing import List

from cdragon.items import Item, get_items


def handler() -> List[Item]:
    return get_items()
