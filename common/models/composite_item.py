from typing import List
from pydantic import BaseModel

from common.models import Item


class CompositeItem(BaseModel):
    name: str
    image: str
    components: List[Item] = []
