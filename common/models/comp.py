from typing import List

from common.models import Champion


from pydantic import BaseModel


class Comp(BaseModel):
    name: str
    champions: List[Champion] = None
    tier: str = None
    playstyle: str = None
