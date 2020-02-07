from typing import List

from common.models import Champion


class Comp:
    def __init__(self, name: str, champions: List[Champion] = None):
        self.name = name
        self.champions = champions if champions is not None else []
